setwd("/path/to/work/directory/")

library(QuasR)
library("BSgenome.Mmusculus.UCSC.mm9")
library(BSgenome)
library(Biostrings)

genomeName <- "BSgenome.Mmusculus.UCSC.mm9"
sampleFile <- "SampleFile.tsv" # file with sample names
clObj <- makeCluster(10) # use multiple cores to speed up
proj <- qAlign(sampleFile, genome = genomeName, clObj = clObj, alignmentsDir = "../BamFiles/") # alignment
proj
qQCReport(proj, "Alignment_QC_report.pdf", clObj = clObj)

restr.site <- DNAString("GATC") 

matches <- vmatchPattern(restr.site, BSgenome.Mmusculus.UCSC.mm9)
head(matches)
matches <- reduce(matches, ignore.strand=TRUE)
GATClevels <- qCount(proj, matches, clObj = clObj, orientation = "any")
colSums(GATClevels[,-1])/alignmentStats(proj)[,2]

#Make matrix into data.frame and run average on the counts. Add the GRanges information to the data.frame

CPM <- t(t(GATClevels[, -1])/colSums(GATClevels[, -1]) * 1e+06)
colSums(CPM) #should be 1e+06

#matrix = mcols(AATTlevels[,-1]) #counted data
ra_df = data.frame(apply(CPM,2,filter,rep(1/21,21)))
ra_df$chr = seqnames(matches)
ra_df$start = start(matches)
ra_df$end = end(matches)

chrs = unique(ra_df$chr)
chrs <- grep("random", chrs, invert=TRUE, value = TRUE)
library(ggplot2)
#plot all 6 in single axis
for (i in as.character(chrs)){
selection = as.vector(ra_df$chr == i)
pdf(file = paste0(i,"_4C_viewpoints.pdf"))

# ggplot(data = df, aes(x = "column name x", y= "column name y"))

abc <- ggplot()+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF_3G4_0min), color="black", size=0.5)+
ylim(0,1000)+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF_3G4_90min), color="orange", size=0.5)+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF_3G4_240min), color="red", size=0.5)+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF.Cre_3G4.C4_0min), color="blue", size=0.5)+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF.Cre_3G4.C4_90min), color="green", size=0.5)+
geom_line(data = ra_df[selection,], aes(x = start, y = X3xCTCF.Cre_3G4.C4_240min), color="purple", size=0.5)+
xlab("Genomic coordinate")+
ylab("CPM")+
theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(), panel.background = element_blank(), axis.line = element_line(colour = "black"))
print(abc)
dev.off()
}

#Export to .bedGraph files
name=c("3xCTCF_3G4_0min", "3xCTCF_3G4_90min", "3xCTCF_3G4_240min", "3xCTCF+Cre_3G4-C4_0min", "3xCTCF+Cre_3G4-C4_90min", "3xCTCF+Cre_3G4-C4_240min")
for(i in 1:6){
  write.table(x=ra_df[,c(7,8,9,i)], file=paste0(name[i],".bedGraph"), sep="\t",row.names = F, col.names = F, quote=F)
}
