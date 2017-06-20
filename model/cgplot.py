import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

lines = list(open("jho1.dat"))
lines = lines[1:]
x = []
y = []
for i, l in enumerate(lines):
    lines[i] = l.split("\n")[0]
    test = lines[i].split(" ")
    datax = 1
    for t in test:
        if not t == "":
            if datax == 1:
                x.append(float(t))
                datax = 2
            else:
                y.append(float(t))


fig, ax = plt.subplots()
ax.plot(x, y)
ax.plot(0.75938, 0, "o", label="CG")
ax.plot(0.86218, 0, "o", label="Neutral Point")
ax.set_ylim([-0.5, 0.5])
ax.set_xlim([0, 1])
ax.grid()
ax.legend(numpoints=1)
fig.savefig("cgaft.jpg")

fig, ax = plt.subplots()
ax.plot(x, y)
ax.plot(0.57325, 0, "o", label="CG")
ax.plot(0.86218, 0, "o", label="Neutral Point")
ax.set_ylim([-0.5, 0.5])
ax.set_xlim([0, 1])
ax.grid()
ax.legend(numpoints=1)
fig.savefig("cgfwd.jpg")
