from java.lang import Integer
from java.util import UUID

from ij import IJ, Prefs
from ij.gui import Overlay, Roi, TextRoi
from ij.measure import ResultsTable
from ij.plugin import Duplicator, HyperStackConverter

from fiji.util.gui import GenericDialogPlus

from loci.common import Region
from loci.plugins import BF
from loci.plugins.in import ImporterOptions
from trainableSegmentation import WekaSegmentation
from graphcut import Graph_Cut
from Utilities import Counter3D

gd = GenericDialogPlus("Neuronal Cell Intensity")
gd.addFileField("Imaris_file", "")
gd.addFileField("Coarse_Classifier", "")
gd.addFileField("Fine_Classifier", "")

gd.showDialog()


## load series_3 from ims file
# imp = IJ.getImage() # TODO use bio-formats importer

path = gd.getNextString()
coarseClassifierFile = gd.getNextString()
fineClassifierFile = gd.getNextString()

options = ImporterOptions()
options.setId(path)
options.setSeriesOn(2, True)

imps = BF.openImagePlus(options)
print imps
imps[0].show()
# IJ.run("Bio-Formats Importer", "open=E:\\eglijan\\projects\\matvolga\\a5_hp__E7_4_e2_low_C0.a5_hp.Tile_1.lsm_stitched_down.ims autoscale color_mode=Default view=Hyperstack stack_order=XYCZT series_1");

## apply classifier to image and get probability map
weka = WekaSegmentation(imps[0])

weka.loadClassifier(coarseClassifierFile)

weka.applyClassifier(True)
probs = weka.getClassifiedImage()

# stack to hyperstack (TODO get substack, only class 1)
probs = HyperStackConverter.toHyperStack(probs, 2, imps[0].getImageStackSize(), 1)
probs = Duplicator().run(probs, 1, 1, 1, probs.getNSlices(), 1, probs.getNFrames() )
probs.setDisplayMode(IJ.GRAYSCALE)
#IJ.setMinAndMax(probs, 0.0, 1.0);

# apply calibration from original? (fix pending)
# probs.setCalibration( imps[0].getCalibration() ) # fix pending
probs.show()

## graph cut segmentation
gc = Graph_Cut() # needs 8-bit, fix pending for 32-bit
cells = gc.processSingleChannelImage(probs, None, 0.9, 0.5, 0) # 0.9 "threshold", 0.5 edge weight -> smoothness
cells.setCalibration( probs.getCalibration() ) # fix pending
IJ.run(cells, "Invert", "stack")
cells.show()

## analyze particles (no, 2D only) -> Counter3D find centers of mass
oc = Counter3D(cells, 128)
centroids = oc.getCentroidList() # always pixel units (fix 3D_Objects_counter?)

## open cropped volumes
boxDims = [300, 300, 10]
maxX = imps[0].getWidth() * 4
maxY = imps[0].getHeight() * 4
maxZ = imps[0].getNSlices()

ovl = Overlay()
rt = ResultsTable.getResultsTable()

options.setSeriesOn(2, False)
options.setSeriesOn(0, True)

bigImps = BF.openImagePlus(options)

options.setCrop(True)

for cent in centroids:
  #print cent
  
  x = cent[0] * 4
  y = cent[1] * 4
  z = cent[2]

  rX = max( int(round(x - (boxDims[0]/2))), 0 )
  rY = max( int(round(y - (boxDims[1]/2))), 0 )
  r = Region(rX, rY , min(boxDims[0], maxX - rX), min(boxDims[1], maxY - rY) )
  #print r
  options.setCropRegion(0, r)
  options.setZBegin(0, int(max(1, z - (boxDims[2]/2))) - 1 )
  options.setZEnd(0, int(min(maxZ, z + (boxDims[2]/2))) - 1 )

  impCell = BF.openImagePlus(options)
  # apply fine classifier
  wekaFine = WekaSegmentation(impCell[0])

  wekaFine.loadClassifier(fineClassifierFile)
  wekaFine.applyClassifier(False)
  cellVolume = wekaFine.getClassifiedImage()

  # measure (3D) intensity (mask, redirect to original)
  # ignore objects at the border!
  # 3D OC options: redirect to
  # Counter3D measure mean
  IJ.setMinAndMax(cellVolume, 0.0, 1.0)
  IJ.run(cellVolume, "16-bit", "")
  IJ.run(cellVolume, "Invert", "stack")
  # set unique image name for 3DCounter redirection
  uid = UUID.randomUUID().toString()
  impCell[0].setTitle(uid)
  Prefs.set("3D-OC-Options_redirectTo.string", uid)
  impCell[0].show()
  cellVolume.show()
  
  oc2 = Counter3D(cellVolume, 1, 1000, boxDims[0]*boxDims[1]*boxDims[2], False, True)
  for obj in oc2.getObjectsList():
    if obj.bound_cube_TL[0] > 0 and obj.bound_cube_TL[1] > 0 and obj.bound_cube_BR[0] < cellVolume.getWidth()-1 and obj.bound_cube_BR[1] < cellVolume.getHeight()-1:
      rectRoi = Roi(rX + obj.bound_cube_TL[0], rY + obj.bound_cube_TL[1], obj.bound_cube_width, obj.bound_cube_height)
      ovl.add(rectRoi)
      textRoi = TextRoi(2 + rX + obj.bound_cube_TL[0], rY + obj.bound_cube_TL[1], IJ.d2s(obj.mean_gray) )
      ovl.add(textRoi)
      rt.incrementCounter()
      rt.addLabel(imps[0].getTitle())
      rt.addValue("X", rX + obj.centroid[0])
      rt.addValue("Y", rY + obj.centroid[1])
      rt.addValue("Mean intensity", obj.mean_gray)
      #print "Object:", obj.bound_cube_TL, obj.bound_cube_BR, obj.size
      #print "Mean value (redirected):", obj.mean_gray

# plot outline and intensity value onto MIP of (full resolution?) image
#IJ.run(bigImps[0], "Z Project...", "projection=[Max Intensity]")
bigImps[0].setOverlay(ovl)
bigImps[0].show()
IJ.run(bigImps[0], "parula", "")
rt.setDecimalPlaces(0,0)
rt.setDecimalPlaces(1,0)
rt.setDecimalPlaces(2,1)
rt.show("Results")
