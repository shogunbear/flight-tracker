from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import json
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Configuration
class Config:
    # Get API key from environment variable or use a default for development
    AVIATION_STACK_API_KEY = os.environ.get('AVIATION_STACK_API_KEY', '469f1ae884f8e4eb3ad55b63fb41ba03')
    AVIATION_STACK_API_URL = "http://api.aviationstack.com/v1/flights"
    
    # For demo purposes, we'll use a mock data file if no API key is provided
    USE_MOCK_DATA = True if not AVIATION_STACK_API_KEY or AVIATION_STACK_API_KEY == "YOUR_AVIATION_STACK_API_KEY" else False
    MOCK_DATA_FILE = "mock_flight_data.json"

app.config.from_object(Config)

# User database - In a production environment, use a real database
users = {
    'david': {
        'password': generate_password_hash('password'),
        'name': 'David'
    }
}

# Helper functions
def get_flight_data(origin_country="US", destination_country="GB", limit=100):
    """
    Fetch flight data from Aviation Stack API or use mock data
    """
    if app.config["USE_MOCK_DATA"]:
        return get_mock_flight_data()
    
    params = {
        'access_key': app.config["AVIATION_STACK_API_KEY"],
        'limit': limit
    }
    
    # Add filters for flights between USA and Europe
    if origin_country:
        params['dep_iata'] = origin_country
    if destination_country:
        params['arr_iata'] = destination_country
        
    response = requests.get(app.config["AVIATION_STACK_API_URL"], params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        # If API call fails, use mock data as fallback
        return get_mock_flight_data()

def get_mock_flight_data():
    """
    Load mock flight data from JSON file or create if it doesn't exist
    """
    mock_file_path = os.path.join(os.path.dirname(__file__), app.config["MOCK_DATA_FILE"])
    
    if os.path.exists(mock_file_path):
        with open(mock_file_path, 'r') as file:
            return json.load(file)
    else:
        # Create mock data if file doesn't exist
        mock_data = generate_mock_flight_data()
        with open(mock_file_path, 'w') as file:
            json.dump(mock_data, file, indent=4)
        return mock_data

def generate_mock_flight_data():
    """
    Generate realistic mock flight data for demo purposes
    """
    us_airports = [
        {"iata": "JFK", "name": "John F. Kennedy International Airport", "city": "New York"},
        {"iata": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles"},
        {"iata": "ORD", "name": "O'Hare International Airport", "city": "Chicago"},
        {"iata": "MIA", "name": "Miami International Airport", "city": "Miami"},
        {"iata": "BOS", "name": "Boston Logan International Airport", "city": "Boston"}
    ]
    
    eu_airports = [
        {"iata": "LHR", "name": "Heathrow Airport", "city": "London", "country": "United Kingdom"},
        {"iata": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
        {"iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
        {"iata": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
        {"iata": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"}
    ]
    
    airlines = [
        {"name": "American Airlines", "iata": "AA"},
        {"name": "United Airlines", "iata": "UA"},
        {"name": "Delta Air Lines", "iata": "DL"},
        {"name": "British Airways", "iata": "BA"},
        {"name": "Lufthansa", "iata": "LH"},
        {"name": "Air France", "iata": "AF"},
        {"name": "KLM", "iata": "KL"}
    ]
    
    flight_statuses = ["scheduled", "active", "landed", "cancelled", "diverted"]
    
    # Generate flights
    flights = []
    now = datetime.now()
    
    # US to Europe flights
    for _ in range(30):
        dep_airport = us_airports[_ % len(us_airports)]
        arr_airport = eu_airports[_ % len(eu_airports)]
        airline = airlines[_ % len(airlines)]
        
        # Generate departure time within next 48 hours
        dep_time = (now + timedelta(hours=(_ * 3) % 48)).strftime("%Y-%m-%dT%H:%M:%S%z")
        arr_time = (now + timedelta(hours=((_ * 3) % 48) + 8)).strftime("%Y-%m-%dT%H:%M:%S%z")
        
        flight_number = f"{airline['iata']}{100 + _ % 900}"
        status = flight_statuses[_ % len(flight_statuses)]
        
        flight = {
            "flight": {
                "number": flight_number,
                "iata": flight_number,
                "icao": f"{airline['iata']}{100 + _ % 900}",
                "codeshared": None
            },
            "airline": {
                "name": airline["name"],
                "iata": airline["iata"],
                "icao": airline["iata"] + "A"
            },
            "departure": {
                "airport": dep_airport["name"],
                "timezone": "America/New_York",
                "iata": dep_airport["iata"],
                "icao": "K" + dep_airport["iata"],
                "terminal": str(1 + _ % 5),
                "gate": f"{chr(65 + _ % 20)}{_ % 10}",
                "scheduled": dep_time,
                "estimated": dep_time,
                "actual": None,
                "estimated_runway": None,
                "actual_runway": None
            },
            "arrival": {
                "airport": arr_airport["name"],
                "timezone": "Europe/London",
                "iata": arr_airport["iata"],
                "icao": "E" + arr_airport["iata"],
                "terminal": str(1 + (_ + 1) % 5),
                "gate": f"{chr(65 + (_ + 1) % 20)}{(_ + 1) % 10}",
                "baggage": str((_ % 5) + 1),
                "scheduled": arr_time,
                "estimated": arr_time,
                "actual": None,
                "estimated_runway": None,
                "actual_runway": None
            },
            "flight_status": status,
            "flight_duration": 480,  # 8 hours in minutes
            "departure_city": dep_airport["city"],
            "arrival_city": arr_airport["city"],
            "arrival_country": arr_airport["country"]
        }
        
        flights.append(flight)
    
    # Europe to US flights
    for _ in range(30):
        dep_airport = eu_airports[_ % len(eu_airports)]
        arr_airport = us_airports[_ % len(us_airports)]
        airline = airlines[_ % len(airlines)]
        
        # Generate departure time within next 48 hours
        dep_time = (now + timedelta(hours=(_ * 3) % 48)).strftime("%Y-%m-%dT%H:%M:%S%z")
        arr_time = (now + timedelta(hours=((_ * 3) % 48) + 9)).strftime("%Y-%m-%dT%H:%M:%S%z")
        
        flight_number = f"{airline['iata']}{500 + _ % 500}"
        status = flight_statuses[_ % len(flight_statuses)]
        
        flight = {
            "flight": {
                "number": flight_number,
                "iata": flight_number,
                "icao": f"{airline['iata']}{500 + _ % 500}",
                "codeshared": None
            },
            "airline": {
                "name": airline["name"],
                "iata": airline["iata"],
                "icao": airline["iata"] + "A"
            },
            "departure": {
                "airport": dep_airport["name"],
                "timezone": "Europe/London",
                "iata": dep_airport["iata"],
                "icao": "E" + dep_airport["iata"],
                "terminal": str(1 + _ % 5),
                "gate": f"{chr(65 + _ % 20)}{_ % 10}",
                "scheduled": dep_time,
                "estimated": dep_time,
                "actual": None,
                "estimated_runway": None,
                "actual_runway": None
            },
            "arrival": {
                "airport": arr_airport["name"],
                "timezone": "America/New_York",
                "iata": arr_airport["iata"],
                "icao": "K" + arr_airport["iata"],
                "terminal": str(1 + (_ + 1) % 5),
                "gate": f"{chr(65 + (_ + 1) % 20)}{(_ + 1) % 10}",
                "baggage": str((_ % 5) + 1),
                "scheduled": arr_time,
                "estimated": arr_time,
                "actual": None,
                "estimated_runway": None,
                "actual_runway": None
            },
            "flight_status": status,
            "flight_duration": 540,  # 9 hours in minutes
            "departure_city": dep_airport["city"],
            "departure_country": dep_airport["country"],
            "arrival_city": arr_airport["city"]
        }
        
        flights.append(flight)
    
    return {"data": flights}

# Authentication middleware
def login_required(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['user_id'] = username
            session['user_name'] = users[username]['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_name=session.get('user_name'))

@app.route('/flights')
@login_required
def flights():
    # Get query parameters
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    airline = request.args.get('airline', '')
    status = request.args.get('status', '')
    
    # Get flight data
    flight_data = get_flight_data()
    
    # Filter flight data based on query parameters
    filtered_flights = flight_data['data']
    
    if origin:
        filtered_flights = [f for f in filtered_flights if origin.upper() in (
            f['departure']['iata'], 
            f['departure_city'].upper() if 'departure_city' in f else ''
        )]
    
    if destination:
        filtered_flights = [f for f in filtered_flights if destination.upper() in (
            f['arrival']['iata'], 
            f['arrival_city'].upper() if 'arrival_city' in f else ''
        )]
    
    if airline:
        filtered_flights = [f for f in filtered_flights if airline.upper() in (
            f['airline']['name'].upper(), 
            f['airline']['iata']
        )]
    
    if status:
        filtered_flights = [f for f in filtered_flights if status.lower() == f['flight_status'].lower()]
    
    return render_template('flights.html', flights=filtered_flights)

@app.route('/api/flights')
@login_required
def api_flights():
    # Get flight data
    flight_data = get_flight_data()
    
    # Get query parameters
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    airline = request.args.get('airline', '')
    status = request.args.get('status', '')
    
    # Filter flight data based on query parameters
    filtered_flights = flight_data['data']
    
    if origin:
        filtered_flights = [f for f in filtered_flights if origin.upper() in (
            f['departure']['iata'], 
            f['departure_city'].upper() if 'departure_city' in f else ''
        )]
    
    if destination:
        filtered_flights = [f for f in filtered_flights if destination.upper() in (
            f['arrival']['iata'], 
            f['arrival_city'].upper() if 'arrival_city' in f else ''
        )]
    
    if airline:
        filtered_flights = [f for f in filtered_flights if airline.upper() in (
            f['airline']['name'].upper(), 
            f['airline']['iata']
        )]
    
    if status:
        filtered_flights = [f for f in filtered_flights if status.lower() == f['flight_status'].lower()]
    
    return jsonify({"data": filtered_flights})

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
