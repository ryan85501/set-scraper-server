# --- Flask Server Code (server.py) ---
# Scrapes SET Index and Value from SET.or.th and returns JSON for frontend.

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
    Scrape SET Index and Value from SET.or.th
    and return JSON response with calculated live_result.
    live_result = last digit of decimal part of SET + digit before decimal of Value
    """
    try:
        url = "https://www.set.or.th/en/market/index/set/overview"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Extract SET Index
        set_index_div = soup.find("div", class_="value text-white mb-0 me-2 lh-1 stock-info")
        set_result = set_index_div.text.strip() if set_index_div else "N/A"

        # ✅ Extract Value (M.Baht)
        value_div = soup.find("span", class_="ms-2 ms-xl-4")
        value = value_div.text.strip() if value_div else "N/A"

        # ✅ Calculate live_result
        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            try:
                # Remove commas
                set_clean = set_result.replace(",", "")
                value_clean = value.replace(",", "")

                # Last digit of decimal part of SET
                if "." in set_clean:
                    decimal_part = set_clean.split(".")[1]
                    set_last_digit = decimal_part[-1] if decimal_part else "0"
                else:
                    set_last_digit = set_clean[-1]

                # Digit before decimal of Value
                if "." in value_clean:
                    integer_part = value_clean.split(".")[0]
                    value_before_decimal = integer_part[-1] if integer_part else "0"
                else:
                    value_before_decimal = value_clean[-1]

                live_result = set_last_digit + value_before_decimal
            except Exception as calc_err:
                print(f"Error calculating live_result: {calc_err}")
                live_result = "N/A"

        return jsonify({
            "set_result": set_result,
            "value": value,
            "live_result": live_result
        })

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": "Failed to connect to the external website."}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {e}"}), 500


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
