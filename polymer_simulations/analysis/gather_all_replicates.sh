#!bin/bash

## Author(s): Pavel Kos
## Contact: pavel.kos@fmi.ch
## This software is distributed without any guarantee under the terms of the GNU General
## Public License, either Version 2, June 1991 or Version 3, June 2007.

temp="temp_$(uuidgen).dat"
echo "Temporary file $temp"
echo Start >> $temp
echo $1 >> $temp

python code/joint_cmap.py $1/ >> $temp
echo joint contact map is calculated
python code/joint_dmap.py $1/ >> $temp
echo joint distance map is calculated
python code/joint_fft/joint_msd.py $1/ >> $temp
echo joint MSD is calculated
echo joint pairwise MSD is calculated
python code/contact_probability.py -i $i/joint_cm.dat -o $i/ -l 100 200 -n 10 >> $temp
echo joint contact probability is calculated
python code/joint_fft/hist_distances.py $i/
echo distribution of distances is calculated
echo Done >> $temp
rm $temp
return 0


