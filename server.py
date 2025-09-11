# server.py
from flask import Flask, jsonify
from requests_html import HTMLSession

app = Flask(__name__)

@app.route('/get_set_data')
def get_set_data():
    """
    Scrapes the SET Index and Value from the SET website, calculates the live result,
    and returns a JSON response.
    """
    try:
        session = HTMLSession()
        url = 'https://www.set.or.th/th/market/index/set/overview'
        response = session.get(url)

        # Scrape the SET Index value (e.g., 1278.05)
        set_index_element = response.html.find('span.value-text-white', first=True)
        set_result = set_index_element.text.strip() if set_index_element else None

        # Scrape the 'Value' (e.g., 19,118.89)
        # Note: The class 'ms-1' and 'ms-xl-4' are from your provided image's HTML.
        value_element = response.html.find('span.ms-1.ms-xl-4', first=True)
        # Clean the value text by removing commas and converting to a number
        value_text = value_element.text.strip().replace(',', '') if value_element else None
        
        # Calculate the live result based on your specified formula
        live_result = ""
        if set_result and value_text:
            # First digit: last decimal number of the SET Index (e.g., 5 from 1278.05)
            # Find the index of the decimal point
            decimal_index = set_result.find('.')
            if decimal_index != -1 and len(set_result) > decimal_index + 1:
                first_digit = set_result[decimal_index + 2] # The second digit after the decimal
                live_result += first_digit

            # Second digit: the number before the decimal from the Value (e.g., 2 from 19118.89)
            try:
                # Convert the cleaned value string to a float and get the integer part
                value_float = float(value_text)
                value_before_decimal = str(int(value_float))
                second_digit = value_before_decimal[-1] # Get the last digit of the integer part
                live_result += second_digit
            except (ValueError, IndexError):
                live_result = "00" # Default value if parsing fails

        # Prepare the final JSON data
        data = {
            "live_result": live_result,
            "set_result": set_result,
            "value": value_text,
            "status": "success"
        }
            
        return jsonify(data)

    except Exception as e:
        # Return an error message if anything goes wrong during scraping or calculation
        return jsonify({
            "live_result": "00",
            "set_result": None,
            "value": None,
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
