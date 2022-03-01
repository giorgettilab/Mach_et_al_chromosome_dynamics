import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import sys
import pandas as pd
import scipy.stats as ss
import itertools


def distr_bursts(arr, rc_min: int = 1, rc_max: int = 4):
    """
    Calculate distribution of bursts considering contact within rc
    Inputs:
        arr - 1D array of floats: distances, order=time
        rc - float: cutting radius
    Outputs:
        distr - 1D arrays of ints: every subarr corresponds to a specific rc and
        every value corresponds to the contact duration
    """
    start_flag_2 = False
    start_flag_1 = False
    start_flag_0 = False
    rcs = np.arange(rc_min, rc_max)
    distr = [[] for _ in range(len(rcs))]
    list_streaks = np.zeros(len(rcs))
    for i in arr:
        if not start_flag_2 and i > rcs[2]:
            start_flag_2 = True
            start_flag_1 = True
            start_flag_0 = True
            list_streaks[2] = 0
            list_streaks[1] = 0
            list_streaks[0] = 0
        elif not start_flag_1 and i > rcs[1]:
            start_flag_1 = True
            start_flag_0 = True
            list_streaks[1] = 0
            list_streaks[0] = 0
        elif not start_flag_0 and i > rcs[0]:
            start_flag_0 = True
            list_streaks[0] = 0

        if i < rcs[0]:
            list_streaks += 1
        elif i < rcs[1]:
            list_streaks[1:] += 1
            if list_streaks[0] > 0 and start_flag_0:
                distr[0].append(list_streaks[0])
                list_streaks[0] = 0
        elif i < rcs[2]:
            list_streaks[2] += 1
            if list_streaks[0] > 0 and start_flag_0:
                distr[0].append(list_streaks[0])
                list_streaks[0] = 0
            if list_streaks[1] > 0 and start_flag_1:
                distr[1].append(list_streaks[1])
                list_streaks[1] = 0
        else:
            if list_streaks[0] > 0 and start_flag_0:
                distr[0].append(list_streaks[0])
                list_streaks[0] = 0
            if list_streaks[1] > 0 and start_flag_1:
                distr[1].append(list_streaks[1])
                list_streaks[1] = 0
            if list_streaks[2] > 0 and start_flag_2:
                distr[2].append(list_streaks[2])
                list_streaks[2] = 0

    return distr


def distr_passage_time(arr, rc_min: int = 1, rc_max: int = 4):
    """
    Calculate distribution of bursts considering contact within rc
    Inputs:
        arr - 1D array of floats: distances, order=time
        rc - float: cutting radius
    Outputs:
        distr - 1D arrays of ints: every subarr corresponds to a specific rc and
        every value corresponds to the contact duration
    """
    start_flag_2 = False
    start_flag_1 = False
    start_flag_0 = False
    rcs = np.arange(rc_min, rc_max)
    distr = [[] for _ in range(len(rcs))]
    list_streaks = np.zeros(len(rcs))
    for i in arr:
        if not start_flag_0 and i < rcs[0]:
            start_flag_2 = True
            start_flag_1 = True
            start_flag_0 = True
            list_streaks[2] = 0
            list_streaks[1] = 0
            list_streaks[0] = 0
        elif not start_flag_1 and i < rcs[1]:
            start_flag_1 = True
            start_flag_2 = True
            list_streaks[1] = 0
            list_streaks[2] = 0
        elif not start_flag_2 and i < rcs[2]:
            start_flag_2 = True
            list_streaks[2] = 0

        if i > rcs[2]:
            list_streaks += 1
        elif i > rcs[1]:
            list_streaks[:2] += 1
            if list_streaks[2] > 0 and start_flag_2:
                distr[2].append(list_streaks[2])
                list_streaks[2] = 0
        elif i > rcs[0]:
            list_streaks[0] += 1
            if list_streaks[2] > 0 and start_flag_2:
                distr[2].append(list_streaks[2])
                list_streaks[2] = 0
            if list_streaks[1] > 0 and start_flag_1:
                distr[1].append(list_streaks[1])
                list_streaks[1] = 0
        else:
            if list_streaks[0] > 0 and start_flag_0:
                distr[0].append(list_streaks[0])
                list_streaks[0] = 0
            if list_streaks[1] > 0 and start_flag_1:
                distr[1].append(list_streaks[1])
                list_streaks[1] = 0
            if list_streaks[2] > 0 and start_flag_2:
                distr[2].append(list_streaks[2])
                list_streaks[2] = 0

    return distr


def ks2_all(arr: list, num: int):
    st_pv = []
    for i in range(int):
        for j in range(i, 16):
            st, pv = stats.ks_2samp(outside[i], outside[j])
            st_pv.append([st, pv])
            print("KS test between ", i, j, " stat=", st, " p-value=", pv)
    return st_pv


def three_tests(a, b):
    stat, p_Student = ss.ttest_ind(a, b)
    stat, p_MW = ss.mannwhitneyu(a, b)
    stat, p_KS = ss.ks_2samp(a, b)
    return p_Student, p_MW, p_KS


def msd_1d(arr):
    res = np.zeros((len(arr) - 1, 2))
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            res[j - i - 1, 0] += (arr[j] - arr[i]) ** 2
            res[j - i - 1, 1] += 1
    return res[:, 0] / res[:, 1]


def main():
    d = []
    for i in range(10):
        print(f"{sys.argv[1]}/{i}/dst_bnd.dat")
        data = np.loadtxt(f"{sys.argv[1]}/{i}/dst_bnd.dat", skiprows=1)
        data = data.T
        d.append(data[0])

    ctcf = d
    plt.figure(figsize=(8, 6))
    for i in range(10):
        h, b = np.histogram(ctcf[i], bins=50, range=(0, 12))
        if i == 0:
            ctcf2out = h
        else:
            ctcf2out += h
        plt.plot((b[:-1] + b[1:]) / 2, h, label=str(i))
    plt.title("Between CTCFs")
    plt.xlabel("Distance, a.u.")
    plt.ylabel("Count")
    plt.legend()
    plt.savefig(sys.argv[1] + "hist_single_reps_ctcf.pdf", dpi=300)
    plt.clf()
    data2out = pd.DataFrame()
    data2out = data2out.assign(bins=(b[:-1] + b[1:]) / 2)
    data2out = data2out.assign(ctcf=ctcf2out)
    data2out.to_csv(sys.argv[1] + "hist_dists.zip", index=False, compression="zip")
    sys.exit()


if __name__ == "__main__":
    main()
