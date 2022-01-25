"""
Apply saved transformation to single channel
"""
from ij import IJ
from ch.fmi.util import TransformUtils as TU
# from ij.gui import GenericDialog, DialogListener

def main():
    imp = IJ.getImage()
    filePath = IJ.getFilePath("Transformation file")
    if filePath != "":
        tfm = TU.loadTransformFromFile(filePath)
        resultImp = TU.applyTransform(imp, tfm)
        resultImp.show()

main()
