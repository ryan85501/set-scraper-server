# --- Flask Server for SET Scraping with Frozen Results ---
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# Store the last official data
last_official_data = None  

# Myanmar TimeZone
myanmar_tz = pytz.timezone("Asia/Yangon")


def fetch_set_data():
    """
    Scrape the SET website to get SET Index and Value.
    """
    url = "https://www.set.or.th/en/market/index/set/overview"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Get SET Index
    set_div = soup.find("div", class_="value text-white mb-0 me-2 lh-1 stock-info")
    set_result = set_div.text.strip().replace(",", "") if set_div else None

    # Find "Value (M.Baht)" label and extract the number after it
    value_label = soup.find(string=lambda text: text and "Value (M.Baht)" in text)
    value = None
    if value_label:
        value_span = value_label.find_next("span")
        if value_span:
            value = value_span.text.strip().replace(",", "")

    if not set_result or not value:
        return None, None

    return set_result, value



def calculate_live_result(set_result, value):
    """
    Calculate live_result using:
    - last digit of set_result (including decimals)
    - last digit of value (integer part only, no decimals)
    """
    try:
        # last digit of SET
        set_str = set_result.replace(",", "")
        last_digit_set = set_str[-1]

        # last digit of Value (ignore decimals)
        value_str = value.split(".")[0].replace(",", "")
        last_digit_value = value_str[-1]

        return last_digit_set + last_digit_value
    except Exception:
        return None


@app.route("/get_set_data", methods=["GET"])
def get_set_data():
    global last_official_data

    now = datetime.now(myanmar_tz)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Trading windows (Myanmar time)
    morning_start = now.replace(hour=11, minute=30, second=0, microsecond=0)
    morning_end = now.replace(hour=12, minute=1, second=0, microsecond=0)
    evening_start = now.replace(hour=15, minute=30, second=0, microsecond=0)
    evening_end = now.replace(hour=16, minute=30, second=0, microsecond=0)

    in_morning = morning_start <= now <= morning_end
    in_evening = evening_start <= now <= evening_end

    try:
        if in_morning or in_evening:
            # Live trading → fetch fresh data
            set_result, value = fetch_set_data()

            if set_result and value:
                live_result = calculate_live_result(set_result, value)

                last_official_data = {
                    "set_result": set_result,
                    "value": value,
                    "live_result": live_result,       # Example initial 2D result (calculated manually)
                    "time": current_time,
                }
                return jsonify(last_official_data)

        # Outside trading → return last frozen result
        if last_official_data:
            return jsonify(last_official_data)

        # If no frozen data yet
        return jsonify({"set_result": "1293.62",
            "value": "38576.94",
            "live_result": "26",
            "time": "2025-09-12 16:30:13"})

    except Exception as e:
        if last_official_data:
            return jsonify(last_official_data)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on: http://{local_ip}:5000")
    app.run(host="0.0.0.0", port=5000)



