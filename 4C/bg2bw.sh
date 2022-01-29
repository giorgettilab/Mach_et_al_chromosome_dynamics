#!/bin/bash
PATH=$PATH:/tungstenfs/scratch/ggiorget/pavel/4c/kentUtils/bin
for i in *.bedGraph
do
awk '!/NA/' $i > temp && mv temp $i
bedGraphToBigWig $i mm9.chrom.sizes $i.bw
done
