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

        # --- Scrape SET Index ---
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else "N/A"

        # --- Scrape Value (M.Baht) safely inside its parent div ---
        value_container = soup.find('div', class_='d-block quote-market-cost ps-2 ps-xl-3')
        value = "N/A"
        if value_container:
            value_span = value_container.find('span', class_='ms-2 ms-xl-4')
            if value_span:
                value = value_span.text.strip().replace(",", "")

        # --- Compute live_result ---
        if set_result != "N/A" and value != "N/A":
            try:
                last_digit_set = set_result[-1]   # last digit of full SET (including decimals)
                value_int = value.split(".")[0]   # take integer part only
                last_digit_value = value_int[-1]  # last digit of integer part
                live_result = last_digit_set + last_digit_value
            except Exception as e:
                print(f"[ERROR] Live result calculation failed: {e}")
                live_result = "N/A"
        else:
            live_result = "N/A"

        # Debug log for Render
        print(f"[DEBUG] set_result={set_result}, value={value}, live_result={live_result}")

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
