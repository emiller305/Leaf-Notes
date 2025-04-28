import csv
import matplotlib.pyplot as plt

#csv_file = 'new_circ_overnight_watered.csv'
csv_file = 'test16.csv'
x = []  # sample number (id)
y = []  # adc_value

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue
        try:
            sample_id = int(row[0])
            value = float(row[2])
            #if value <= -0.009 and value > -0.012:  # filter out outliers
            if sample_id > 100:
                x.append(sample_id)
                y.append(value)
        except Exception as e:
            print(f"Skipping row due to error: {e}")
'''
x2 = []
y2 = []
csv_file = 'overnight2_watered.csv'
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue
        try:
            sample_id = int(row[0])
            value = float(row[2])
            #if value <= 0:  # filter out outliers
            if sample_id > 7000:
                x2.append(sample_id)
                y2.append(value)
        except Exception as e:
            print(f"Skipping row due to error: {e}")

x3 = []
y3 = []
csv_file = 'plant2_test9_stim.csv'
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue
        try:
            sample_id = int(row[0])
            value = float(row[2])
            #if value <= 0:  # filter out outliers
            if sample_id > 0:
                x3.append(sample_id)
                y3.append(value)
        except Exception as e:
            print(f"Skipping row due to error: {e}")
'''


plt.figure(figsize=(12, 6))
plt.plot(x, y, label='third overnight watered', color='green')
#plt.plot(x2, y2, label='second overnight watered', color='orange')
#plt.plot(x3, y3, label='first overnight watered', color='blue')
plt.title('ADC Values by Sample Number')
plt.xlabel('Sample ID')
plt.ylabel('ADC Value')
plt.grid(True)
plt.legend()
plt.tight_layout()
#plt.ylim(-1.0, 1)
plt.show()
