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
        url = "https://www.set.or.th/th/market/index/set/overview"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip() if set_index_div else "N/A"

        value_div = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_div.text.strip() if value_div else "N/A"

        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            set_clean = set_result.replace(",", "")
            value_clean = value.replace(",", "")

            # Last digit of decimal part of SET
            if "." in set_clean:
                decimal_part = set_clean.split(".")[1]
                last_digit_set = decimal_part[-1] if decimal_part else "0"
            else:
                last_digit_set = "0"

            # Last digit of integer part of Value
            if "." in value_clean:
                integer_part_value = value_clean.split(".")[0]
            else:
                integer_part_value = value_clean

            last_digit_value = integer_part_value[-1] if integer_part_value else "0"

            live_result = last_digit_set + last_digit_value

            # Debug logging
            print(f"[DEBUG] set_result={set_result}, value={value}, "
                  f"last_digit_set={last_digit_set}, last_digit_value={last_digit_value}, "
                  f"live_result={live_result}")

        return jsonify({
            'set_result': set_result,
            'value': value,
            'live_result': live_result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)

