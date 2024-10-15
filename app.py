from flask import Flask, render_template_string, request
import requests
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('search_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile_number TEXT,
            carrier TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Get SIM provider function
def get_sim_provider(mobile_number):
    access_key = '0bcbac976cd60ea1a2947e605ab471f8'  # Replace with your actual access key
    url = f'http://apilayer.net/api/validate?access_key={access_key}&number={mobile_number}&country_code=IN'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if data['valid']:
            return data['carrier']  # This returns the SIM provider
        else:
            return "Invalid mobile number"
    else:
        return "Error: Unable to fetch data"

# Route to handle the form and result
@app.route('/', methods=['GET', 'POST'])
def index():
    sim_provider = ''
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        sim_provider = get_sim_provider(mobile_number)
        
        # Store the search in the database
        if sim_provider not in ["Invalid mobile number", "Error: Unable to fetch data"]:
            conn = sqlite3.connect('search_history.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO search_history (mobile_number, carrier) VALUES (?, ?)', (mobile_number, sim_provider))
            conn.commit()
            conn.close()
    
    return render_template_string(INDEX_HTML, sim_provider=sim_provider)

# Route to display the search history (for admin only)
@app.route('/history')
def history():
    conn = sqlite3.connect('search_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM search_history')
    searches = cursor.fetchall()
    conn.close()
    return render_template_string(HISTORY_HTML, searches=searches)

# HTML template for the main page
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIM Provider Lookup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        input[type="text"] {
            padding: 10px;
            margin: 10px 0;
            width: 300px;
            border: none;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background: #ff4081;
            color: white;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Find Your SIM Provider</h1>
        <form method="POST">
            <input type="text" name="mobile_number" placeholder="Enter mobile number" required>
            <button type="submit">Get SIM Provider</button>
        </form>
        {% if sim_provider %}
            <div class="result">
                <h2>The SIM provider is: <span>{{ sim_provider }}</span></h2>
            </div>
        {% endif %}
        <a href="/history" style="color: white; text-decoration: underline;">View Search History</a>
    </div>
</body>
</html>
'''

# HTML template for the history page
HISTORY_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search History</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid white;
        }
        th {
            background-color: rgba(255, 255, 255, 0.2);
        }
        a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search History</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Mobile Number</th>
                <th>SIM Provider</th>
            </tr>
            {% for search in searches %}
            <tr>
                <td>{{ search[0] }}</td>
                <td>{{ search[1] }}</td>
                <td>{{ search[2] }}</td>
            </tr>
            {% endfor %}
        </table>
        <a href="/">Back to Search</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
