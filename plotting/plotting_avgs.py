import csv
import matplotlib.pyplot as plt
import numpy as np

def load_and_average_by_sample_id(csv_file, min_sample_id, chunk_size=5000):
    x_raw = []
    y_raw = []
    
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                sample_id = int(row[0])
                value = float(row[2])
                if sample_id > min_sample_id:
                    x_raw.append(sample_id/64)
                    y_raw.append(value)
            except Exception as e:
                print(f"Skipping row due to error: {e}")
    
    x_avg = []
    y_avg = []
    for i in range(0, len(y_raw), chunk_size):
        chunk_x = x_raw[i:i+chunk_size]
        chunk_y = y_raw[i:i+chunk_size]
        if len(chunk_y) == chunk_size:
            x_avg.append(np.mean(chunk_x))
            y_avg.append(np.mean(chunk_y))
    
    return x_avg, y_avg

# Stim Data
# x, y = load_and_average_by_sample_id('./data/new_circ_256_w_stim.csv', min_sample_id=500)
#x2, y2 = load_and_average_by_sample_id('./data/new_circ_256_w_stim.csv', min_sample_id=500)

x, y = load_and_average_by_sample_id('new_circ_overnight_watered.csv', min_sample_id=12000)
x2, y2 = load_and_average_by_sample_id('overnight2_watered.csv', min_sample_id=7000)
x3, y3 = load_and_average_by_sample_id('overnight3_watered.csv', min_sample_id=10)
#x4, y4 = load_and_average_by_sample_id('data_overnight_2.csv', min_sample_id=0)
#x5, y5 = load_and_average_by_sample_id('test_output.csv', min_sample_id=6000)

plt.figure(figsize=(12, 6))
#plt.plot(x, y, color='green')
#plt.plot(x2, y2, label='Plant Signal With Stimulus 2', color='orange')

plt.plot(x, y, label='first overnight watered (avg)', color='green')
plt.plot(x2, y2, label='second overnight watered (avg)', color='orange')
plt.plot(x3, y3, label='third overnight watered (avg)', color='blue')
#plt.plot(x4, y4, label='overnight no watering (avg)', color='red')
#plt.plot(x5, y5, label='overnight no watering (avg)', color='purple')
plt.title('Plant Signal With Stimulus')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
