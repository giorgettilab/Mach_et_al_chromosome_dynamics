# @File (label="Choose directory to open", style="directory") srcDir

"""
Merge two 16-bit channels into RGB
with enhanced contrast
"""

import re, os
from ij import IJ
from ij.plugin import RGBStackMerge, RGBStackConverter
from java.io import File

def getFilteredFileList(folder, pattern):
    """
    Return a list of files in `folder` filtered by `pattern`
    """
    for root, folders, files in os.walk(folder):
        break
    r = re.compile(pattern)
    return filter(r.match, files)


imagePattern = "^(?P<basename>\w+)_(?P<channel>w\d\w+)_(?P<pos>pos\d)_[\w-]*.tif$"
greenChannel = "w1L491"
redChannel =   "w2L640"

# get directory file list
fileList = getFilteredFileList(srcDir.getAbsolutePath(), imagePattern)

print "File list:", fileList
# match pattern
# ?get channels

# get positions
pos_set = set()
for f in fileList:
    m = re.match(imagePattern, f)
    pos_set.add(m.group("pos"))

for p in pos_set:
    # open green channel
    pos_pattern = re.sub('\(\?P<pos>[^\)]*\)', p, imagePattern)
    green_pattern = re.sub('\(\?P<channel>[^\)]*\)', greenChannel, pos_pattern)
    red_pattern = re.sub('\(\?P<channel>[^\)]*\)', redChannel, pos_pattern)
    for f in fileList:
        m = re.match(green_pattern, f)
        if m:
            print "Opening green image", f
            greenImage = f
            outName = f.replace(greenChannel, "RGB")
        m = re.match(red_pattern, f)
        if m:
            print "Opening red image", f
            redImage = f
    redImp = IJ.openImage(os.path.join(srcDir.getAbsolutePath(), redImage))
    IJ.setMinAndMax(redImp, 0, 16000)
    #IJ.run(redImp, "Enhance Contrast...", "saturated=0.2 process_all use")
    greenImp = IJ.openImage(os.path.join(srcDir.getAbsolutePath(), greenImage))
    IJ.setMinAndMax(greenImp, 0, 24000)
    #IJ.run(greenImp, "Enhance Contrast...", "saturated=0.2 process_all use")

    #redImp.show() # DEBUG
    #greenImp.show() # DEBUG

    fused = RGBStackMerge.mergeChannels([redImp, greenImp], False)
    redImp.close()
    greenImp.close()
    #fused.show() # DEBUG

    RGBStackConverter.convertToRGB(fused)

    # create new folder if necessary
    outBaseName = outName[0:-4]
    saveDir = File(os.path.join(srcDir.getAbsolutePath(), outBaseName))
    if not saveDir.exists():
        saveDir.mkdir()
    print "Writing to", saveDir.getAbsolutePath()
    IJ.run(fused, "Image Sequence... ", "format=TIFF save=[" + os.path.join(saveDir.getAbsolutePath(), outBaseName + "0000.tif] name=[" + outBaseName +  "]"));
    fused.close()

  # adjust contrast
  # open red channel
  # adjust contrast
  # merge channels
  # convert to RGB
  # save as image sequence in (new) folder
