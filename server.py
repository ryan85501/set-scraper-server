# --- Corrected Flask Server Code ---
# This server scrapes SET data and calculates live_result correctly.

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    """
    Fetches live SET data from the SET.or.th website by scraping.
    live_result = (last digit of set_result’s decimal) + (last digit before decimal in value)
    """
    try:
        url = "https://www.set.or.th/th/market/index/set/overview"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find SET index value
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip() if set_index_div else "N/A"

        # Find Value (M.Baht)
        value_div = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_div.text.strip() if value_div else "N/A"

        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            try:
                # --- Formula ---
                # Last digit of set_result’s decimal
                if "." in set_result:
                    decimal_part = set_result.split(".")[1]
                    last_digit_set = decimal_part[-1] if decimal_part else "0"
                else:
                    last_digit_set = "0"

                # Last digit before decimal in value
                integer_part_value = value.split(".")[0].replace(",", "")
                last_digit_value = integer_part_value[-1] if integer_part_value else "0"

                live_result = last_digit_set + last_digit_value
            except Exception as e:
                print(f"Error calculating live_result: {e}")
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
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server will be running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
