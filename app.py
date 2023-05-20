from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from numpy import array
from numpy import random,int64
from pandas import DataFrame,to_timedelta

app = Flask(__name__)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # MySQL configuration
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mercede$!970",
        database="bank"
    )

    cur=mydb.cursor()
    if request.method == 'POST':
        # Get the form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_no = request.form['phone']
        house_no = request.form['house_no']
        street_no = request.form['street_no']
        area = request.form['area']
        city = request.form['city']
        country = request.form['country']

        
        
        
        cur.execute("SELECT email FROM bank.customers")
        record=cur.fetchall()
        record = array(record)
        
        if email in record:
            # return redirect('signup')
            return render_template("signup.html",error="Email already exists.")
        else:
            cur.execute("SELECT account_no FROM bank.bank_accounts")
            account_numbers=cur.fetchall()
            account_numbers=array(account_numbers)
            new_account_no=int64(random.randint(low=1000000000,high=9999999999,dtype=int64))
            while new_account_no in account_numbers:
                new_account_no=random.randint(low=1000000000,high=9999999999)
            cur.execute("INSERT INTO bank.customers (first_name, last_name, email, phone_no, house_no, street_no, area, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (first_name, last_name, email, phone_no, house_no, street_no, area, city, country))
            cur.execute("SELECT customer_id FROM bank.customers WHERE email=%s",(email,))
            customer_id=cur.fetchone()
            
            cur.execute("INSERT INTO bank.bank_accounts (customer_id,account_no,pin,account_balance) VALUES (%s,%s,%s,%s)", (customer_id[0],"PK-"+str(new_account_no),1111,0))
            mydb.commit()
            
        cur.close()
        
        
        
    
    # Render the signup form
    return render_template("signup.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mercede$!970",
        database="bank"
    )
    
    cur=mydb.cursor()
    
    if request.method == 'POST':
        # Get the form data
        account_no = request.form['account_no']
        
        pin = request.form['pin']

        #tally form data from the database
        cur.execute("SELECT account_no,pin FROM bank.bank_accounts WHERE account_no=%s and pin=%s",(account_no,pin))
        record=cur.fetchone()
        cur.close()
        mydb.close()
        if record is None:
            return render_template("login.html",error="Invalid ID or Password") #need to make error page.
        else:
            # Redirect the user to the account page
            return redirect(url_for('post_login', account_no=account_no))

    # If the request method is GET, render the login page
    return render_template('login.html',error="")






@app.route('/post_login')
def post_login():
       # Connect to database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mercede$!970",
        database="bank"
    )
    # Create cursor
    cursor = mydb.cursor()
    account_no = request.args.get('account_no')
    
    # Execute SELECT statement to retrieve balance amount for given account number
    cursor.execute("SELECT account_balance FROM bank_accounts WHERE account_no=%s", (account_no,))
    # Fetch balance amount from result
    result = cursor.fetchone()
    balance = result[0]
    # Close cursor and database connection
    cursor.close()
    mydb.close()
   
    
    return render_template('post_login.html',balance=balance, account_no=account_no)


@app.route('/transfer',methods=['GET','POST'])
def transfer():
    account_no = request.args.get('account_no')
    #print(account_no)
    if request.method=='POST':
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mercede$!970",
        database="bank"
        )
    
        cursor = mydb.cursor()
        
        target_account=request.form.get('target_account')
        cursor.execute("select account_no from bank_accounts where account_no=%s",(target_account,))
        target_account=cursor.fetchone()
        if target_account is None:
            return render_template("transfer.html",error="Account not found",account_no=account_no)
        else:
            target_account=target_account[0]
            amount=request.form.get('amount')
            cursor.execute("select account_balance from bank_accounts where account_no=%s",(account_no,))
            #print(f'acc={account_no}')
            balance=(cursor.fetchone())[0]
            if float(amount)>float(balance):
                return render_template("transfer.html",error="Insufficient Funds",account_no=account_no)
            else:
                cursor.execute("select account_balance from bank_accounts where account_no=%s",(target_account,))
                target_balance=(cursor.fetchone())[0]
                cursor.execute("UPDATE bank_accounts SET account_balance = %s - %s WHERE account_no = %s;", (balance, amount, account_no))
                cursor.execute("UPDATE bank_accounts SET account_balance = %s + %s WHERE account_no=%s;",(target_balance,amount,target_account))
                cursor.execute("INSERT INTO bank.transactions(account_no,target_account,amount,nature) VALUES(%s,%s,%s,%s)",(account_no,target_account,amount,"transfer"))
                mydb.commit()
        cursor.close()
        mydb.close()
    return render_template('transfer.html',error="",account_no=account_no)
            




@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    account_no=request.args.get('account_no')
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        if amount:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mercede$!970",
                database="bank"
            )
            cursor = mydb.cursor()
            cursor.execute("SELECT account_balance FROM bank_accounts WHERE account_no = %s", (account_no,))
            result = cursor.fetchone()
            balance = result[0]
            cursor.execute("UPDATE bank_accounts SET account_balance = %s + %s WHERE account_no = %s;", (balance, amount, account_no))
            cursor.execute("INSERT INTO bank.transactions(account_no,amount,nature) VALUES(%s,%s,%s)",(account_no,amount,"deposit"))
            mydb.commit()
            cursor.close()
            mydb.close()
    return render_template('deposit.html', account_no=account_no)


@app.route('/withdrawal',methods=['GET', 'POST'])
def withdrawal():
    account_no=request.args.get('account_no')
    print(account_no)
    if request.method == 'POST':
        amount = request.form.get('amount')
        if amount:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mercede$!970",
                database="bank"
            )
            cursor = mydb.cursor()
            cursor.execute("SELECT account_balance FROM bank_accounts WHERE account_no = %s", (account_no,))
            result = cursor.fetchone()
            balance = result[0]
            if float(amount)>float(balance):
                return render_template("withdrawal.html",error="Insufficient Funds",account_no=account_no)
            else:
            
                cursor.execute("UPDATE bank_accounts SET account_balance = %s - %s WHERE account_no = %s;", (balance, amount, account_no))
                cursor.execute("INSERT INTO bank.transactions(account_no,amount,nature) VALUES(%s,%s,%s)",(account_no,amount,"withdrawal"))
                mydb.commit()
            cursor.close()
            mydb.close()
    return render_template('withdrawal.html',account_no=account_no,error="")


@app.route('/details')
def details():
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mercede$!970",
                database="bank")
    account_no=request.args.get("account_no")       
    cursor = mydb.cursor()
    cursor.execute("select account_no,target_account,amount,nature,date_of_transaction,time_format(time_of_transaction,'%r') as transaction_time from transactions where account_no=%s or target_account=%s order by date_of_transaction DESC,time_of_transaction DESC",(account_no,account_no)
    )
    df=DataFrame(cursor.fetchall())
    
    

    print(df)
    return render_template("details.html",account_no=account_no,df=df)

@app.route('/')
def dashboard():
    # Render the dashboard page 
    return render_template('dashboard.html')




if __name__ == '__main__':
    app.run(host='localhost', port=5000,debug=True)
