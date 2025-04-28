import csv
import matplotlib.pyplot as plt
import numpy as np

def load_and_average_with_offset(csv_file, min_sample_id, max_sample_id=None, chunk_size=5000, vertical_offset=0):
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
                    if not max_sample_id or sample_id < max_sample_id:
                        x_raw.append(sample_id/64)
                        y_raw.append(value)
            except Exception as e:
                print(f"Skipping row due to error: {e}")

    # Center the signal
    mean_y = np.mean(y_raw)
    y_raw = [v - mean_y for v in y_raw]

    x_avg = []
    y_avg = []
    for i in range(0, len(y_raw), chunk_size):
        chunk_x = x_raw[i:i+chunk_size]
        chunk_y = y_raw[i:i+chunk_size]
        if len(chunk_y) == chunk_size:
            x_avg.append(np.mean(chunk_x))
            y_avg.append(np.mean(chunk_y) + vertical_offset)

    return x_avg, y_avg

# Use sample ID filters for both
x, y = load_and_average_with_offset('new_circ_overnight_watered.csv', min_sample_id=12000, max_sample_id= 1.6e6,vertical_offset=0.00015)
x2, y2 = load_and_average_with_offset('overnight2_watered.csv', min_sample_id=7000, max_sample_id= 1.6e6, vertical_offset=0.0001)
x3, y3 = load_and_average_with_offset('overnight3_watered.csv', min_sample_id=10, max_sample_id= 1.6e6, vertical_offset=0.00005)
#x4, y4 = load_and_average_with_offset('data_overnight_2.csv', min_sample_id=0, vertical_offset=0.03)
#x5, y5 = load_and_average_with_offset('test_output.csv', min_sample_id=100000, vertical_offset=0.04)

plt.figure(figsize=(12, 6))
plt.plot(x, y, label='Day 1 After Watering', color='green')
coeffs = np.polyfit(x, y, 1)
trendline = np.poly1d(coeffs)
plt.plot(x, trendline(x), linestyle='--', color='green')

plt.plot(x2, y2, label='Day 2 After Watering', color='orange')
coeffs = np.polyfit(x2, y2, 1)
trendline = np.poly1d(coeffs)
plt.plot(x2, trendline(x2), linestyle='--', color='orange')

plt.plot(x3, y3, label='Day 3 After Watering', color='blue')
coeffs = np.polyfit(x3, y3, 1)
trendline = np.poly1d(coeffs)
plt.plot(x3, trendline(x3), linestyle='--', color='blue')
#plt.plot(x4, y4, label='second overnight no watering (avg)', color='red')
#plt.plot(x5, y5, label='first overnight no watering (avg)', color='purple')
plt.title('Averaged Plant Signals After Watering (5000-Sample Averaged Window)')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
