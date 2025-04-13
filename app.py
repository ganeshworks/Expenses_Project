from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('login'))  # ✅ this sends user to login page first

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
              session['loggedin'] = True
              session['username'] = user['username']
              session['user_id'] = user['id']  # <-- Add this line
        return redirect(url_for('dashboard'))
    else:
            flash('Invalid Username or Password', 'danger')

    return render_template('login.html')  # Always render login if GET or failed login

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))  # 🚫 redirect if not logged in
    


# @app.route('/transactions', methods=['GET', 'POST'])
# def transactions():
#     if 'user_id' not in session:
#         return redirect('/login')

#     cur = mysql.connection.cursor()

#     # Get user accounts for dropdown
#     cur.execute("SELECT account_name FROM accounts WHERE user_id = %s", (session['user_id'],))
#     accounts = cur.fetchall()

#     if request.method == 'POST':
#         t_type = request.form['type']
#         amount = request.form['amount']
#         purpose = request.form['purpose']
#         account = request.form['account']

#         cur.execute("""
#             INSERT INTO transactions (user_id, transaction_type, amount, purpose, account_name)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (session['user_id'], t_type, amount, purpose, account))

#         mysql.connection.commit()
#         flash('Transaction recorded successfully!', 'success')
#         return redirect('/transactions')

#     cur.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC", (session['user_id'],))
#     all_transactions = cur.fetchall()
#     cur.close()
#     return render_template('transactions.html', user=session['username'], transactions=all_transactions, accounts=accounts)

@app.route('/cash_in_cash_out', methods=['GET', 'POST'])
def cash_in_cash_out():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in
    
    # Retrieve user transactions from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT transaction_type, amount, purpose, transaction_date, transaction_time, account_name, transaction_number FROM transactions")
    data = cur.fetchall()

    transactions = []
    for row in data:
        txn = {
            'transaction_type': row[0],
            'amount': row[1],
            'purpose': row[2],
            'transaction_date': row[3],
            'transaction_time': row[4],
            'account_name': row[5],
            'transaction_number': row[6]
        }
        transactions.append(txn)  # Append each transaction to the list

    # Handle form submission for adding a transaction
    if request.method == 'POST':
        transaction_type = request.form['transaction_type']
        amount = request.form['amount']
        purpose = request.form['purpose']
        transaction_date = request.form['transaction_date']
        transaction_time = request.form['transaction_time']
        transaction_number = request.form.get('transaction_number')  # Optional
        account_name = request.form['account_name']

        # Insert the transaction into the database
        cur.execute("""
        INSERT INTO transactions (user_id, transaction_type, amount, purpose, transaction_date, transaction_time, transaction_number, account_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], transaction_type, amount, purpose, transaction_date, transaction_time, transaction_number, account_name))

        mysql.connection.commit()

        return redirect(url_for('cash_in_cash_out'))

    return render_template('cash_in_cash_out.html', transactions=transactions)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
