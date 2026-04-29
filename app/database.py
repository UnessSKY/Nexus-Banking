import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    """Initialize database tables"""
    with sqlite3.connect('bank.db') as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        pin_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        balance REAL NOT NULL DEFAULT 0.0,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
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
                        )''')
        
        # Add test user if none exists
        if not cursor.execute("SELECT 1 FROM users WHERE email='test@example.com'").fetchone():
            pin_hash = generate_password_hash("1234")
            cursor.execute(
                "INSERT INTO users (name, email, pin_hash) VALUES (?, ?, ?)",
                ("Test User", "test@example.com", pin_hash)
            )
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
                (user_id, 1000.0)
            )
            
            # Add test transactions
            test_transactions = [
                (user_id, -50.0, "purchase", "supermarket", "Groceries", 1000.0, 950.0),
                (user_id, -20.0, "purchase", "online", "Amazon", 950.0, 930.0),
                (user_id, 200.0, "deposit", None, "Paycheck", 930.0, 1130.0)
            ]
            
            for tx in test_transactions:
                cursor.execute('''INSERT INTO transactions 
                                (account_id, amount, transaction_type, location_type, 
                                description, old_balance, new_balance)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''', tx)
            
        conn.commit()
def create_user(name, email, pin, initial_balance=0.0):
    """Create a new user with account and initial balance"""
    if not pin.isdigit() or len(pin) != 4:
        raise ValueError("PIN must be exactly 4 digits")
    
    pin_hash = generate_password_hash(pin)
    
    with get_db() as conn:
        try:
            conn.execute('BEGIN')
            
            # Create user
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (name, email, pin_hash) VALUES (?, ?, ?)',
                (name, email, pin_hash)
            )
            user_id = cursor.lastrowid
            
            # Create account with initial balance
            cursor.execute(
                'INSERT INTO accounts (user_id, balance) VALUES (?, ?)',
                (user_id, float(initial_balance))
            )
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'email' in str(e):
                raise ValueError("Email already exists")
            raise
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Registration failed: {str(e)}")
def get_db():
    """Get database connection"""
    conn = sqlite3.connect('bank.db')
    conn.row_factory = sqlite3.Row
    return conn
