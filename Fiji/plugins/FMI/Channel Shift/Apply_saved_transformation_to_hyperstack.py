"""
Apply saved transformation to multi-channel image
"""
from ij import IJ
from ij.plugin import ChannelSplitter
# from ij.gui import GenericDialog, DialogListener

from fiji.util.gui import GenericDialogPlus

from ch.fmi.util import TransformUtils as TU

def main():
    imp = IJ.getImage()
    channels = ChannelSplitter.split(imp)
    gd = GenericDialogPlus("Channel shift correction")
    for i in range(len(channels)):
        gd.addFileField("Transformation_" + str(i+1), "")
    gd.showDialog()
    #filePath = IJ.getFilePath("Transformation file")
    tfms = []
    for i in range(len(channels)):
        tfmFilePath = gd.getNextString()
        tfms.append(TU.loadTransformFromFile(tfmFilePath))
    resultsImps = TU.applyTransforms(channels, tfms)
    for result in resultsImps:
        result.show()

main()
