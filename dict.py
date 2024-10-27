import json
import ast
data = ''
try:
    # First, normalize the string by ensuring proper escaping of nested quotes
    data = data.replace('\\"', '"')  # Remove any already escaped quotes
    data = data.replace('"[', '[')   # Fix nested array start
    data = data.replace(']"', ']')   # Fix nested array end
    
    # Parse JSON
    data = json.loads(data)
    print("Successfully parsed JSON!")
    print(len(data['line_items']))
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