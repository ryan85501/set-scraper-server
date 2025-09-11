# --- Corrected Flask Server Code ---
# This server scrapes SET.or.th and calculates live_result properly.

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

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

        # --- Scrape SET index ---
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else "N/A"

        # --- Scrape Value (M.Baht) ---
        value_div = soup.find('div', class_='d-block quote-market-value ps-2 ps-xl-3')
        value = value_div.text.strip().replace(",", "") if value_div else "N/A"

        # --- Compute live_result ---
        if set_result != "N/A" and value != "N/A":
            try:
                # Last digit of SET result (including decimals)
                last_digit_set = set_result[-1]

                # Last digit of value (ignore decimals, take integer part)
                value_int = value.split(".")[0]
                last_digit_value = value_int[-1]

                live_result = last_digit_set + last_digit_value

            except Exception as e:
                print(f"[ERROR] Live result calculation failed: {e}")
                live_result = "N/A"
        else:
            live_result = "N/A"

        return jsonify({
            'set_result': set_result,
            'value': value,
            'live_result': live_result
        })

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({'error': 'Failed to connect to the external website.'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {e}'}), 500


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
