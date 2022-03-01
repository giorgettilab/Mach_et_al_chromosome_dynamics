import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd

data = []
for i in range(10):
    data.append(np.loadtxt(f"{sys.argv[1]}/{i}/mytraj.lammpstrj_msd_a_fft.dat"))
avd = np.mean(data, axis=0)
np.savetxt(f"{sys.argv[1]}/joint_msd.dat", avd)
