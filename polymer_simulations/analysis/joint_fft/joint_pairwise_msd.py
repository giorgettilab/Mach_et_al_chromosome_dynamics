import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd

data = []
for i in range(10):
    data.append(
        np.loadtxt(f"{sys.argv[1]}/{i}/dst_bnd.dat_msd_pairwise_fft.dat", skiprows=1)
    )
print(data)
avd = np.mean(data, axis=0)
np.savetxt(f"{sys.argv[1]}/joint_pairwise_msd.dat", avd)
