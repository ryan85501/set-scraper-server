from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
CORS(app)

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    try:
        url = "https://www.set.or.th/en/market/index/set/overview"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- SET Result (Index value) ---
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else "N/A"

        # --- Value (M.Baht) ---
        value_span = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_span.text.strip().replace(",", "") if value_span else "N/A"

        # --- Live Result Calculation ---
        if set_result != "N/A" and value != "N/A":
            # last digit of SET (including decimals)
            last_digit_set = set_result[-1]

            # remove decimals from value and pick last digit
            value_int_part = value.split(".")[0]
            last_digit_value = value_int_part[-1]

            live_result = last_digit_set + last_digit_value
        else:
            live_result = "N/A"

        # DEBUG LOGGING for Render logs
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
    print(f"Server will be running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
