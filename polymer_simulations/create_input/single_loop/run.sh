#!/bin/sh
#$ -S /bin/sh

#$ -V
#$ -cwd
#$ -j y
#$ -N off500-5-3
#$ -l m_mem_free=5G    # memory for a single job
#$ -l h_rt=1200000
#$ -r y # job can be rerun
#$ -pe orte 8

mpirun -np $NSLOTS /home/kospa2/lammps_le-main/build5/lmp -in polymer.lam
