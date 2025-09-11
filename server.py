# --- Corrected Flask Server Code with Frozen Time ---
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, time as dtime

app = Flask(__name__)
CORS(app)

# Store last official snapshot (result + time)
last_official_data = {
    "set_result": None,
    "value": None,
    "live_result": None,
    "time": None
}

# Myanmar Timezone
yangon_tz = pytz.timezone("Asia/Yangon")

def is_within_trading_hours(now):
    """Check if current Myanmar time is within trading windows."""
    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:  # Saturday or Sunday
        return False

    morning_start = dtime(11, 30)
    morning_end = dtime(12, 1)
    afternoon_start = dtime(15, 30)
    afternoon_end = dtime(16, 30)

    return (morning_start <= now.time() <= morning_end) or \
           (afternoon_start <= now.time() <= afternoon_end)

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    global last_official_data

    now = datetime.now(yangon_tz)

    # If not trading time, return last official frozen data
    if not is_within_trading_hours(now):
        if last_official_data["set_result"]:
            return jsonify(last_official_data)
        else:
            return jsonify({"error": "No official data yet"}), 503

    try:
        url = "https://www.set.or.th/en/market/index/set/overview"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- SET Index ---
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else None

        # --- Value (M.Baht) ---
        value_span = soup.find("div", class_="d-block quote-market-cost ps-2 ps-xl-3") \
                         .find("span", class_="ms-2 ms-xl-4")
        value = value_span.text.strip().replace(",", "") if value_span else None

        # --- Compute live_result ---
        live_result = None
        if set_result and value:
            try:
                # Last digit of set_result (include decimals)
                last_digit_set = set_result[-1]

                # Remove decimals in value and pick last digit
                value_no_decimal = value.split(".")[0]
                last_digit_value = value_no_decimal[-1]

                live_result = last_digit_set + last_digit_value
            except Exception:
                live_result = None

        # --- Time snapshot ---
        current_time = now.strftime("%I:%M %p")  # e.g., "11:45 AM"

        # If we're at freeze cutoff -> store official data
        if now.time() >= dtime(12, 1) and now.time() < dtime(15, 30):
            # Freeze at 12:01 PM
            if live_result:
                last_official_data = {
                    "set_result": set_result,
                    "value": value,
                    "live_result": live_result,
                    "time": "12:01 PM"
                }
        elif now.time() >= dtime(16, 30):
            # Freeze at 4:30 PM
            if live_result:
                last_official_data = {
                    "set_result": set_result,
                    "value": value,
                    "live_result": live_result,
                    "time": "04:30 PM"
                }
        else:
            # Normal trading → update live
            if live_result:
                last_official_data = {
                    "set_result": set_result,
                    "value": value,
                    "live_result": live_result,
                    "time": current_time
                }

        return jsonify(last_official_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
