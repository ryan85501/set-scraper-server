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
        set_result_element = soup.find('p', string='SET Index')
        set_result = "N/A"
        if set_result_element:
            set_index_div = set_result_element.find_next_sibling('div')
            if set_index_div:
                set_result_value = set_index_div.find('div', class_='text-white')
                if set_result_value:
                    set_result = set_result_value.text.strip().replace(",", "")

        # --- Value (M.Baht) ---
        value_element = soup.find('p', string='Value (M.Baht)')
        value = "N/A"
        if value_element:
            value_div = value_element.find_next_sibling('div')
            if value_div:
                value_span = value_div.find('div', class_='text-white')
                if value_span:
                    value = value_span.text.strip().replace(",", "")
                    
        # --- Live Result Calculation ---
        if set_result != "N/A" and value != "N/A":
            # last digit of SET (include decimals, e.g. 1278.05 -> 5)
            last_digit_set = set_result[-1]

            # remove decimals from value and pick last digit (e.g. 42552.94 -> 42552 -> 2)
            value_int_part = value.split(".")[0]
            last_digit_value = value_int_part[-1]

            live_result = last_digit_set + last_digit_value
        else:
            live_result = "N/A"

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
