"""
Measure channel shift from separate images
"""

from ij import IJ, WindowManager
from ij.gui import GenericDialog, DialogListener
from ij.plugin import ChannelSplitter
from fiji.util.gui import GenericDialogPlus

from ch.fmi.util import TransformUtils as TU

# DialogListener for interactive behaviour
class MyListener (DialogListener):
    def dialogItemChanged(self, gd, event):
        return True

# Main script

def main():
    if WindowManager.getImageCount() < 1:
        IJ.noImage()
        return
    # Dialog #1: get channels and general parameters
    gd = GenericDialogPlus("Channel shift correction")
    gd.addImageChoice("Channel_1", None)
    gd.addStringField("Channel_name_1", "C1")
    gd.addImageChoice("Channel_2", None)
    gd.addStringField("Channel_name_2", "C2")
    gd.addImageChoice("Channel_3", None) # TODO allow None here
    gd.addStringField("Channel_name_3", "C3")
    #gd.addCheckbox("Show_overlayed_image", False)
    #gd.addCheckbox("Show_point_selections", True) # currently not supported
    #gd.addCheckbox("Save_transforms", True)
    
    # TODO add choice of transformation model (translation, rigid, affine)
    # TODO add option to ignore Z ?
    gd.addMessage("")
    global messageField, saveCheckboxState
    saveCheckboxState = True
    messageField = gd.getMessage()
    dl = MyListener()
    gd.addDialogListener(dl)
    dl.dialogItemChanged(gd, None) # Initialize error message
    gd.showDialog()
    if gd.wasCanceled():
        print "Script was cancelled."
        return
    imps = []
    imps.append(gd.getNextImage())
    imps.append(gd.getNextImage())
    imps.append(gd.getNextImage())
    chName1 = gd.getNextString()
    chName2 = gd.getNextString()
    chName3 = gd.getNextString()
    print imps
    showOverlay = False # gd.getNextBoolean()
    showPoints = False # gd.getNextBoolean()
    #saveTransforms = gd.getNextBoolean()
    # Dialog #2: get reference channel
    gd2 = GenericDialog("Reference channel")
    chNames = [chName1, chName2]
    if imps[2] != None:
        chNames.append(chName3)
    gd2.addRadioButtonGroup("Reference channel", chNames, 3, 1, chName1)
    gd2.showDialog()
    if gd2.wasCanceled():
        print "Script was cancelled."
        return
    refChName = gd2.getNextRadioButton()
    refChPos = chNames.index(refChName)
    # Dialog #3 get file path to save
    saveDir = IJ.getDirectory("Save transformation files to")

    # Get and adjust parameters
    params = TU.getDefaultRegistrationParameters()
    params.dimensionality = 3 # TODO make sure dimensionality and model are consistent
    params.silent = False # verbose mode for debugging
    params.fuse = (1 if showOverlay else 2) # no Overlay image
    params.setPointsRois = showPoints
    # For each channel from 2 to n, align to first channel (getModels)
    for i in range(len(imps)):
        if i != refChPos:
            print "Aligning channel", i+1, "to channel", refChPos+1
            model = TU.getModel( imps[i], imps[refChPos], params )
            TU.saveModelToFile(model, saveDir + "/Channel_Transformation_" + chNames[i])
        else:
            print "Saving unity matrix for reference channel"
            TU.saveIdentityModelToFile(saveDir + "/Channel_Transformation_" + chNames[i])
            
    # If 'save transformations': save tfm files for each channel ('ChannelTransformation_' + channelNameX + '.txt')

main()
