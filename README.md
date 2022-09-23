Code for the study: 
# Live-cell imaging and physical modeling reveal control of chromosome folding dynamics by cohesin and CTCF
by 
### Pia Mach<sup>1,2*</sup>, Pavel Kos<sup>1*</sup>, Yinxiu Zhan<sup>1*</sup>, Julie Cramard<sup>1</sup>, Simon Gaudin<sup>1,3</sup>, Jana Tünnermann<sup>1,2</sup>, Jan Eglinger<sup>1</sup>, Jessica Zuin<sup>1</sup>, Mariya Kryzhanovska<sup>1</sup>, Sebastien Smallwood<sup>1</sup>, Laurent Gelman<sup>1</sup>, Edoardo Marchi<sup>4</sup>, Gregory Roth<sup>1</sup>, Elphège P Nora<sup>5</sup>, Guido Tiana<sup>4</sup>, Luca Giorgetti<sup>1,#</sup>

<sup>1</sup> Friedrich Miescher Institute for Biomedical Research, Basel, Switzerland

<sup>2</sup> University of Basel, Basel, Switzerland

<sup>3</sup> École Normale Supérieure de Lyon and Université Claude Bernard Lyon I, Université de Lyon, Lyon, France

<sup>4</sup> Università degli Studi di Milano and INFN, Milan, Italy.

<sup>5</sup> Cardiovascular Research Institute, University of California San Francisco; Department of Biochemistry and Biophysics, University of California San Francisco; San Francisco, CA, USA

<sup>#</sup> correspondence: luca.giorgetti@fmi.ch

## 4C
Folder contains bash script to trim the adapter sequence and R script to map all the insertions. All the packages are specified in the Supplementary information.

## Fiji
Folder contains installation package for plugin with ImageJ. You can find the detailed information [here](https://imagej.net/software/fiji/)

## Hi-C
Folder contains config files and used chromosome sizes corresponding to genome mm9. The analysis was performed using HiC-Pro. All the details are specified in the Supplementary information.

## nanopore
Folder contains nanopore sequences for TetO and LacO in FASTA format.

## sequences
Folder contains reads coming from the TetR or LacI, to exclude them from the consideration.

## polymer simulations
Folder contains input to perform the simulations using LAMMPS package with specifically designed addon. There is python and C++ code to analyze it. Calculating MSD was developed using FFT with the complexity O(n*log(n)).

All the code was compiled with CMake v.3.15.5 when applicable and executed on linux with OS CentOS 7. The used Python version was 3.8.10 unless other information stated in the Supplemntary information. 
