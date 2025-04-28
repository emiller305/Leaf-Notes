# Set up SQLite database
def create_database():
    conn = sqlite3.connect('adc_data.db')  # Database file
    c = conn.cursor()
    
    # Create table for ADC data if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS adc_readings (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                     adc_value INTEGER
                 )''')
    conn.commit()
    conn.close()

# Function to read ADC value (replace with actual ADC read code)
def read_adc():
    # Pseudocode for reading ADC value
    # adc_value = adc.read(channel)  # Replace with actual ADC reading code
    adc_value = 512  # Example value, replace with actual ADC value
    return adc_value

# Function to log ADC data into the SQLite database
def log_adc_data():
    adc_value = read_adc()  # Get the latest ADC value
    if adc_value is not None:
        conn = sqlite3.connect('adc_data.db')
        c = conn.cursor()
        
        # Insert the ADC value into the database
        c.execute("INSERT INTO adc_readings (adc_value) VALUES (?)", (adc_value,))
        
        conn.commit()  # Save the data
        conn.close()
        print(f"Logged ADC value: {adc_value}")
    else:
        print("Failed to read ADC data")

# Main function to continuously log data
def main():
    while True:
        log_adc_data()
        time.sleep(1)  # Adjust the interval (in seconds) as needed

if __name__ == "__main__":
    create_database()  # Ensure the database and table are created
    main()  # Start logging data
