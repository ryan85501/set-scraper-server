from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket
from datetime import datetime, time
import pytz

app = Flask(__name__)
CORS(app)

# Store last official result globally
official_result = {"set_result": "N/A", "value": "N/A", "live_result": "N/A"}

# Timezone (Bangkok time for SET market)
BANGKOK_TZ = pytz.timezone("Asia/Bangkok")

def is_market_open():
    """Check if current time is within allowed trading windows (Mon–Fri)."""
    now = datetime.now(BANGKOK_TZ)
    weekday = now.weekday()  # Monday=0, Sunday=6

    if weekday >= 5:  # Saturday or Sunday
        return False

    morning_start = time(11, 30)
    morning_end = time(12, 1)
    afternoon_start = time(15, 30)
    afternoon_end = time(16, 30)

    if morning_start <= now.time() <= morning_end:
        return True
    if afternoon_start <= now.time() <= afternoon_end:
        return True
    return False


@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    global official_result

    if not is_market_open():
        # Outside trading hours → return last official result
        return jsonify(official_result)

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

        # --- Scrape Value (M.Baht) ---
        value_container = soup.find('div', class_='d-block quote-market-cost ps-2 ps-xl-3')
        value = "N/A"
        if value_container:
            value_span = value_container.find('span', class_='ms-2 ms-xl-4')
            if value_span:
                value = value_span.text.strip().replace(",", "")

        # --- Compute live_result ---
        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            try:
                last_digit_set = set_result[-1]   # last digit of full SET (including decimals)
                value_int = value.split(".")[0]   # integer part only
                last_digit_value = value_int[-1]  # last digit of integer part
                live_result = last_digit_set + last_digit_value
            except Exception as e:
                print(f"[ERROR] Live result calculation failed: {e}")

        # Build result object
        result = {
            'set_result': set_result,
            'value': value,
            'live_result': live_result
        }

        # Save as official result if it's the last minute of the session
        now = datetime.now(BANGKOK_TZ).time()
        if now >= time(12, 1) or now >= time(16, 30):
            official_result = result
            print(f"[OFFICIAL] Frozen official result at {now}: {official_result}")
        else:
            print(f"[LIVE] Live result at {now}: {result}")

        return jsonify(result)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify(official_result)


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000)
