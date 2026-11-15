import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

# ---------- Day 1: meet the two-electrode data ----------
data = loadmat("data/ECoG-1.mat")
print(data.keys())                 # see which variables the file holds

E1 = data["E1"]                    # electrode 1, shape (trials, samples)
E2 = data["E2"]                    # electrode 2, same shape
t = data["t"].reshape(-1)          # time in seconds, flattened to 1-D

print(E1.shape, E2.shape, t.shape)

dt = t[1] - t[0]
fs = 1 / dt
K = E1.shape[0]                    # number of trials (rows)
N = E1.shape[1]                    # samples per trial (columns)
T = N * dt

print(f"K = {K} trials, N = {N} samples, dt = {dt} s, fs = {fs:.0f} Hz, T = {T:.2f} s")

plt.show()
