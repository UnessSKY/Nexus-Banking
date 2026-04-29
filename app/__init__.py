from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from datetime import datetime
import os



app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Change this in production!

# Database Configuration
DATABASE = os.path.join(os.path.dirname(__file__), '..', 'bank.db')

def get_db():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                location_type TEXT,
                description TEXT,
                old_balance REAL NOT NULL,
                new_balance REAL NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            );
        ''')
        conn.commit()

# Initialize database before first request
init_db()

# Helper Functions
def login_required(f):
    """Decorator to ensure user is logged in"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_user(name, email, pin):
    """Create a new user with hashed PIN"""
    if not pin.isdigit() or len(pin) != 4:
        raise ValueError("PIN must be exactly 4 digits")
    
    pin_hash = generate_password_hash(pin)
    
    with get_db() as conn:
        try:
            # Start transaction
            conn.execute('BEGIN')
            
            # Create user
            cur = conn.execute(
                'INSERT INTO users (name, email, pin_hash) VALUES (?, ?, ?)',
                (name, email, pin_hash)
            )
            user_id = cur.lastrowid
            
            # Create account
            conn.execute(
                'INSERT INTO accounts (user_id, balance) VALUES (?, ?)',
                (user_id, 0.0)
            )
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'email' in str(e):
                raise ValueError("Email already exists")
            raise

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pin = request.form.get('pin', '').strip()
        
        # Validate inputs
        if not email or not pin:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('login'))
        
        if not pin.isdigit() or len(pin) != 4:
            flash('PIN must be exactly 4 digits', 'error')
            return redirect(url_for('login'))
        
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE email = ?', 
                (email,)
            ).fetchone()
            
            if not user or not check_password_hash(user['pin_hash'], pin):
                flash('Invalid email or PIN', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        pin = request.form.get('pin', '').strip()
        pin_confirm = request.form.get('pin_confirm', '').strip()
        initial_balance = request.form.get('initial_balance', '0').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email or '@' not in email:
            errors.append('Valid email is required')
        if not pin.isdigit() or len(pin) != 4:
            errors.append('PIN must be exactly 4 digits')
        if pin != pin_confirm:
            errors.append('PINs do not match')
        try:
            initial_balance = float(initial_balance)
            if initial_balance < 0:
                errors.append('Initial balance cannot be negative')
        except ValueError:
            errors.append('Invalid initial balance amount')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html',
                                name=name,
                                email=email,
                                initial_balance=initial_balance)
        
        try:
            # This line was fixed - now matches the function signature
            user_id = create_user(name, email, pin)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html',
                                name=name,
                                email=email,
                                initial_balance=initial_balance)
    
    return render_template('register.html')
@app.route('/dashboard')
@login_required
def dashboard():
    with get_db() as conn:
        # Get account info
        account = conn.execute(
            'SELECT * FROM accounts WHERE user_id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not account:  # Add this check to prevent errors
            flash('Account not found', 'error')
            return redirect(url_for('login'))
        
        # Get transactions
        transactions = conn.execute('''
            SELECT * FROM transactions 
            WHERE account_id = ?
            ORDER BY transaction_date DESC
            LIMIT 10
        ''', (account['id'],)).fetchall()
        
        # Get spending analytics
        spending_by_location = conn.execute('''
            SELECT location_type, SUM(amount) as total 
            FROM transactions 
            WHERE account_id = ? AND amount < 0
            GROUP BY location_type
        ''', (account['id'],)).fetchall()
        
        # Make sure all required variables are passed
        return render_template('dashboard.html',
                           user_name=session.get('user_name', 'User'),
                           current_balance=account['balance'],
                           transactions=transactions,
                           spending_by_location=spending_by_location)
@app.route('/transaction', methods=['GET', 'POST'])  # ← Accept BOTH methods
@login_required
def add_transaction():
    if request.method == 'POST':  # ← Handle form submission
        try:
            amount = float(request.form['amount'])
            description = request.form['description'].strip()
            recipient = request.form.get('recipient', '').strip()

            with get_db() as conn:
                # Start transaction
                conn.execute('BEGIN IMMEDIATE TRANSACTION')
                
                # Get current balance
                account = conn.execute(
                    '''SELECT a.balance, a.id 
                    FROM accounts a
                    WHERE a.user_id = ?''',
                    (session['user_id'],)
                ).fetchone()

                # Validate funds
                if amount < 0 and abs(amount) > account['balance']:
                    conn.rollback()
                    flash('❌ Insufficient funds!', 'error')
                    return redirect(url_for('add_transaction'))  # ← Return to form

                # Process transaction
                new_balance = account['balance'] + amount
                conn.execute('''
                    INSERT INTO transactions (
                        account_id, amount, transaction_type,
                        description, old_balance, new_balance
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    account['id'],
                    amount,
                    'transfer' if recipient else ('deposit' if amount >=0 else 'withdrawal'),
                    f"To: {recipient}" if recipient else description,
                    account['balance'],
                    new_balance
                ))

                # Update balance
                conn.execute(
                    'UPDATE accounts SET balance = ? WHERE id = ?',
                    (new_balance, account['id'])
                )
                conn.commit()

            flash('✅ Transaction successful!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('⚠️ Invalid amount format', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'⚠️ Transaction failed: {str(e)}', 'error')
    
    # GET request or failed POST → show form
    return render_template('transaction.html')  # ← Ensure this template exists
@app.route('/logout')
def logout():
    # Clear all session variables
    session.clear()
    flash('You have been successfully logged out', 'success')
    return redirect(url_for('login'))
@app.route('/update_balance', methods=['GET', 'POST'])
@login_required
def update_balance():
    with get_db() as conn:
        # Get current account info
        account = conn.execute(
            'SELECT * FROM accounts WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()
        
        if not account:
            flash('Account not found', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                new_balance = float(request.form['balance'])
                
                if new_balance < 0:
                    flash("Balance can't be negative", "error")
                    return render_template('update_balance.html',
                                        current_balance=account['balance'])
                
                # Start transaction
                conn.execute('BEGIN')
                
                # Record as adjustment transaction
                conn.execute('''
                    INSERT INTO transactions (
                        account_id, amount, transaction_type,
                        description, old_balance, new_balance
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    account['id'],
                    new_balance - account['balance'],  # Difference
                    'adjustment',
                    'Manual balance update',
                    account['balance'],
                    new_balance
                ))
                
                # Update account balance
                conn.execute(
                    'UPDATE accounts SET balance = ? WHERE id = ?',
                    (new_balance, account['id'])
                )
                
                conn.commit()
                flash('Balance updated successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except ValueError:
                conn.rollback()
                flash('Invalid amount entered', 'error')
            except Exception as e:
                conn.rollback()
                flash(f'Error updating balance: {str(e)}', 'error')
        
        return render_template('update_balance.html',
                            current_balance=account['balance'])
if __name__ == '__main__':
    app.run(debug=True)
