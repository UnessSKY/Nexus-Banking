import database
db = database.get_db_connection()

# Test users
print("Users:")
print(db.execute("SELECT * FROM users").fetchall())

# Test accounts
print("\nAccounts:")
print(db.execute("SELECT * FROM accounts").fetchall())

# Test transactions
print("\nTransactions:")
print(db.execute("SELECT * FROM transactions").fetchall())

db.close()
