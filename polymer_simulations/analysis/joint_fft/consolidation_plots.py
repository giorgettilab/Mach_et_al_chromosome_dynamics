import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import pathlib
import argparse
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42

argparser = argparse.ArgumentParser(description="Consolidation plots")
argparser.add_argument(
    "-i", "--input", help="Consolidation zip of on/off cases", required=True
)
argparser.add_argument(
    "-chr",
    "--realistic",
    help="To estimate chain length (1125 if chr and 1000 if not)",
    required=True,
)
args = argparser.parse_args()
df = pd.read_csv(args.input)  # path to consolidation zip archive

for var in [
    "msd_alpha1",
    "msd_D1",
    "msd_alpha2",
    "msd_D2",
    "pc_slope_aver",
    "dsts_ctcf",
    "num_loops",
]:
    if "msd_alpha" in var:
        bot_lim = 0.4
        top_lim = 0.8
        log_flag = False
    elif "msd_D" in var:
        bot_lim = 10.0
        top_lim = 30.0
        log_flag = False
    elif "pc_slope" in var:
        bot_lim = -3.0
        top_lim = -0.3
        log_flag = False
    elif "dsts" in var:
        bot_lim = 3
        top_lim = 6
        log_flag = False
    elif "num_loops" in var:
        bot_lim = 0
        top_lim = 30
        log_flag = False

    for ctcf in ["on", "off"]:
        for extruder_speed in [175000, 17500, 1750]:
            subdf = df[(df.ctcf == ctcf) & (df.extruder_speed == extruder_speed)]
            if subdf.empty:
                continue
            if var == "dsts_ctcf" and args.realistic == "on":
                continue
            if var == "num_loops":
                if args.realistic == "on":
                    backbone_bonds = 1124
                    data = (
                        subdf.pivot("loading_rate", "unloading_rate", var)
                        - backbone_bonds
                    ) / 9.0
                else:
                    backbone_bonds = 999
                    data = (
                        subdf.pivot("loading_rate", "unloading_rate", var)
                        - backbone_bonds
                    ) / 8.0
            else:
                data = subdf.pivot("loading_rate", "unloading_rate", var)
            plt.figure()
            if log_flag:
                sns.heatmap(
                    data,
                    norm=LogNorm(vmin=bot_lim, vmax=top_lim),
                    annot=True,
                    cmap="viridis",
                    cbar_kws={"label": var},
                )
            else:
                sns.heatmap(
                    data,
                    annot=True,
                    vmin=bot_lim,
                    vmax=top_lim,
                    cmap="viridis",
                    cbar_kws={"label": var},
                )

            plt.title(f"CTCF {ctcf}, extruder speed {extruder_speed}")
            pathlib.Path(
                "/".join(args.input.split("/")[:-1]) + "/consolidation_plots"
            ).mkdir(parents=True, exist_ok=True)
            p = (
                "/".join(args.input.split("/")[:-1])
                + f"/consolidation_plots/{ctcf}_{extruder_speed}_{var}.pdf"
            )
            print(p)
            plt.savefig(
                p,
            )
            plt.close()
