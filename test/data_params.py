#!/home/koenvs/anaconda/bin/python3

f = open("safeled_debug_app/test/params_data")

side_a = []
side_b = []

for line in f:
    if line.startswith("Current"):
        continue
    elif line.startswith("A side"):
        t = line.split(",")
        for x in t:
            side_a.append(int(x.strip("Aside: "), 16))
    elif line.startswith("B side"):
        t = line.split(",")
        for x in t:
            side_b.append(int(x.strip("Bside: "), 16))

print(side_a)
print(side_b)
print(type(side_a[0]))