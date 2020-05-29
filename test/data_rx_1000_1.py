#!/home/koenvs/anaconda/bin/python3

import re

f = open("safeled_debug_app/test/data_rx_1000_1", "r")

THRESHOLD_LEVEL = 8

bit_array = []
strength_array_1 = []
strength_array_0 = []
noise_array = []
for line in f:
    if line.startswith("Receiving"):
        continue
    if any("/"):
        line.rstrip()
        temp = line.split(" ")
        for x in temp:
            if re.search(r"[0-1]/.", x):
                y = x.split("/")
                if int(y[1]) < THRESHOLD_LEVEL:
                    noise_array.append(int(y[1]))
                else:
                    bit_array.append(int(y[0]))
                    if y[0] == "0":
                        strength_array_0.append(int(y[1]))
                    elif y[0] == "1":
                        strength_array_1.append(int(y[1]))
                    else:
                        continue

# print(bit_array)
# print(strength_array_0)
# print(strength_array_1)
# print(noise_array)

average = lambda a: round(sum(a)/len(a), 1)
avg_0 = average(strength_array_0)
avg_1 = average(strength_array_1)
avg_noise = average(noise_array)
cnt_0 = bit_array.count(0)
cnt_1 = bit_array.count(1)
max_0 = max(strength_array_0)
max_1 = max(strength_array_1)
print(avg_0, cnt_0, max_0)
print(avg_1, cnt_1, max_1)
print(avg_noise)

