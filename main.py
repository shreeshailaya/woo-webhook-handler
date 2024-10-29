from flask import Flask, request, jsonify
import json
import logging
import datetime
import urllib.parse
from decouple import config
import mysql.connector
from share import share_file_with_user


application = Flask(__name__)



def create_logger(log_file_name='public-mart.log'):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a formatter to specify the format of log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler to write logs to the specified file
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger
logger = create_logger()



# Endpoint to handle WooCommerce order data
@application.route('/api/order', methods=['POST'])
def order_handler():
    now = datetime.datetime.now()
    print(now, "START OPERATION")
    data = request.get_json()
    parsed_data = data_cleaning(data=data)
    email=parsed_data['billing']['email']
    table_name = config("DRIVE_TABLE")
    for i in range(len(parsed_data['line_items'])):
        # list_of_items_id.append(parsed_data['line_items'][i]['product_id'])
        product_id = parsed_data['line_items'][i]['product_id']
        product_id = int(product_id)
        query = f"select drive_id from {table_name} where product_id = {product_id}"
        drive_id = execute_query(query=query)
        print(drive_id[0])
        print(email)
        share_file_with_user(file_id=drive_id[0], email=email) 
    print(now, "END OPERATION")
    # Send a response back to WooCommerce
    return jsonify({"status": "success", "message": "Order processed successfully"}), 200
    

@application.route('/', methods=['GET'])
def home():
    try:
        return "<marquee>Welcome to PublicMart</marquee>", 200
    except Exception as e:
        print("Error processing order:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    



# MySQL database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config('HOST_NAME'),
            user=config('USER_NAME'), 
            password=config('USER_PASSWORD'),
            database=config('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MySQL database: {err}")
        return None


def execute_query(query, params=None):
    try:
        print(query)
        connection = get_db_connection()
        if connection is None:
            logger.error("Could not establish database connection")
            return None
            
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return result
        
    except mysql.connector.Error as err:
        logger.error(f"Error executing query: {err}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()



def data_cleaning(data):
    try:
        # First clean up the outer structure
        if data.startswith("{'") and data.endswith("'}"):
            data = data[2:-2]  # Remove {'...'}
        
        def fix_nested_json_array(text, start_marker, end_marker=']"'):
            pos = 0
            while True:
                start = text.find(start_marker, pos)
                if start == -1:
                    break
                    
                end = text.find(end_marker, start) + len(end_marker)
                if end == -1:
                    break
                    
                section = text[start:end]
                if "test101" in section:
                    fixed_section = section.replace('"test101"', '\\"test101\\"')
                if "fixed_product" in section:
                    fixed_section = fixed_section.replace('"fixed_product"', '\\"fixed_product\\"')
                text = text[:start] + fixed_section + text[end:]
                pos = start + len(fixed_section)
                
            return text
        
        # Fix both value and display_value sections
        data = fix_nested_json_array(data, '"value":"[')
        data = fix_nested_json_array(data, '"display_value":"[')
        
        # Parse JSON
        parsed_data = json.loads(data)
        print("Successfully parsed JSON!")
        print(f"Order ID: {parsed_data['id']}")
        print(f"Status: {parsed_data['status']}")

        return parsed_data

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Error position: {e.pos}")
        print("Context around error:")
        start_pos = max(0, e.pos - 50)
        end_pos = min(len(data), e.pos + 50)
        print(data[start_pos:end_pos])
        print("\nCharacter at error:", repr(data[e.pos]))



if __name__ == '__main__':
    application.run(port=5000, debug=True)
