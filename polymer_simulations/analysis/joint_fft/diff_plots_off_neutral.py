import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import numpy as np
import argparse
import matplotlib as mpl
import matplotlib.ticker as tkr

formatter = tkr.ScalarFormatter(useMathText=True)
formatter.set_scientific(False)
mpl.rcParams["pdf.fonttype"] = 42

parser = argparse.ArgumentParser(
    description="Plot the difference between the off- and neutral-state data."
)
parser.add_argument(
    "-i1", "--input1", help="Consolidation zip of on/off cases", required=True
)
parser.add_argument(
    "-i2", "--input2", help="Consolidation zip of naked chain", required=True
)
parser.add_argument("-o", "--output", help="Output directory", required=True)
parser.add_argument("-s", "--speed", help="Speed of the chain", type=int, default=17500)
parser.add_argument(
    "-nd",
    "--no_distances",
    help="Ignore distances, i.e. realistic data",
    type=bool,
    default=False,
)
args = parser.parse_args()
print(args)
df = pd.read_csv(args.input1)

df2 = pd.read_csv(args.input2)

for var in [
    "msd_alpha1",
    "msd_D1",
    "msd_alpha2",
    "msd_D2",
    "pc_slope_aver",
    "dsts_ctcf",
]:
    if args.no_distances and var == "dsts_ctcf":
        continue
    if "msd_alpha" in var:
        bot_lim = 0.6
        top_lim = 1 / bot_lim
        log_flag = True
    elif "msd_D" in var:
        bot_lim = 0.6
        top_lim = 1 / bot_lim
        log_flag = True
    elif "pc_slope" in var:
        bot_lim = 0.6
        top_lim = 1.4
        log_flag = False
    elif "dsts" in var:
        bot_lim = 0.5
        top_lim = 1.5
        log_flag = False

    for extruder_speed in [args.speed]:
        subdf = df[(df.ctcf == "off") & (df.extruder_speed == extruder_speed)]
        if subdf.empty:
            continue
        print(var)
        data_off = subdf[
            (subdf.ctcf == "off")
            & (subdf.loading_rate > 0.00001)
            & (subdf.unloading_rate < 1.1)
        ].pivot("loading_rate", "unloading_rate", var)
        data_neutral = df2.pivot("loading_rate", "unloading_rate", var).values
        plt.figure()
        if log_flag:
            ax = sns.heatmap(
                np.divide(
                    data_off,
                    data_neutral,
                    out=np.zeros_like(data_off),
                    where=data_neutral != 0,
                ),
                annot=True,
                fmt=".2f",
                norm=LogNorm(vmin=bot_lim, vmax=top_lim),
                square=True,
                cmap="coolwarm",
                cbar_kws={
                    "label": var,
                    "ticks": [bot_lim, 1, top_lim],
                    "format": formatter,
                },
            )
            ax.collections[0].colorbar.ax.yaxis.set_ticks([], minor=True)
        else:
            print(data_off)
            print(data_neutral)
            sns.heatmap(
                np.divide(
                    data_off,
                    data_neutral,
                    out=np.zeros_like(data_off),
                    where=data_neutral != 0,
                ),
                annot=True,
                vmin=bot_lim,
                vmax=top_lim,
                cmap="coolwarm",
                cbar_kws={"label": var},
            )

        plt.title(f"Differential plot [off/naked], extruder speed {extruder_speed}")
        print(args.output + f"/diff_off_w_neutral_{extruder_speed}_{var}.pdf")
        plt.savefig(args.output + f"/diff_off_w_neutral_{extruder_speed}_{var}.pdf")
        plt.close()
