import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import numpy as np
import argparse
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42
parser = argparse.ArgumentParser(
    description="Plot the difference between the off- and neutral-state data."
)
parser.add_argument(
    "-i", "--input", help="Consolidation zip of on/off cases", required=True
)
parser.add_argument("-o", "--output", help="Output file", required=True)
parser.add_argument(
    "-s", "--speed", help="Speed of the extruder", type=int, default=17500
)
args = parser.parse_args()
print(args)

df = pd.read_csv(args.input, compression="zip")

for var in [
    "msd_alpha1",
    "msd_D1",
    "msd_alpha2",
    "msd_D2",
    "pc_slope_aver",
    "dsts_ctcf",
]:
    if "msd_alpha" in var:
        bot_lim = 0.9
        top_lim = 1.1
        log_flag = False
    elif "msd_D" in var:
        bot_lim = 0.9
        top_lim = 1.1
        log_flag = False
    elif "pc_slope" in var:
        bot_lim = 0.6
        top_lim = 1.4
        log_flag = False
    elif "dsts" in var:
        bot_lim = 0.5
        top_lim = 1.5
        log_flag = False

    for extruder_speed in [args.speed]:
        subdf = df[(df.extruder_speed == extruder_speed)]
        if subdf.empty:
            continue
        data_on = subdf[(subdf.ctcf == "on")].pivot(
            "loading_rate", "unloading_rate", var
        )
        data_off = subdf[(subdf.ctcf == "off")].pivot(
            "loading_rate", "unloading_rate", var
        )
        plt.figure()
        if log_flag:
            sns.heatmap(
                np.divide(
                    data_on, data_off, out=np.zeros_like(data_on), where=data_off != 0
                ),
                norm=LogNorm(vmin=bot_lim, vmax=top_lim),
                annot=True,
                cmap="PRGn",
                fmt=".2f",
                cbar_kws={"label": var},
            )
        else:
            sns.heatmap(
                np.divide(
                    data_on, data_off, out=np.zeros_like(data_on), where=data_off != 0
                ),
                annot=True,
                vmin=bot_lim,
                vmax=top_lim,
                cmap="PRGn",
                fmt=".2f",
                cbar_kws={"label": var},
            )

        plt.title(f"Differential plot [on/off], extruder speed {extruder_speed}")
        plt.savefig(args.output + f"/diff_on_off_{var}_{extruder_speed}.pdf")
        plt.show()
        plt.close()
