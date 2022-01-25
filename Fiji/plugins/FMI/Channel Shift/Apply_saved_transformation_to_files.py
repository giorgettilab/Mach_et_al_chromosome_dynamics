import os
from ij import IJ, ImagePlus
# from ij.gui import GenericDialog
from fiji.util.gui import GenericDialogPlus
from loci.plugins import BF
from ch.fmi.util import TransformUtils as TU

def run():
  gd = GenericDialogPlus("Apply Transform to Files")
  gd.addDirectoryField("Input_directory", "")
  gd.addDirectoryField("Output_directory", "")
  gd.addFileField("Transformation", "")
  gd.addStringField("File_extension", ".tif")
  gd.addStringField("File_name_contains", "")
  gd.addCheckbox("Keep directory structure when saving", True)
  gd.showDialog()
  if gd.wasCanceled():
    return
  srcDir = gd.getNextString()
  dstDir = gd.getNextString()
  transformFile = gd.getNextString()
  if srcDir == "" or dstDir == "" or transformFile == "":
    IJ.error("Please provide an input and output directory as well as a transformation file.")
    return
  ext = gd.getNextString()
  containString = gd.getNextString()
  keepDirectories = gd.getNextBoolean()
  tfm = TU.loadTransformFromFile(transformFile)
  for root, directories, filenames in os.walk(srcDir):
    for filename in filenames:
      # Check for file extension
      if not filename.endswith(ext):
        continue
      # Check for file name pattern
      if containString not in filename:
        continue
      process(srcDir, dstDir, root, filename, keepDirectories, tfm)

def process(srcDir, dstDir, currentDir, fileName, keepDirectories, transform):
  IJ.log("Applying transformation...\n" + transform.string() + "... to " + fileName)
  print "Processing:"
  print "srcDir:", srcDir
  print "dstDir", dstDir
  print "currentDir", currentDir
  print "fileName", fileName
  # imp = IJ.openImage(os.path.join(currentDir, fileName))
  # use BF here
  imps = BF.openImagePlus(os.path.join(currentDir, fileName))
  imp = imps[0]
  resultImp = TU.applyTransform(imp, transform)
  saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
  print "Saving to", saveDir
  IJ.saveAs(resultImp, "Tiff", os.path.join(saveDir, fileName));
  #imp.close()

run()
