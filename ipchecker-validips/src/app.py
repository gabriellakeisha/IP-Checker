# main Flask application
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

def is_valid_ipv4(ip):
    # validating IPv4 address: must have exactly 4 groups separated by dots
    if not ip or ip.strip() == '':
        return False
    
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    return True

def is_valid_ipv6(ip):
    # validating IPv6 address: must have 2-8 groups separated by colons
    if not ip or ip.strip() == '':
        return False
    
    parts = ip.split(':')
    if len(parts) < 2 or len(parts) > 8:
        return False
    
    return True

# total valid IP based on the comma-separated list of IP addresses 
def count_valid_ips(items_string):
    # checking validity status
    if not items_string:
        return 0, []
    
    items = items_string.split(',')
    valid_count = 0
    validity_list = []
    
    for item in items:
        item = item.strip()
        
        if not item: # empty string
            validity_list.append({'ip': '', 'valid': False, 'reason': 'empty'})
            continue
        
        # check IPv4
        if '.' in item and is_valid_ipv4(item):
            valid_count += 1
            validity_list.append({'ip': item, 'valid': True, 'type': 'IPv4'})
        # check IPv6
        elif ':' in item and is_valid_ipv6(item):
            valid_count += 1
            validity_list.append({'ip': item, 'valid': True, 'type': 'IPv6'})
        else:
            validity_list.append({'ip': item, 'valid': False, 'reason': 'invalid format'})
    
    return valid_count, validity_list

@app.route('/', methods=['GET'])
# endpoint to validate the IPs
def validate_ips():
    # GET parameter: items (comma-separated IP addresses)
    # returns: JSON with validation results

    # get items parameter
    items = request.args.get('items', '')
    
    # validate input
    if not items:
        return jsonify({
            'error': 'No items provided. Please provide IP addresses',
            'valid_count': 0,
            'items': ''
        }), 400
    
    # count valid IPs
    try:
        valid_count, validity_list = count_valid_ips(items)
        
        return jsonify({
            'error': '',
            'items': items,
            'valid_count': valid_count,
            'total_items': len(items.split(',')),
            'details': validity_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Error processing request: {str(e)}',
            'valid_count': 0,
            'items': items
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    # health check
    return jsonify({'status': 'healthy', 'service': 'ipchecker-validips'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
