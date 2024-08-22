import sqlite3
from datetime import datetime, timedelta

# Function to format datetime objects to string
def format_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M')

# Function to generate unique bag tag numbers
def generate_bag_tag_numbers(start_number, count):
    return [f'0012345678{str(start_number + i).zfill(2)}' for i in range(count)]

# Function to generate PNRs
def generate_pnrs(start_char, count):
    pnrs = []
    for i in range(count):
        pnrs.append(f'{chr(start_char + i)}{chr(start_char + i)}{chr(start_char + i)}{str(100 + i)}')
    return pnrs

# Function to generate flight numbers
def generate_flight_numbers(airline_code_start, count):
    flight_numbers = []
    for i in range(count):
        airline_code = chr(airline_code_start + (i % 26)) + chr(airline_code_start + ((i + 1) % 26))
        flight_numbers.append(f'{airline_code}{str(100 + i)}')
    return flight_numbers

# Initialize data generation parameters
num_entries = 20
start_bag_tag_number = 90  # To generate bag tag numbers starting from '001234567890'
start_pnr_char = ord('A')  # To generate PNRs starting from 'AAA'
start_flight_number_char = ord('A')  # To generate flight numbers starting from 'AA'
passenger_names = [
    'John Smith', 'Jane Doe', 'Michael Johnson', 'Emily Davis', 'David Wilson',
    'Sarah Brown', 'Chris Lee', 'Amanda Garcia', 'Daniel Martinez', 'Laura Rodriguez',
    'James Anderson', 'Patricia Thomas', 'Robert Taylor', 'Linda Hernandez', 'Thomas Moore',
    'Barbara Jackson', 'Kevin Martin', 'Susan Thompson', 'Brian White', 'Karen Harris'
]
airports = ['JFK', 'LAX', 'ORD', 'DFW', 'DEN', 'SFO', 'LAS', 'MCO', 'SEA', 'CLT',
            'EWR', 'MIA', 'PHX', 'IAH', 'BOS', 'MSP', 'FLL', 'DTW', 'PHL', 'LGA']
terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4', 'Terminal 5',
             'Terminal A', 'Terminal B', 'Terminal C', 'Terminal D', 'Terminal E']
belt_numbers = list(range(1, 21))

# Generate data
bag_tag_numbers = generate_bag_tag_numbers(start_bag_tag_number, num_entries)
pnrs = generate_pnrs(start_pnr_char, num_entries)
flight_numbers = generate_flight_numbers(start_flight_number_char, num_entries)

# Initialize lists to hold data for each table
baggage_details = []
baggage_scanning = []
passenger_details = []

# Current date for reference
current_date = datetime(2024, 8, 15, 5, 0)  # Starting at Aug 15, 2024, 5:00 AM

for i in range(num_entries):
    bag_tag = bag_tag_numbers[i]
    pnr = pnrs[i]
    passenger_name = passenger_names[i]
    flight_number = flight_numbers[i]
    origin = airports[i % len(airports)]
    destination = airports[(i + 5) % len(airports)]
    layover = '-' if i % 4 != 0 else airports[(i + 10) % len(airports)]  # Every 4th bag has a layover
    check_in_time = current_date + timedelta(hours=i)
    bag_drop_location = terminals[i % len(terminals)]
    rush_bag = 'Yes' if i % 5 == 0 else 'No'  # Every 5th bag is a rush bag
    load_time = check_in_time + timedelta(minutes=45)
    unload_time = load_time + timedelta(hours=3)
    belt_number = belt_numbers[i % len(belt_numbers)]
    claim_status = 'Claimed' if i % 3 != 0 else 'Unclaimed'  # Every 3rd bag is unclaimed

    # Append to baggage_details
    baggage_details.append((
        bag_tag,
        pnr,
        flight_number,
        origin,
        destination,
        layover,
        format_datetime(check_in_time),
        bag_drop_location,
        rush_bag,
        format_datetime(load_time),
        format_datetime(unload_time),
        belt_number,
        claim_status
    ))

    # Scanning details
    scan_points = [
        ('Check-In Counter', check_in_time + timedelta(minutes=15), 'Checked In'),
        ('Security Checkpoint', check_in_time + timedelta(minutes=30), 'Cleared'),
        ('Loading Bay', load_time, 'Loaded')
    ]

    if layover != '-':
        layover_load_time = unload_time + timedelta(hours=2)
        scan_points.append(('Layover Loading Bay', layover_load_time, 'Loaded'))
        final_unload_time = layover_load_time + timedelta(hours=3)
    else:
        final_unload_time = unload_time + timedelta(hours=3)

    scan_points.append(('Unloading Bay', final_unload_time - timedelta(minutes=15), 'Unloaded'))
    scan_points.append(('Baggage Claim Area', final_unload_time, 'Ready for Claim'))

    for location, time, status in scan_points:
        baggage_scanning.append((
            bag_tag,
            location,
            format_datetime(time),
            status
        ))

    # Passenger details
    if rush_bag == 'Yes':
        # For rush bags, assign a different flight number for passenger
        passenger_flight_number = flight_numbers[(i + 1) % len(flight_numbers)]
    else:
        passenger_flight_number = flight_number

    passenger_details.append((
        bag_tag,
        pnr,
        passenger_name,
        passenger_flight_number
    ))

# Now, proceed to create the database and insert the data

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('baggage_tracking.db')
cursor = conn.cursor()

# Create the baggage_details table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS baggage_details (
        bag_tag_number TEXT PRIMARY KEY,
        pnr TEXT,
        flight_number TEXT,
        origin TEXT,
        destination TEXT,
        layover TEXT,
        check_in_time TEXT,
        bag_drop_location TEXT,
        rush_bag TEXT,
        load_time TEXT,
        unload_time TEXT,
        belt_number INTEGER,
        claim_status TEXT
    )
''')

# Create the baggage_scanning table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS baggage_scanning (
        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bag_tag_number TEXT,
        bag_scan_location TEXT,
        bag_scan_time TEXT,
        bag_status TEXT,
        FOREIGN KEY (bag_tag_number) REFERENCES baggage_details (bag_tag_number)
    )
''')

# Create the passenger_details table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passenger_details (
        passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bag_tag_number TEXT,
        pnr TEXT,
        passenger_name TEXT,
        passenger_flight_number TEXT,
        FOREIGN KEY (bag_tag_number) REFERENCES baggage_details (bag_tag_number)
    )
''')

# Insert data into baggage_details table
cursor.executemany('''
    INSERT INTO baggage_details (
        bag_tag_number, pnr, flight_number, origin, destination, layover,
        check_in_time, bag_drop_location, rush_bag, load_time, unload_time,
        belt_number, claim_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', baggage_details)

# Insert data into baggage_scanning table
cursor.executemany('''
    INSERT INTO baggage_scanning (
        bag_tag_number, bag_scan_location, bag_scan_time, bag_status
    ) VALUES (?, ?, ?, ?)
''', baggage_scanning)

# Insert data into passenger_details table
cursor.executemany('''
    INSERT INTO passenger_details (
        bag_tag_number, pnr, passenger_name, passenger_flight_number
    ) VALUES (?, ?, ?, ?)
''', passenger_details)

# Commit the transactions
conn.commit()

# Close the connection
conn.close()

print("Data inserted successfully into baggage_tracking.db")
