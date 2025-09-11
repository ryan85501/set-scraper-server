# --- Flask Server with SET Scraper and Official Result Logic ---
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
from zoneinfo import ZoneInfo

app = Flask(__name__)
CORS(app)

# Timezone: Myanmar (Yangon)
YANGON_TZ = ZoneInfo("Asia/Yangon")

# Store official result
official_result = None
official_timestamp = None


def get_set_data():
    """
    Scrapes SET index and value from set.or.th and computes live_result.
    """
    try:
        url = "https://www.set.or.th/en/market/index/set/overview"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # --- Get SET Index ---
        set_index_div = soup.find("div", class_="value text-white mb-0 me-2 lh-1 stock-info")
        set_result = set_index_div.text.strip().replace(",", "") if set_index_div else "N/A"

        # --- Get Value (M.Baht) ---
        value_span = soup.select_one("div.d-block.quote-market-cost.ps-2.ps-xl-3 span.ms-2.ms-xl-4")
        value = value_span.text.strip().replace(",", "") if value_span else "N/A"

        live_result = "N/A"
        if set_result != "N/A" and value != "N/A":
            # Get last digit from SET (including decimals)
            last_digit_set = set_result.replace(".", "")[-1]

            # Get last digit from value (ignore decimals)
            value_int_part = value.split(".")[0] if "." in value else value
            last_digit_value = value_int_part[-1]

            # Combine
            live_result = last_digit_set + last_digit_value

        return set_result, value, live_result

    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return "N/A", "N/A", "N/A"


def is_trading_day():
    """Check if today is Monday–Friday."""
    today = datetime.now(YANGON_TZ).weekday()
    return today < 5  # 0 = Monday, 4 = Friday


def in_trading_session(now):
    """Check if current Yangon time is within trading sessions."""
    morning_start, morning_end = time(11, 30), time(12, 1)
    afternoon_start, afternoon_end = time(15, 30), time(16, 30)

    if morning_start <= now.time() <= morning_end:
        return "morning"
    elif afternoon_start <= now.time() <= afternoon_end:
        return "afternoon"
    return None


@app.route("/get_set_data", methods=["GET"])
def get_set_data_route():
    global official_result, official_timestamp

    now = datetime.now(YANGON_TZ)
    session = in_trading_session(now)

    # Display current Yangon time
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    if not is_trading_day():
        return jsonify({
            "error": "Market Closed (Weekend)",
            "current_time": current_time_str,
            "set_result": "N/A",
            "value": "N/A",
            "live_result": "N/A",
            "official_result": official_result,
            "official_timestamp": official_timestamp
        })

    set_result, value, live_result = get_set_data()

    if session:
        # Live session → update live result
        official_result = live_result
        official_timestamp = current_time_str
    else:
        # Outside session → keep static official result
        live_result = official_result

    return jsonify({
        "current_time": current_time_str,
        "set_result": set_result,
        "value": value,
        "live_result": live_result,
        "official_result": official_result,
        "official_timestamp": official_timestamp
    })


if __name__ == "__main__":
    print("Flask server running with Myanmar (Yangon) timezone")
    app.run(host="0.0.0.0", port=5000)

