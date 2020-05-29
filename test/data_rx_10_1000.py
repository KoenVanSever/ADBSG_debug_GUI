#!/home/koenvs/anaconda/bin/python
#/usr/bin/python3

import re
import matplotlib.pyplot as plt

f = open("safeled_debug_app/test/data_rx_10_1000", "r")
adc_arr = []
for l in f:
    if re.search(r'.,.', l):
        adc_arr.append(l)
f.close()

adc_data_hf = []
adc_data_50 = []
for line in adc_arr:
    temp = line.split(",")
    temp2 = list(map(lambda x: int(x), temp))
    temp2.pop(len(temp2)-1)
    if len(temp2) > 400:
        adc_data_50.append(temp2)
    elif len(temp2) <= 400:
        adc_data_hf.append(temp2)

plt.plot(adc_data_hf[0])
plt.savefig("safeled_debug_app/test/test_image.png")
    
print(f"hf: {len(adc_data_hf)}")
print(f"50: {len(adc_data_50)}")
