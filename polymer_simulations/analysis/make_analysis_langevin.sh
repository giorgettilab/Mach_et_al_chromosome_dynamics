#!bin/bash

## Author(s): Pavel Kos
## Contact: pavel.kos@fmi.ch
## This software is distributed without any guarantee under the terms of the GNU General
## Public License, either Version 2, June 1991 or Version 3, June 2007.

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)
temp="temp_$(uuidgen).dat"
echo "Temporary file $temp"
echo Start >> $temp
echo $1 >> $temp

if [ "$2" == "replot" ]; then
replot=true
else
replot=false
fi

if [ "$3" == "difflen" ]; then
    difflen=true
else
    difflen=false
fi

if [ "$2" == "difflen" ]; then
    difflen=true
else
    difflen=false
fi

echo -en "\nFolder path to be analyzed: $1\n"
# Check whether files are here
if [ ! -f $1/mytraj.lammpstrj ]; then
echo -en "${RED}[-][-]${NC} No traj file\n"
return 1
fi

# Check whether maps have been already calculated 
if ([ ! -f $1/mytraj.lammpstrj_dm.dat ]) || [ "$replot" = true ] ; then
echo -en "${RED}[-]${NC} Calculating contact/distance maps"
fi
wait

# Check whether msds averaged/single have been calculated
if [ ! -f $1/mytraj.lammpstrj_msd_s_fft.dat ] || [ ! -f $1/mytraj.lammpstrj_msd_a_fft.dat ] || [ "$replot" = true ]; then
echo -en "${RED}[-]${NC} Calculating MSD of single beads"
mpiexec -np 5 code/msd_c/msd_fft -lmp -p $1/mytraj.lammpstrj >> $temp 2>&1
if [ -f $1/mytraj.lammpstrj_msd_s_fft.dat ] || [ -f $1/mytraj.lammpstrj_msd_a_fft.dat ]; then
echo -en "\033[2K"
echo -en "\r${GREEN}[+]${NC} MSDs averaged and per bead (single) have been calculated\n"
else
echo -en "\033[2K"
echo -en "\r${RED}[-][-]${NC} Something went wrong with calculating MSDs: averaged and for single beads\n"
return 1
fi
else
echo -en "${GREEN}[+]${NC} MSDs averaged and per bead (single) have been calculated\n"
fi

# Check whether distance map has been already plotted
if [ ! -f $1/mytraj.lammpstrj_dm.dat.png ] || [ "$replot" = true ] ; then
echo -en "${RED}[-]${NC} Plotting distance map"
python3 code/dmap.py $1/mytraj.lammpstrj_dm.dat 1000 >> $temp 2>&1
if [ -f $1/mytraj.lammpstrj_dm.dat.png ]; then
echo -en "\033[2K"
echo -en "\r${GREEN}[+]${NC} Distance map is plotted\n"
else
echo -en "\033[2K"
echo -en "\r${RED}[-][-]${NC} Something went wrong with plotting distance map\n"
return 1
fi
else
echo -en "${GREEN}[+]${NC} Distance map has already been plotted\n"
fi

# Check whether contact map has been already plotted
if [ ! -f $1/mytraj.lammpstrj_cm.dat.png ] || [ "$replot" = true ] ; then
echo -en "${RED}[-]${NC} Plotting contact map"
python3 code/cmap.py $1/mytraj.lammpstrj_rc_3.000000_cm.dat >> $temp 2>&1
if [ -f $1/mytraj.lammpstrj_rc_3.000000_cm.dat.png ]; then
echo -en "\033[2K"
echo -en "\r${GREEN}[+]${NC} Contact map is plotted\n"
else
echo -en "\033[2K"
echo -en "\r${RED}[-][-]${NC} Something went wrong with plotting contact map\n"
return 1
fi
else
echo -en "${GREEN}[+]${NC} Contact map has already been plotted\n"
fi

# Check whether pc has been already plotted
if [ ! -f $1/pc_contact_prob.png ] || [ "$replot" = true ] ; then
echo -en "${RED}[-]${NC} Plotting contact probability"
python3 code/contact_probability.py -i $1/mytraj.lammpstrj_rc_3.000000_cm.dat -f pdf -lb 1 -o $1/ >> $temp 2>&1
if [ -f $1/pc_contact_prob.png ] || [ -f $1/pc_contact_prob.pdf ]; then
echo -en "\033[2K"
echo -en "\r${GREEN}[+]${NC} Pc is plotted\n"
else
echo -en "\033[2K"
echo -en "\r${RED}[-][-]${NC} Something went wrong with plotting Pc\n"
return 1
fi
else
echo -en "${GREEN}[+]${NC} Pc has already been plotted\n"
fi

# Check whether pairwise MSD has been already calculated
if [ ! -f $1/dst_bnd.dat_msd_pairwise_fft.dat ] || [ "$replot" = true ] ; then
    echo -en "${RED}[-]${NC} Plotting pairwise MSD"
    mpiexec -np 1 code/ctcf_msd_pairwise/ctcf_msd_fft -p $1/dst_bnd.dat -s 1 >> $temp 2>&1
    if [ -f $1/dst_bnd.dat_msd_pairwise_fft.dat ]; then
        echo -en "\033[2K"
        echo -en "\r${GREEN}[+]${NC} Pairwise MSD is calculated\n"
    else
        echo -en "\033[2K"
        echo -en "\r${RED}[-][-]${NC} Something went wrong with calculating pairwise MSD\n"
        return 1
    fi
else
    echo -en "${GREEN}[+]${NC} Pairwise MSD has already been calculated\n"
fi
echo -en "${GREEN}[+][+]${NC} Done!\n"
rm $temp
return 0
