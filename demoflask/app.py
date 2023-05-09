import random
from flask import Flask, make_response, render_template ,request ,redirect ,url_for, session, Response, send_file, flash
from flask_mysqldb import MySQL
from flask_mysqldb import MySQL
import MySQLdb.cursors
import json
import mysql.connector
import re,os
import hashlib ,secrets ,stripe
import pandas as pd
from faker import Faker
from openpyxl.workbook import Workbook
from openpyxl import Workbook
from openpyxl.writer.excel import save_workbook
from io import BytesIO
import io
import base64
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail, Message

# stripe.api_key = 'sk_test_51MecXQSDtBJBmoILDf81I4a1WOUDvL4uZARTjE5HDBoejn0mhWr00VBSgDpVfwqAVqXRUQHzTDWlWWPtI6oiAADo00nYf3isY7'




app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aadi@9011'
# app.config['MYSQL_PASSWORD'] = 'Jeffrey@08'
app.config['MYSQL_DB'] = 'ecart'


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'team.personelexpensetracker@gmail.com'
app.config['MAIL_PASSWORD'] = 'uabvnvzwyngutqit'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# login_manager = LoginManager()
# login_manager.init_app(app)


mysql = MySQL(app)

# product = {
#     'name': 'Mycart',
#     'description': 'This is my product description.',
#     'amount': 1000, 
#     'currency': 'usd',
#     'quantity': 1,
# }

# # fake = Faker()
# # data = []
# # for i in range(10):
# #     data.append({
# #         'Title': fake.sentence(),
# #         'Description': fake.paragraph(),
# #         'Image': fake.image_url(),
# #         'Category': fake.word(),
# #         'Subcategory': fake.word(),
# #         'Brand': fake.company(),
# #         'Price': fake.pyfloat(left_digits=2, right_digits=2, positive=True),
# #         'OrgPrice': fake.pyfloat(left_digits=2, right_digits=2, positive=True),
# #         'Rating': fake.pyfloat(left_digits=1, right_digits=1, positive=True),
# #         'Stock': fake.pyint(min_value=0, max_value=100),
# #     })

# # # Create a Pandas DataFrame and write to Excel file
# # df = pd.DataFrame(data)
# # df.to_excel('products.xlsx', index=False)

@app.route('/no', methods=['GET', 'POST'])
def demo():
    
        

    return render_template('demo.html')

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="Aadi@9011",
#   database="ecart"
# )
def calculate_num_pages(num_items, items_per_page):
   return (num_items + items_per_page - 1) // items_per_page
@app.route('/add_products', methods=['POST'])
def add_products():
    user_data = inject_data()

    # Get the uploaded file
    uploaded_file = request.files['file']

    print(uploaded_file)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
   
    # Check the file extension and save the file
    if uploaded_file.filename.endswith('.csv'):
        file_format = 'csv'
    elif uploaded_file.filename.endswith('.xlsx'):
        file_format = 'xlsx'
    else:
        return 'Invalid file format. Please upload a CSV or XLSX file.'

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
    uploaded_file.save(file_path)

    # Read the data using pandas
    if file_format == 'csv':
        df = pd.read_csv(file_path)
    elif file_format == 'xlsx':
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        return 'Error reading the file.'

    # Remove rows with NaN values
    df = df.dropna(how='any')
    
    # Process each row of the data
    for index, row in df.iterrows():
        # Extract the values from the row
        title = row['Title']
        description = row['Description']
        image = row['Image']
        category = row['Category']
        subcategory = row['Subcategory']
        brand = row['Brand']
        price = row['Price']
        orgprice = row['OrgPrice']
        rating = row['Rating']
        stock = row['Stock']
        sellerid = user_data.get('sellerid')
        currency = 'USD'
        pimage1 = 0
        pimage2 = 0
        pimage3 = 0

        # Insert the values into the database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO products (pcategory, psubcategory, pbrand, ptitle, pdescription, pprice, porgprice, prating, pstock, pimage, pimage1, pimage2, pimage3, sellerid,currency) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        values = (category, subcategory, brand, title, description, price, orgprice, rating, stock, image, pimage1, pimage2, pimage3, sellerid, currency)
        cursor.execute(sql, values)
        mysql.connection.commit()

    return 'Products added successfully'



@app.route('/add_single_product', methods=['GET','POST'])
def add_single_product():
    category = request.form['category']
    subcategory = request.form['subcategory']
    brand = request.form['brand']
    title = request.form['title']
    description = request.form['desc']
    price = request.form['price']
    orgprice = request.form['orgprice']
    rating = request.form['rating']
    image = request.form['image']

    image1 = request.files['image1'].read()
    image2 = request.files['image2'].read()
    image3 = request.files['image3'].read()
    stock = request.form['stock']
    currency = request.form['currency']
    
    # encoded_data = base64.b64encode(image).decode('utf-8')  # Decode the encoded data before inserting into the database
    insert_product(category, subcategory, brand, title, description, price, orgprice, rating, image, image1, image2, image3, stock, currency)
    return 'Product added successfully'

def insert_product(category, subcategory, brand, title, description, price, orgprice, rating, image, image1, image2, image3, stock, currency):
    user_data = inject_data()
    seller= user_data.get('sellerid')
    
    cursor = mysql.connection.cursor()
    # SQL query to insert data into products table
    sql = "INSERT INTO products (pcategory, psubcategory, pbrand, ptitle, pdescription, pprice, porgprice, prating, pstock, pimage, pimage1, pimage2, pimage3, sellerid, currency) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # Execute the query
    cursor.execute(sql, (category, subcategory, brand, title, description, price, orgprice, rating, stock, image, image1, image2, image3, seller, currency))
    # Commit the changes to the database
    mysql.connection.commit()
    # Close the database connection
    cursor.close()

@app.route('/download_template')
def download_template():
    path = "uploads/products.xlsx"
    # Send the Excel file as a download attachment
    return send_file(path, as_attachment=True)

@app.route('/')
def index():

        return render_template('index.html')

@app.route('/reset',methods = ['GET','POST'])
def reset():
    cursor = mysql.connection.cursor()
    email = session.get('emailver')
    # print(email)

    cursor.execute('SELECT * FROM seller WHERE email=%s', (email,))
    account = cursor.fetchone()
    if account:
        val = account[13]
        if request.method == 'POST':
             password = request.form['newpass']
             hashpass = hashlib.sha256(password.encode()).hexdigest()
             confirm_password = request.form['conpass']
             hashconpass = hashlib.sha256(confirm_password.encode()).hexdigest()
             if password == confirm_password:
                    cursor.execute('UPDATE seller SET password =%s, conpass =%s, otp=NULL WHERE email=%s', (hashpass, hashconpass, email))
                    mysql.connection.commit()
                    msg = 'Password Reset successfully'
                    return render_template('sellerregister.html',msg = msg)
             else:
                    flash('Passwords do not match')
                    return render_template('reset.html', val=val)
        else:
                flash('Invalid OTP')
                return render_template('reset.html', val=val)
    else:
        val = None
    return render_template('reset.html', val=val)

    

@app.route('/generateotp', methods = ['GET','POST'] )
def generateotp():
    return render_template('otp.html')

@app.route('/email-verification', methods = ['GET','POST'] )
def emailverification():
    if request.method == 'POST' and 'mail' in request.form:
        email = request.form['mail']

        cursor = mysql.connection.cursor()

        cursor.execute('SELECT * FROM seller WHERE email=%s', (email,))
        account = cursor.fetchone()

        name = account[10]

        if account:
            session['emailver'] = email
            
            if 'otp' not in session:  # Check if OTP has been generated yet
                otp = random.randint(100000, 999999)
                # print(otp)
                cursor.execute('UPDATE seller SET otp=%s WHERE email=%s', (otp, email))
                mysql.connection.commit()
                session['otp'] = otp
                html = render_template('email.html', name=name , otp=otp)
                msg = Message('Subject of the email', sender='team.personelexpensetracker@gmail.com', recipients=[email])
                msg.html = html

                # Send the email message
                mail.send(msg)
            return redirect(url_for('reset'))
        else:
            flash('Email does not exist')
            return redirect(url_for('generateotp'))

    return render_template('otp.html')


@app.route('/logreg', methods =["GET","POST"])
def logreg():
    msg = ''
    name = ''
    if 'register' in request.form:

        if request.method == 'POST' and 'uname' in request.form and 'pass' in request.form and 'email' in request.form and 'phone' in request.form and 'conpass' in request.form :
            fullname = request.form['name']
            username = request.form['uname']
            shopname = request.form['shopname']
            ownername = request.form['ownername']
            shopno = request.form['shopno']
            shopaddress = request.form['shopaddress']
            regno =request.form['regno']
            email = request.form['email']
            mobile = request.form['phone']
            password = request.form['pass']
            conpassword = request.form['conpass']
            address = request.form['address']

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            hashed_conpassword = hashlib.sha256(conpassword.encode()).hexdigest()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM seller WHERE username = % s', (username, ))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                if (password == conpassword):
                    cursor.execute('INSERT INTO seller VALUES (NULL,%s , % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, NULL)', (fullname,mobile, email, address,shopname,ownername,shopno,shopaddress,regno,username ,hashed_password, hashed_conpassword,  ))
                    mysql.connection.commit()
                    msg = 'You have successfully registered !'
                else:
                    msg = 'Passwords does not match.Reenter password'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('Sellerregister.html', msg = msg)
    else:
        if request.method == 'POST' and 'uname' in request.form and 'upass' in request.form:
            username = request.form['uname']
            password = request.form['upass']
            hashpass = hashlib.sha256(password.encode()).hexdigest()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM seller WHERE password = % s', (hashpass, ))
            
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['username'] = username
                msg = "Login successfull"
                # resp = make_response(render_template('index.html',msg = msg))
                # resp.set_cookie('username', username)
                # return resp
                return redirect(url_for('home'))
                
            else:
                msg = "Invalid Credentials"
    
    return render_template("sellerregister.html",msg =msg)
    

@app.route('/home')
def home():
    uname = session.get('username')

    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM seller WHERE username = %s", (uname,))
        res = cursor.fetchall()

        if not res:
            return "User not found", 404

        sidval = res[0][0]


        cursor.execute("SELECT SUM(ordertotal), SUM(orderoftotparitem), SUM(orderstatus = 'pending') as pending FROM orders WHERE sellerid = %s", (sidval,))
        statdata = cursor.fetchone()

        cursor.execute("SELECT orders.orderid, orderdetails.paymentstatus, products.ptitle, orders.orderstatus FROM orders JOIN orderdetails ON orders.orderid = orderdetails.orderid JOIN products ON orders.orderproductid = products.esin WHERE orders.sellerid = %s ORDER BY orders.orderdate DESC LIMIT 10;", (sidval,))
        rodata = cursor.fetchall()     
        print(rodata)   


    return render_template('home.html', res=res, statdata=statdata,rdata = rodata, active='home')


@app.route('/analytics') 
def analytics():
    user_data = inject_data()
    sellerid = user_data.get('sellerid')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DATE(orderdate) AS order_date, sellerid, SUM(orderoftotparitem) AS total_sales_per_day FROM orders WHERE sellerid = %s GROUP BY DATE(orderdate)",(sellerid,)) 
    salestrend = cursor.fetchall()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT SUM(orders.orderoftotparitem), products.ptitle  FROM orders  JOIN products ON orders.orderproductid = products.esin  WHERE orders.sellerid = %s GROUP BY products.ptitle;",(sellerid,))
    revbyprod = cursor.fetchall()

    cursor = mysql.connection.cursor()
    cursor.execute("select count(orders.orderstatus),orders.orderstatus from orders where orders.sellerid = %s group by orders.orderstatus",(sellerid,))
    ordstat = cursor.fetchall()

    cursor = mysql.connection.cursor()
    cursor.execute("select sum(orders.orderoftotparitem),products.psubcategory from orders join products on orders.orderproductid = products.esin where orders.sellerid=%s group by products.psubcategory;",(sellerid,))
    salebycat = cursor.fetchall()
    print(salebycat)

    cursor = mysql.connection.cursor()
    cursor.execute(" SELECT DATE_FORMAT(orderdate, '%%Y-%%m') AS month,SUM(ordertotal) AS revenue FROM orders where sellerid =%s GROUP BY DATE_FORMAT(orderdate, '%%Y-%%m') ORDER BY month ASC",(sellerid,))
    revdata = cursor.fetchall()
    print(revdata)



    return render_template('analytics.html', active='analytics', data1 = salestrend ,data2 = revbyprod , data3 = ordstat ,salecat = salebycat,revdata = revdata)

@app.route('/addproducts')
def addproducts():
    return render_template('addproducts.html', active='add')

@app.route('/orderspage')
def orderspage():
    user_data = inject_data()
    sellerid = user_data.get('sellerid')
    cur = mysql.connection.cursor()
    cur.execute("select * from orders where sellerid = %s",(sellerid,))
    orders = cur.fetchall()


    return render_template('orderspage.html', active='order',orders = orders)


@app.route('/change_status', methods=['POST'])
def change_status():
    data = request.get_json()
    order_id = data['id']
    new_status = data['status']
    print(order_id)
    print(new_status)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET orderstatus=%s WHERE orderid=%s", (new_status, order_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Status changed successfully'})


@app.route('/report')
def report():
    return render_template('report.html', active='report')

@app.route('/customer')
def customer():
    user_data = inject_data()
    sellerid = user_data.get('sellerid')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT users.username, users.email, users.address, SUM(orders.orderoftotparitem) as total_orders,sum(orders.ordertotal) as totalamount FROM users JOIN orders ON users.username = orders.username where orders.sellerid = %s GROUP BY users.username",(sellerid,))
    customers = cursor.fetchall()
    return render_template('customer.html', active='customer',customers = customers)

@app.route('/productspage')
def productspage():
    uname = session.get('username')
    cursor = mysql.connection.cursor()
    cursor1 = mysql.connection.cursor()
    cursor.execute("Select id from seller Where username = %s",(uname,))
    id = cursor.fetchone()

    cursor1.execute("select * from products where sellerid = %s",(id,))
    res = cursor1.fetchall()

    

    return render_template('productspage.html',result = res, active='product')


@app.route('/update', methods=['POST'])
def update():
    id = request.form['esin']
    title = request.form['ptitle']
    description = request.form['pdesc']
    pprice = request.form['pprice']
    pmrp = request.form['pmrp']
    stock = request.form['pstock']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE products SET ptitle=%s, pdescription=%s, pprice=%s, porgprice=%s, pstock=%s WHERE esin=%s", (title, description, pprice, pmrp, stock, id))
    mysql.connection.commit()

    return redirect(url_for('productspage'))


@app.route('/updateprofile', methods=['POST'])  


def updateprofile():
            name = session.get('username')
            fullname = request.form['name']
            shopname = request.form['shopname']
            ownername = request.form['ownername']
            shopno = request.form['shopno']
            shopaddress = request.form['shopaddress']
            regno =request.form['regno']
            email = request.form['email']
            mobile = request.form['phone']
 
            address = request.form['address']
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE seller SET fullname=%s, phone=%s, email=%s, address=%s, shopname=%s,ownername =%s,shopnumber =%s,shopaddress=%s,regnum=%s WHERE username=%s", (fullname, mobile, email, address, shopname, ownername,shopno,shopaddress,regno,name))
            mysql.connection.commit()

            return redirect(url_for('home'))


def update_status():
    # Get the order ID and status from the form submission
    order_id = request.form['order_id']
    new_status = request.form['new_status']
    
    # Update the order status in the database or some other storage method
    # Here, we'll just print the new status for demonstration purposes
    print(f"Order {order_id} status updated to {new_status}")
    
    # Return a response to indicate the status update was successful
    return redirect(url_for('orderspage'))


@app.route('/deleteprod/<string:id>', methods=['GET'])
def deleteprod(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE esin = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('productspage'))
 
# @app.route('/upload', methods=['POST'])
# def upload():
#     image = request.files['image'].read()
#     conn = mysql.connector.connect(user='root', password='Aadi@9011', host='localhost', database='demo')
#     cursor = conn.cursor()
#     cursor.execute('INSERT INTO images (image) VALUES (%s)', (image,))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return 'Image uploaded successfully'

# @app.route('/image/<int:image_id>')
# def image(image_id):
#     conn = mysql.connector.connect(user='root', password='Aadi@9011', host='localhost', database='demo')
#     cursor = conn.cursor()
#     cursor.execute('SELECT image FROM images WHERE id=%s', (image_id,))
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if result is not None:
#         image_data = result[0]
#         return Response(image_data, mimetype='image/jpeg')
#     else:
#         return 'Image not found', 404

@app.context_processor
def inject_data():
    # logic to retrieve data
    name =session.get('username')
    cursor = mysql.connection.cursor()
    cursor.execute("Select * from seller Where username = %s",(name,))
    res = cursor.fetchall() 
    sowner =0
    sname =0
    sid =0
    for data in res:  
        sowner = data[6]
        sname = data[5]
        sid = data[0]
    

    return dict(uname=name,shopown = sowner,shopname =sname,sellerid = sid,result = res)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    resp = make_response(render_template('sellerregister.html'))
    resp.delete_cookie('username')
    return resp




if __name__ == '__main__':
    app.run(debug=True, port=4000)