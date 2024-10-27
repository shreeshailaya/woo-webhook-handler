from flask import Flask, request, jsonify
import json
import logging
import datetime
import urllib.parse



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
    list_of_items_id = []
    email =''
    try:
        # Parse as raw URL-encoded data
        raw_data = request.get_data(as_text=True)
        order_data = urllib.parse.parse_qs(raw_data)
        data = str(order_data)
        try:
            # First, normalize the string by ensuring proper escaping of nested quotes
            data = data.replace('\\"', '"')  # Remove any already escaped quotes
            data = data.replace('"[', '[')   # Fix nested array start
            data = data.replace(']"', ']')   # Fix nested array end
            # Parse JSON
            data = json.loads(data)
            print("Successfully parsed JSON!")
            for i in range(len(data['line_items'])):
                print(data['line_items'][i]['product_id'])
            print(data['billing']['email'])
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Error position: {e.pos}")
            print(f"Error line: {e.lineno}, column: {e.colno}")
            # Print more context around the error
            start_pos = max(0, e.pos - 50)
            end_pos = min(len(data), e.pos + 50)
            print(f"Problematic string portion:\n{data[start_pos:end_pos]}")
       
        # Send a response back to WooCommerce
        return jsonify({"status": "success", "message": "Order processed successfully"}), 200
    
    except Exception as e:
        print("Error processing order:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    
@application.route('/', methods=['GET'])
def home():
    try:
        return "<marquee>Welcome to PublicMart</marquee>", 200
    except Exception as e:
        print("Error processing order:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    application.run(port=5000, debug=True)
