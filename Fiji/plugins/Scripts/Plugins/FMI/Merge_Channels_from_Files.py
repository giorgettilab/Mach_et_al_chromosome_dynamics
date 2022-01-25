"""
Merge single channel files
# (C)2015 Jan Eglinger, FAIM, FMI Basel
"""

import os
from difflib import SequenceMatcher
from fiji.util.gui import GenericDialogPlus
from ij import IJ, Prefs
from ij.gui import GenericDialog
from ij.plugin import RGBStackMerge
from loci.plugins import BF

PREF_KEY = "batchMergeChannels."
MERGED_STR = "_merged_"
ijLUTs = IJ.getLuts()

"""
### Options dialog
"""
def getOptions():
  gd = GenericDialogPlus("Merge single-channel files")
  gd.addDirectoryField("Choose a directory", Prefs.get(PREF_KEY+"folder", ""))
  gd.addStringField("Input_file_extension",  Prefs.get(PREF_KEY+"readExt", "ids"))
  gd.addNumericField("Number of channels", Prefs.get(PREF_KEY+"nCh", 3), 0)
  gd.addStringField("Output_file_extension", Prefs.get(PREF_KEY+"saveExt", "tif"))
  gd.showDialog()
  if gd.wasCanceled():
    return None, None, None, None
  folder, readExt, nCh, saveExt = gd.getNextString(), gd.getNextString(), gd.getNextNumber(), gd.getNextString()
  Prefs.set(PREF_KEY+"folder", folder)
  Prefs.set(PREF_KEY+"readExt", readExt)
  Prefs.set(PREF_KEY+"nCh", nCh)
  Prefs.set(PREF_KEY+"saveExt", saveExt)
  return folder, readExt, nCh, saveExt

"""
### Channel names dialog
"""
def getChannelConfig(nCh):
  gd = GenericDialog("Channel names")
  chNames = []
  chLuts = []
  for i in range(int(nCh)):
    gd.addStringField("Channel_" + str(i+1), Prefs.get(PREF_KEY+"ch"+str(i+1), ""))
    gd.addChoice("Channel_" + str(i+1) + " LUT", ijLUTs, Prefs.get(PREF_KEY+"lut"+str(i+1), getLUT(i)))
  gd.showDialog()
  if gd.wasCanceled():
    return None, None
  for i in range(int(nCh)):
    chName = gd.getNextString()
    chNames.append(chName)
    Prefs.set(PREF_KEY+"ch"+str(i+1), chName)
    chLut = gd.getNextChoice()
    chLuts.append(chLut)
    Prefs.set(PREF_KEY+"lut"+str(i+1), chLut)
  return chNames, chLuts

# ------ Helper methods ------
def getLUT(i):
  return {
    0: 'Red',
    1: 'Green',
    2: 'Blue',
    3: 'Cyan',
    4: 'Magenta',
    5: 'Yellow'
  }.get(i, 'Grays')

def getContaining(seq, value, ext):
  for el in seq:
    if value in el and el.endswith(ext):
      yield el

def getRatio(matcher, x):
  matcher.set_seq2(x)
  return matcher.ratio()

def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr

"""
### Merge images

Merge all files in a set, using the given LUTs
"""
def merge(folder, set, luts, chNames, ext):
  print len(set), "files being merged:"
  imps = []
  for name, lut in zip(set, luts):
    print name, "(" + lut + ")"
    # open file using bio-formats
    imp = BF.openImagePlus(os.path.join(folder, name))[0]
    # set LUT
    IJ.run(imp, lut, "")
    imps.append(imp)
  # merge images
  mergedImp = RGBStackMerge.mergeChannels(imps, False)
  # get common name parts
  names = []
  for name, ch in zip(set, chNames):
    prefix, suffix = name.split(ch)
    names.append(prefix + MERGED_STR + suffix)
  saveName = long_substr(names) + "." + ext # TODO replace longest substring by consensus string
  print "Saving as", saveName
  # save merged image
  # mergedImp.show()
  if ext is "tif" or "tiff":
    IJ.saveAs(mergedImp, "Tiff", os.path.join(folder, saveName))
  else:
    IJ.run(mergedImp, "Bio-Formats Exporter", "save=[" + os.path.join(folder, saveName) + "]")
  # "Bio-Formats Exporter", "save=[" + mergetitle + "]")
  print "Done saving."
  mergedImp.close()
  return

"""
### Group files

Group files in a collection of lists and merge them
"""
def mergeFiles(folder, inputLists, luts, chNames, ext):
  i = 0
  nFiles = len(inputLists[i])
  # Check if all lists have the same length, else return
  for chList in inputLists:
    if len(inputLists[i]) != nFiles:
      IJ.error("Equal numbers of files for each channel are required.\n" + str(nFiles) + " files per channel were expected.")
      return
    i += 1

  s = SequenceMatcher()
  for f in inputLists[0]:
    mergeSet = []
    mergeSet.append(f)
    s.set_seq1(f)
    for i in range(1, len(inputLists)):
      # add corresponding channels to merge set by similarity
      mergeSet.append(max(inputLists[i], key=lambda x: getRatio(s,x)))
    # merge current set
    merge(folder, mergeSet, luts, chNames, ext)
  return

"""
### Main method

 - Get folder and channel number
 - Get channel configuration (names and LUTs)
 - Iterate over folder and subfolders

"""
def run():
  # Ask for directory, file extension, and number of channels to merge
  folder, readExt, nCh, saveExt = getOptions()
  if folder is None:
    return
  if folder == "" or not os.path.isdir(folder):
    IJ.error("Not a valid folder")
    return
  
  # Ask for n channel names
  chNames, chLuts = getChannelConfig(nCh)
  if chNames is None:
    return

  # Get directory listings with extension and channel names,
  # perform channel merge per subfolder
  for currDir, dirFiles, files in os.walk(folder):
    fileLists = []
    for channel in chNames:
      fileLists.append(list(getContaining(files, channel, readExt)))
    mergeFiles(currDir, fileLists, chLuts, chNames, saveExt)
  print "Done."
  return

run()
