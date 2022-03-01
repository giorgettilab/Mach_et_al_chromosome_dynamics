import numpy as np
import os
import numpy as np
import random
from shutil import copyfile


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


def linear_chain(
    path: str,
    n: int,
    cell_size: float,
    ctcf: int = 0,
    tad_size: int = 100,
    langevin: bool = False,
):
    rho = 3  # density
    if langevin:
        total = n
    else:
        total = int(rho * (cell_size ** 3))
    solvent = total - n
    if ctcf == 8:  # 1k
        left = np.linspace(1500, 8500, ctcf).astype(int) - int(tad_size / 2 + 1)
        if bool(tad_size % 2):
            right = np.linspace(1500, 8500, ctcf).astype(int) + int(tad_size / 2)
        else:
            right = np.linspace(1500, 8500, ctcf).astype(int) + int(tad_size / 2 - 1)
    elif ctcf == 17 or ctcf == 33 or ctcf == 65:  # 500, 250, 125
        left = np.linspace(1000, 9000, ctcf) - int(tad_size / 2 + 1)
        if bool(tad_size % 2):
            right = np.linspace(1000, 9000, ctcf) + int(tad_size / 2)
        else:
            right = np.linspace(1000, 9000, ctcf) + int(tad_size / 2 - 1)
    elif ctcf == 1:
        left = np.array([489])
        right = np.array([509])
    with open(path, "w") as thefile:
        thefile.write("#linear chain\n\n")
        thefile.write("    " + str(total) + " atoms\n")
        thefile.write("    " + str(n - 1) + " bonds\n\n\n")
        if ctcf > 0:
            thefile.write("  3 atom types\n")
        else:
            thefile.write("  2 atom types\n")
        thefile.write("  2 bond types\n\n")
        thefile.write("0.000 %5.3f xlo xhi\n" % cell_size)
        thefile.write("0.000 %5.3f ylo yhi\n" % cell_size)
        thefile.write("0.000 %5.3f zlo zhi\n\n" % cell_size)
        thefile.write("Masses\n")
        if ctcf > 0:
            thefile.write("\n1\t1000\n2\t1000\n3\t1000\n\n Atoms\n\n")
        else:
            thefile.write("\n1  1.00\n2 1.00\n\n Atoms\n\n")
    f = open(path, "a")
    trj = random_walk_confined(n, (cell_size - 1) / 2)
    for i in range(n):
        if i in left:
            f.write(
                "%8d 1 2 %5.4f %5.4f %5.4f\n"
                % (
                    i + 1,
                    trj[i, 0] + cell_size / 2,
                    trj[i, 1] + cell_size / 2,
                    trj[i, 2] + cell_size / 2,
                )
            )
        elif i in right:
            f.write(
                "%8d 1 3 %5.4f %5.4f %5.4f\n"
                % (
                    i + 1,
                    trj[i, 0] + cell_size / 2,
                    trj[i, 1] + cell_size / 2,
                    trj[i, 2] + cell_size / 2,
                )
            )
        else:
            f.write(
                "%8d 1 1 %5.4f %5.4f %5.4f\n"
                % (
                    i + 1,
                    trj[i, 0] + cell_size / 2,
                    trj[i, 1] + cell_size / 2,
                    trj[i, 2] + cell_size / 2,
                )
            )
    for i in range(solvent):
        f.write(
            "%8d 0 4 %5.4f %5.4f %5.4f\n"
            % (
                n + i + 1,
                random.uniform(0, cell_size),
                random.uniform(0, cell_size),
                random.uniform(0, cell_size),
            )
        )
    f.close()
    with open(path, "a") as thefile:
        thefile.write("\n Bonds\n\n")
    f = open(path, "a")
    for i in range(1, n):
        f.write("%8d 1 %5d %5d\n" % (i, i, i + 1))
    f.close()


def calc_box(c, n, langevin=False):
    if langevin:
        return (n / c) ** (1 / 3)
    else:
        return (n / c / 3) ** (1 / 3)


nBeads = 1000
box = calc_box(0.01, nBeads, langevin=True)
ctcf = ["on", "off"]  # 0.001 1.0
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
                    # copyfile("../def_input/polymer.lam", loc_path)
                    fr = open("polymer.lam", "r")
                    fw = open(f"{loc_path}polymer.lam", "w")
                    linear_chain(
                        loc_path + "pol1k.data",
                        nBeads,
                        box,
                        ctcf=1,
                        tad_size=19,
                        langevin=True,
                    )
                    run_r = open("run.sh", "r")
                    run_w = open(f"{loc_path}run.sh", "w")
                    for line in fr:
                        if "fix loop all extrusion" in line:
                            if a == "on":
                                fw.write(f"fix loop all extrusion {b} 1 2 3 0.0 2\n")
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
