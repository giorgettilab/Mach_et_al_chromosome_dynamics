import numpy as np
import sys
import matplotlib.pyplot as plt
import pandas as pd
import argparse


def logbin(data_x, data_y, numdots=20, ptf="Deafault path"):
    """
    Replot data from linear space to logspace with evenly distributed dots.
    Inputs:
        data_x, data_y - arrays of x,y
        numdots - number of values on the future graph
    """

    newdata_y = []
    newdata_x = []
    distr = np.logspace(
        np.log10(min(data_x)), np.log10(max(data_x)), num=numdots * 2 + 1
    )
    for i in range(1, len(distr), 2):
        val = 0
        counter = 0
        for j in range(len(data_x)):
            if data_x[j] > distr[i - 1] and data_x[j] < distr[i + 1]:
                val += data_y[j]
                counter += 1
        if counter > 0:
            newdata_y.append(val / counter)
            newdata_x.append(distr[i])
    return newdata_x, newdata_y


def calc_pc(cm, myrange):
    pc = np.zeros((len(cm), 2))
    for i in range(myrange[0][0], myrange[0][1]):
        for j in range(myrange[1][0], myrange[1][1]):
            if j > i and cm[i, j] is not np.nan:
                pc[j - i, 1] += cm[i, j]
                pc[j - i, 0] += 1
    res = np.divide(
        pc[:, 1], pc[:, 0], out=np.zeros_like(pc[:, 1]), where=pc[:, 0] != 0
    )
    return res / max(res)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcualte log-binned contact probability"
    )
    parser.add_argument("-i", "--input", type=str, help="input file")
    parser.add_argument("-o", "--output", type=str, help="output file")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="dpi")
    parser.add_argument("-f", "--format", type=str, default="png", help="format")
    parser.add_argument("-lb", "--logbin", type=int, default=1, help="logbin")
    parser.add_argument("-n", "--num_bins", type=int, default=30, help="Number of bins")
    parser.add_argument(
        "-l",
        "--limits",
        nargs=2,
        metavar=("low_lim", "top_lim"),
        help="define window to calculate PC on chain",
    )
    return parser.parse_args()


def main():
    parsed = parse_args()
    cm = np.loadtxt(parsed.input)  # + "mytraj.lammpstrj_cm.dat")

    if parsed.limits is None:
        aver_range = [[0, 1000], [0, 1000]]
    else:
        low_lim = int(parsed.limits[0])
        top_lim = int(parsed.limits[1])
        aver_range = [
            [low_lim, top_lim],
            [low_lim, top_lim],
        ]
    aver = calc_pc(cm, aver_range)
    aver[aver == 0] = np.nan
    if parsed.logbin == 1:
        aver_x, aver_y = logbin(
            np.arange(1, len(aver)), aver[1:], numdots=parsed.num_bins
        )
    else:
        aver_x = np.arange(1, len(aver))
        aver_y = aver[1:]

    print("Pc path", parsed.input)

    hic_pc = pd.read_csv(
        "/tungstenfs/scratch/ggiorget/pavel/code_projects/systematic_chrodyn_simulations/bonev_track/Bonev.scaling.1kb.csv"
    )
    if parsed.logbin == 1:
        hic_x, hic_y = logbin(
            hic_pc["s_bp"].values / 1000,
            hic_pc["balanced.avg"].values / np.max(hic_pc["balanced.avg"].values),
            numdots=30,
        )
    else:
        hic_x = hic_pc["s_bp"].values / 1000
        hic_y = hic_pc["balanced.avg"].values / np.max(hic_pc["balanced.avg"].values)

    plt.figure(figsize=(10, 8))
    plt.plot(aver_x, aver_y / max(aver_y), label="average")
    plt.plot(hic_x, hic_y / max(hic_y), label="Bonev et.al. 2017")
    print(hic_x[:5], hic_y[:5])
    plt.xlabel("Genome distance, a.u. (8 Kb)")
    plt.ylabel("Contact probability")
    plt.legend()
    # if parsed.logbin == 1:
    plt.xscale("log")
    plt.yscale("log")
    if parsed.format == "png":
        plt.savefig(parsed.output + "pc_contact_prob.png", dpi=parsed.dpi)
    elif parsed.format == "pdf":
        plt.savefig(parsed.output + "pc_contact_prob.pdf")
    plt.close()

    data2out = pd.DataFrame()
    data2out["aver_x"] = aver_x
    data2out["aver"] = aver_y
    data2out.to_csv(
        parsed.output + "pc_in_out_across.zip", index=False, compression="zip"
    )


if __name__ == "__main__":
    main()
