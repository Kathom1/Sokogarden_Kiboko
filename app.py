from flask import *
import pymysql
from flask_cors import CORS
import os #Allows the python code to communicate with the operating system in use
app = Flask(__name__)
CORS(app) #Allows requests from external origins
#Configuring our upload folder
app.config['UPLOAD_FOLDER'] = 'Static/Images'

@app.route ('/api/signup',methods=['POST'])
def signup():
    #Extract values posted in the request and store them in variables
    username = request.form ['username']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    # Connect to database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')

    # Initialise the connection
    cursor = connection.cursor()
    
    # Do the sql query to insert data of the 4 columns
    sql = 'insert into users(username,password,email,phone) values(%s,%s,%s,%s)'

    # Create data to replace the placeholders
    data = (username,password,email,phone)

    # Execute the sql and data together using our cursor
    cursor.execute(sql,data)

    # We need to commit/save changes
    connection.commit()

    return jsonify ({'success':'Thank you for joining'})

#Sign in route    
@app.route ('/api/signin',methods=['POST'])
def signin():
    #Extracting values and storing them as variables
    username = request.form['username']
    password = request.form['password']

    #Connection to database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')

    #Initialising the connection
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    #Sql query
    sql = 'select * from users where username = %s and password = %s'

    #Data for placeholders
    data = (username,password)

    #Executing sql and data together
    cursor.execute(sql,data)

    #We do not commit cause the data is already in the database we are just reading data

    count = cursor.rowcount
    if count == 0 :
        return jsonify({'message':'login failed'})
    else:
        user = cursor.fetchone()
        #Remove the password key
        del user['password']
        return jsonify({'message':'login successful',
                        'user': user})
    
#Add products route
@app.route ('/api/add_product',methods = ['POST'])
def add_product():
    #Extracting values and storing them in form of variables
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    #Extract image data
    product_photo= request.files['product_photo']

    #Get the image file name
    filename = product_photo.filename

    #Specify computer path where the image will be saved
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)

    #Save the above path
    product_photo.save(photo_path)

    #Connection to database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')

    #Initialising the connection
    cursor = connection.cursor()

    #SQL query
    sql='insert into product_details(product_name,product_description,product_cost,product_photo) values(%s,%s,%s,%s)'

    #Data to replace placeholders
    data = (product_name,product_description,product_cost,filename)

    #Executing the sql together with the data
    cursor.execute(sql,data)

    #Saving changes to the database
    connection.commit()

    return jsonify({'message':'Product added successfully'})

    # Get Products
@app.route('/api/get_products_details')
def get_products_details():
    # Connection to database
    connection = pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')

    # Creating cursor object
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    # SQL Query
    sql='select * from product_details'

    # Executing the sql
    cursor.execute(sql)

    # Get products in form of dictionary
    product_details= cursor.fetchall()

    # Return products
    return jsonify(product_details)

  # Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
        if request.method == 'POST':
            # Extract POST Values sent
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64
            encoded = base64.b64encode(data.encode())
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php",
                "AccountReference": "SokoGarden Online",
                "TransactionDesc": "Payments for Products"
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) # 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

if __name__ == '__main__':
    app.run(debug=True)