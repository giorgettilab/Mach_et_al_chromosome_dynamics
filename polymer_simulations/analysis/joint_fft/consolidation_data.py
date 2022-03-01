import numpy as np
import pandas as pd
import glob
import sys


def msd_slope(path):
    msd = np.loadtxt(path)
    slope1, d1 = np.polyfit(
        np.log10(msd[:11, 0] * 4.76), np.log10(msd[:11, 1] * (0.095) ** 2), 1
    )
    slope2, d2 = np.polyfit(
        np.log10(msd[300:500, 0] * 4.76), np.log10(msd[300:500, 1] * (0.095) ** 2), 1
    )
    return slope1, 10 ** d1, slope2, 10 ** d2


def pc_slope(path):
    pc = pd.read_csv(path)
    temp_lim = pc.count()["aver"]
    slope_aver, _ = np.polyfit(
        np.log10(pc["aver_x"].values[:temp_lim]),
        np.log10(pc["aver"].values[:temp_lim]),
        1,
    )
    return slope_aver


def aver_dist(path):
    ad = pd.read_csv(path)
    d_ctcf_w = np.average(ad["bins"].values, weights=ad["ctcf"].values)
    return d_ctcf_w


def aver_amount_loops(path):
    a = np.loadtxt(path, skiprows=3000, max_rows=5000)
    if len(a) == 5000:
        return a.mean(axis=0)[-1]
    else:
        return 0


def main():
    joint_data = pd.DataFrame(
        columns=[
            "ctcf",
            "extruder_speed",
            "loading_rate",
            "unloading_rate",
            "msd_alpha1",
            "msd_D1",
            "msd_alpha2",
            "msd_D2",
            "pc_slope_aver",
            "dsts_ctcf",
            "num_loops",
        ]
    )
    p1 = sys.argv[1]
    paths = glob.glob(p1 + "/*/*/*/*/")
    for path in paths:
        print(path)
        msd_a1, msd_d1, msd_a2, msd_d2, pc_aver, d_ctcf = 0, 0, 0, 0, 0, 0
        path_msd = path + "/joint_msd.dat"
        path_pc = path + "/pc_aver.zip"
        path_dsts = path + "/hist_dists.zip"
        path_num_loops = glob.glob(path + "/9/*.o*")[-1]
        a = path.split("/")
        if glob.glob(path_msd):
            msd_a1, msd_d1, msd_a2, msd_d2 = msd_slope(path_msd)
        if glob.glob(path_pc):
            pc_aver = pc_slope(path_pc)

        if glob.glob(path_dsts):
            d_ctcf = aver_dist(path_dsts)
        num_loops = aver_amount_loops(path_num_loops)
        print(a)
        s2 = {
            "ctcf": a[-5],  # ++++++++++++++++++++++++++++++++++
            "extruder_speed": float(a[-4]),  # ++++++++++++++++++++++++++++++++++
            "loading_rate": float(a[-3]),  # ++++++++++++++++++++++++++++++++++
            "unloading_rate": float(a[-2]),  # ++++++++++++++++++++++++++++++++++
            "msd_alpha1": msd_a1,  # ++++++++++++++++++++++++++++++++++
            "msd_D1": msd_d1,  # ++++++++++++++++++++++++++++++++++
            "msd_alpha2": msd_a2,  # ++++++++++++++++++++++++++++++++++
            "msd_D2": msd_d2,  # ++++++++++++++++++++++++++++++++++
            "pc_slope_aver": pc_aver,  # ++++++++++++++++++++++++++++++++++
            "dsts_ctcf": d_ctcf,  # ++++++++++++++++++++++++++++++++++
            "num_loops": num_loops,  # ++++++++++++++++++++++++++++++++++
        }
        joint_data = joint_data.append(s2, ignore_index=True)
    joint_data.to_csv(sys.argv[1] + "consolidation.zip", index=False, compression="zip")


if __name__ == "__main__":
    main()
