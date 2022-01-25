# @ImagePlus imp

from ij import IJ
from ij.plugin.frame import RoiManager

def run():
    rm = RoiManager.getInstance()
    if not rm:
        print "Please first add some ROIs to the ROI Manager"
        return
    impMask = IJ.createImage("Mask", "8-bit grayscale-mode", imp.getWidth(), imp.getHeight(), imp.getNChannels(), imp.getNSlices(), imp.getNFrames())
    IJ.setForegroundColor(255, 255, 255)
    rm.runCommand(impMask,"Deselect")
    rm.runCommand(impMask,"Fill")
    impMask.show()

run()
