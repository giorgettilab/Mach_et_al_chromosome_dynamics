"""
Save last model to file
"""
from ij import IJ
from ij.io import SaveDialog
import os
from plugin import Descriptor_based_registration

from ch.fmi.util import TransformUtils as TU

if Descriptor_based_registration.lastModel1 != None:
  # setup dialog to get file name
  sd = SaveDialog("Save transformation file to", "", "")
  filePath = os.path.join(sd.getDirectory(), sd.getFileName())
  # Descriptor_based_registration.lastModel1
  TU.saveModelToFile( Descriptor_based_registration.lastModel1, filePath )
else:
  IJ.error("No last model found.")
