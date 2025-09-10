# --- Corrected Flask Server Code ---
# This server is a proxy to scrape data from a website and serve it to the frontend.
# It now correctly returns 'set_result', 'value', and 'live_result' in the JSON response.

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
CORS(app) # This enables CORS for all routes, allowing your HTML to fetch data

@app.route('/get_set_data', methods=['GET'])
def get_set_data():
    """
    Fetches live SET data from the SET.or.th website by scraping.
    This function is a proxy to bypass CORS issues when fetching data directly from the browser.
    """
    try:
        url = "https://www.set.or.th/th/market/index/set/overview"
        
        # Add more headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the SET Index value
        set_index_div = soup.find('div', class_='value text-white mb-0 me-2 lh-1 stock-info')
        set_result = set_index_div.text.strip() if set_index_div else "N/A"

        # Find the "Value" number
        value_div = soup.find('span', class_='ms-2 ms-xl-4')
        value = value_div.text.strip() if value_div else "N/A"
        
        # --- PLACEHOLDER FOR 2D LOTTERY DATA SCRAPING ---
        # The scraping logic for the live 2D result needs to be added here.
        # This is currently hardcoded to "N/A".
        live_result = "N/A"
        
        # Return all three pieces of data
        if set_result != "N/A" and value != "N/A":
            return jsonify({
                'set_result': set_result,
                'value': value,
                'live_result': live_result
            })
        else:
            print("Could not find the necessary data on the page.")
            return jsonify({'error': 'Data not found on the page'}), 500

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({'error': 'Failed to connect to the external website.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

if __name__ == '__main__':
    # Get the computer's local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server will be running on: http://{local_ip}:5000")
    # This runs the app on your local network, making it accessible from your phone.
    app.run(host='0.0.0.0', port=5000)
