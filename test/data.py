#!/home/koenvs/anaconda3/bin/python3

x = open("safeled_debug_app/test/help_data", "r")
y = open("safeled_debug_app/test/putty.log", "r")

t = []
for line in x:
    a = []
    a = line.split('-')
    if len(a) >= 2:
        t.append(a[0].rstrip().lstrip())
print(t)