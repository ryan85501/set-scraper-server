# --- Corrected Flask Server Code ---
# This server scrapes SET data and calculates live_result correctly.

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    """
    Fetch live SET data, extract set_result and value, 
    then calculate live_result using custom formula.
    """
    try:
        url = "https://www.set.or.th/en/market/index/set/overview"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # SET index value
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else "N/A"

        # Value number
        value_div = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_div.text.strip().replace(",", "") if value_div else "N/A"

        # Calculate live_result
        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            # remove commas, keep decimals for set_result
            set_digits = ''.join([c for c in set_result if c.isdigit()])
            last_digit_set = set_digits[-1] if set_digits else "0"

            # only integer part for value
            value_int_part = value.split(".")[0]
            last_digit_value = value_int_part[-1] if value_int_part else "0"

            live_result = f"{last_digit_set}{last_digit_value}"

            # Debug log
            print(f"[DEBUG] set_result={set_result}, value={value}, last_digit_set={last_digit_set}, last_digit_value={last_digit_value}, live_result={live_result}")

        return jsonify({
            'set_result': set_result,
            'value': value,
            'live_result': live_result
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running at: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
