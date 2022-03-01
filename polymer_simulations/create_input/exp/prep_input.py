import numpy as np
import random
from shutil import copyfile
from pandas.core.frame import DataFrame
import pandas as pd
import uuid
import argparse
import os


def create_coordinates(radius: float, bdsNumber: int = 1000):

    r = 1.0  # initial bond length
    x1 = [np.random.uniform(-1, 1)]
    y1 = [np.random.uniform(-1, 1)]
    z1 = [np.random.uniform(-1, 1)]
    for i in range(bdsNumber - 1):
        theta = np.arccos(1 - 2 * np.random.uniform(0, 1))
        phi = np.random.uniform(0, 2 * np.pi)
        while (
            np.sqrt(
                (x1[-1] + r * np.sin(theta) * np.cos(phi)) ** 2
                + (y1[-1] + r * np.sin(theta) * np.sin(phi)) ** 2
                + (z1[-1] + r * np.cos(theta)) ** 2
            )
            > radius - 2
        ):
            theta = np.arccos(1 - 2 * np.random.uniform(0, 1))
            phi = np.random.uniform(0, 2 * np.pi)
        x1.append(x1[-1] + r * np.sin(theta) * np.cos(phi))
        y1.append(y1[-1] + r * np.sin(theta) * np.sin(phi))
        z1.append(z1[-1] + r * np.cos(theta))
    return (x1, y1, z1)


def filter_ctcf(df_ctcf):
    df_ctcf["orientation"] = np.where(df_ctcf["orientation"] == "+", 1, -1)


def write_lmp_mouse_chr(
    start: int, end: int, init_ctcf: DataFrame, path: str = "./mescs"
):

    ctcf = init_ctcf.copy(deep=True)
    total_size = end - start
    xboxlen = (total_size / 0.01) ** (1 / 3)

    with open(path, "w") as thefile:
        thefile.write("# mESC\n\n")
        thefile.write(f"    {total_size} atoms\n")
        thefile.write(f"    {total_size-1} bonds\n\n\n")
        thefile.write("  4 atom types\n")
        thefile.write("  2 bond types\n\n")
        thefile.write(f"{-xboxlen/2} {xboxlen/2} xlo xhi\n")
        thefile.write(f"{-xboxlen/2} {xboxlen/2} ylo yhi\n")
        thefile.write(f"{-xboxlen/2} {xboxlen/2} zlo zhi\n\n")
        thefile.write("Masses\n\n")
        # 1 - neutral
        # 2 - forward ctcf (left boundary)
        # 3 - reverse ctcf (right boundary)
        # 4 - forward/reverse ctcf (left/right boundary)
        for i in range(4):
            thefile.write(f"{i+1}\t1000.00\n")
        thefile.write("\nAtoms\n\n")

    f = open(path, "a")
    id_bead = 0
    filter_ctcf(ctcf)
    x, y, z = create_coordinates(xboxlen, bdsNumber=end - start)
    for i in range(start, end):
        if i in ctcf.mid.values:
            num_matches = len(ctcf.loc[ctcf["mid"] == i].orientation.values)
            if (
                num_matches > 1
                and abs(np.sum(ctcf.loc[ctcf["mid"] == i].orientation.values))
                != num_matches
            ):
                f.write(
                    f"{id_bead+1} 0 4 {x[id_bead]} {y[id_bead]} {z[id_bead]}\n"
                )  # forward/reverse ctcf (left-right boundary)
                id_bead += 1
            else:
                if ctcf.loc[ctcf["mid"] == i].orientation.values[0] > 0:
                    f.write(
                        f"{id_bead+1} 0 2 {x[id_bead]} {y[id_bead]} {z[id_bead]}\n"
                    )  # forward ctcf (left boundary)
                    id_bead += 1
                elif ctcf.loc[ctcf.mid == i].orientation.values[0] < 0:
                    f.write(
                        f"{id_bead+1} 0 3 {x[id_bead]} {y[id_bead]} {z[id_bead]}\n"
                    )  # reverse ctcf (right boundary)
                    id_bead += 1
        else:
            f.write(
                f"{id_bead+1} 0 1 {x[id_bead]} {y[id_bead]} {z[id_bead]}\n"
            )  # neutral chromatin
            id_bead += 1
    f.write("\n Bonds\n\n")
    id_bead = 1
    id_bond = 1
    for i in range(end - start - 1):
        f.write(f"{id_bond} 1 {id_bead} {id_bead+1}\n")
        id_bead += 1
        id_bond += 1
    id_bead += 1
    f.close()


def parse_args():
    argparser = argparse.ArgumentParser(
        description="Generate a lammps input file for a mouse chromosome"
    )
    argparser.add_argument(
        "--start",
        type=int,
        help="start position of the chromosome",
        required=True,
    )
    argparser.add_argument(
        "--end",
        type=int,
        help="end position of the chromosome",
        required=True,
    )
    argparser.add_argument(
        "--ctcf_path",
        type=str,
        help="path to the ctcf file",
        default="ctcf/ctcf_orientation.csv",
    )
    argparser.add_argument(
        "--num_configs",
        type=int,
        help="number of configurations to generate",
        default=1,
    )
    argparser.add_argument(
        "--output_path",
        type=str,
        help="path to the output file",
        default=f"./inputs/mescs_{uuid.uuid1()}.lmp",
    )
    argparser.add_argument(
        "--chr",
        type=str,
        help="mouse chromosome",
        default="chr1",
    )
    return argparser.parse_args()


def random_walk_confined(n, box):
    r = 1
    trj = np.zeros((n, 3))
    trj[0, 0] = random.uniform(0, box)
    trj[0, 1] = random.uniform(0, box)
    trj[0, 2] = random.uniform(0, box)
    for i in range(1, n):
        theta = np.arccos(1 - 2 * random.uniform(0, 1))
        phi = random.uniform(0, 2 * np.pi)
        trj[i, 0] = trj[i - 1, 0] + r * np.sin(theta) * np.cos(phi)
        trj[i, 1] = trj[i - 1, 1] + r * np.sin(theta) * np.sin(phi)
        trj[i, 2] = trj[i - 1, 2] + r * np.cos(theta)
        while (
            trj[i, 0] < 0
            or trj[i, 1] < 0
            or trj[i, 2] < 0
            or trj[i, 0] > box
            or trj[i, 1] > box
            or trj[i, 2] > box
        ):
            theta = np.arccos(1 - 2 * random.uniform(0, 1))
            phi = random.uniform(0, 2 * np.pi)
            trj[i, 0] = trj[i - 1, 0] + r * np.sin(theta) * np.cos(phi)
            trj[i, 1] = trj[i - 1, 1] + r * np.sin(theta) * np.sin(phi)
            trj[i, 2] = trj[i - 1, 2] + r * np.cos(theta)
    return trj


def calc_box(c, n, langevin=False):
    if langevin:
        return (n / c) ** (1 / 3)
    else:
        return (n / c / 3) ** (1 / 3)


args = parse_args()
ctcf = pd.read_csv(args.ctcf_path, sep=",")
if args.chr not in ctcf.chr.unique():
    raise ValueError(f"{args.chr} not in {ctcf.chr.unique()}")
sub_ctcf = ctcf[ctcf.chr == args.chr]
sub_ctcf = sub_ctcf.assign(
    mid=((sub_ctcf["start"].values + sub_ctcf["end"].values) / 2 / 8000).astype(int)
)

nBeads = 1000
box = calc_box(0.01, nBeads, langevin=True)
ctcf = ["on", "off"]
extruder_speed = ["17500", "175000"]
loading_prob = ["0.02", "0.05", "0.1", "0.2", "0.5"]
unloading_prob = ["0.002", "0.005", "0.01", "0.02", "0.05"]
total_sys = []
for a in ctcf:
    for b in extruder_speed:
        for c in loading_prob:
            for d in unloading_prob:
                for e in range(10):
                    loc_path = f"{a}/{b}/{c}/{d}/{e}/"
                    os.makedirs(loc_path)
                    fr = open("polymer.lam", "r")
                    fw = open(f"{loc_path}polymer.lam", "w")

                    write_lmp_mouse_chr(
                        args.start, args.end, sub_ctcf, path=loc_path + "pol1k.data"
                    )
                    run_r = open("run.sh", "r")
                    run_w = open(f"{loc_path}run.sh", "w")
                    for line in fr:
                        if "fix loop all extrusion" in line:
                            if a == "on":
                                fw.write(f"fix loop all extrusion {b} 1 2 3 0.0 2 4\n")
                            else:
                                fw.write(f"fix loop all extrusion {b} 1 2 3 1.0 2\n")
                        elif "fix loading all" in line:
                            fw.write(
                                f"fix loading all ex_load 7000 1 1 1.12 2 prob {c} {np.random.randint(10000000)} iparam 1 1 jparam 1 1\n"
                            )
                        elif "fix unloading all" in line:
                            fw.write(
                                f"fix unloading all ex_unload 7000 2 0.5 prob {d} {np.random.randint(10000000)}\n"
                            )
                        else:
                            fw.write(line)
                    for line in run_r:
                        if "#$ -N" in line:
                            run_w.write(f"#$ -N {a}{b}-{c.count('0')}-{d.count('0')}\n")
                        else:
                            run_w.write(line)
