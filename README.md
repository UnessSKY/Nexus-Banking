# Nexus-Banking

A secure, feature-rich Flask web application for managing bank accounts with user authentication, balance tracking, and transaction history.

## 🚀 Features

- **User Authentication**: Secure registration and login with 4-digit PIN-based authentication
- **Account Management**: Create and manage your bank account with balance tracking
- **Transaction Management**: Record and view deposits, withdrawals, and transfers with full history
- **Dashboard**: View account balance, recent transactions, and spending analytics
- **Responsive Design**: User-friendly interface that works on desktop and mobile devices
- **Secure Sessions**: Flask session management with secure user authentication
- **Transaction Validation**: Prevent overdrafts with real-time balance checking
- **Database Persistence**: SQLite database for reliable data storage

## 📋 Project Structure

```
banking_system/
├── app/
│   ├── __init__.py              # Flask app initialization with all routes
│   ├── database.py              # Database setup and functions
│   ├── static/                  # CSS, JS, and static assets
│   │   └── style.css
│   └── templates/               # HTML templates
│       ├── base.html            # Base template
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── transaction.html
│       ├── add_transaction.html
│       └── update_balance.html
├── tests/
│   └── test.py                  # Testing utilities
├── bank.db                      # SQLite database (auto-created)
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd banking_system
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app/__init__.py
   ```
   
   The app will be available at `http://localhost:5000`

## 🔐 Authentication

### Default Test User
- **Email**: test@example.com
- **PIN**: 1234
- **Balance**: $1,000.00

### Creating a New Account
1. Click "Register" on the login page
2. Enter your name, email, and 4-digit PIN
3. Confirm your PIN
4. Set your initial balance
5. Click "Register" to create your account

## 💰 Transaction Types

- **Deposit**: Add funds to your account
- **Withdrawal**: Remove funds from your account
- **Transfer**: Send money to another user (with recipient name)
- **Adjustment**: Manual balance updates

## 🗄️ Database Schema

### Users Table
```sql
- id: Primary key
- name: User's full name
- email: Unique email address
- pin_hash: Hashed 4-digit PIN
- created_at: Account creation timestamp
```

### Accounts Table
```sql
- id: Primary key
- user_id: Foreign key to users
- balance: Current account balance
```

### Transactions Table
```sql
- id: Primary key
- account_id: Foreign key to accounts
- amount: Transaction amount
- transaction_type: deposit/withdrawal/transfer/adjustment
- location_type: Optional location of transaction
- description: Transaction details
- old_balance: Balance before transaction
- new_balance: Balance after transaction
- transaction_date: Timestamp of transaction
```

## 🔒 Security Features

- **PIN Hashing**: PINs are hashed using Werkzeug security utilities
- **Session Management**: Secure Flask sessions for user authentication
- **SQL Injection Prevention**: Parameterized queries throughout
- **Input Validation**: All user inputs are validated before processing
- **Transaction Integrity**: Database transactions ensure consistency

## 📝 Usage Examples

### Login
```
1. Navigate to http://localhost:5000
2. Enter your email and 4-digit PIN
3. Click "Login"
```

### Create a Transaction
```
1. Click "Add Transaction" from the dashboard
2. Enter amount (negative for withdrawal, positive for deposit)
3. Add a description
4. Optionally enter recipient name for transfers
5. Click "Submit"
```

### Update Balance
```
1. Click "Update Balance" from the dashboard
2. Enter the new balance amount
3. Click "Update"
4. A manual adjustment transaction will be recorded
```

## 🧪 Testing

Run the test file to verify the database setup:
```bash
python tests/test.py
```

This will display all users, accounts, and transactions in the database.

## 📚 Technologies Used

- **Flask**: Web framework for Python
- **SQLite**: Lightweight database
- **Werkzeug**: Security utilities for password hashing
- **HTML/CSS**: Frontend interface
- **Jinja2**: Template engine

## 🐛 Troubleshooting

### Port 5000 Already in Use
```bash
# Use a different port
python -c "from app import app; app.run(port=5001)"
```

### Database Not Found
The `bank.db` file is automatically created on first run.

### Module Not Found Errors
Ensure you've activated your virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Created as a Flask banking system learning project.

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

---

**Note**: This is a demo application for educational purposes. Do not use in production without additional security measures.
