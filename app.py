from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Function to get SIM provider
def get_sim_provider(mobile_number):
    access_key = '0bcbac976cd60ea1a2947e605ab471f8'  # Replace with your actual Numverify access key
    url = f'http://apilayer.net/api/validate?access_key={access_key}&number={mobile_number}&country_code=IN'

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['valid']:
            return data['carrier']  # Returns the SIM provider
        else:
            return "Invalid mobile number"
    else:
        return "Error: Unable to fetch data"

# HTML template with embedded CSS for styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIM Provider Finder</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            font-family: Arial, sans-serif;
        }
        .container {
            text-align: center;
            background: rgba(0, 0, 0, 0.5);
            padding: 40px;
            border-radius: 10px;
        }
        input[type="text"] {
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
            width: 250px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #2575fc;
            color: white;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #6a11cb;
        }
        .result {
            margin-top: 20px;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SIM Provider Finder</h1>
        <form method="POST">
            <input type="text" name="mobile_number" placeholder="Enter Mobile Number" required>
            <input type="submit" value="Get SIM Provider">
        </form>
        {% if sim_provider %}
            <div class="result">The SIM provider for {{ mobile_number }} is: <strong>{{ sim_provider }}</strong></div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    sim_provider = None
    mobile_number = None
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        sim_provider = get_sim_provider(mobile_number)
    return render_template_string(HTML_TEMPLATE, sim_provider=sim_provider, mobile_number=mobile_number)

if __name__ == '__main__':
    app.run(debug=True)
