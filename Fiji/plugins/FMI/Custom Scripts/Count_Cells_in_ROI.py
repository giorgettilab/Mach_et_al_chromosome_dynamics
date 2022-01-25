from ij import IJ, ImagePlus
from ij.measure import ResultsTable
from ij.process import ImageProcessor
from trainableSegmentation import WekaSegmentation

# get current image
imp = IJ.getImage()

# new imp from ROI (taken from Clipboard.java)
imp.copy()
newImp = ImagePlus.getClipboard()
roi = newImp.getRoi()
if roi!=None and roi.isArea():
  roi = roi.clone()
  roi.setLocation(0, 0);
  newImp.setRoi( roi )
  IJ.run(newImp, "Clear Outside", None)
  newImp.deleteRoi()
#newImp.show()

# weka.applyClassifier to imp
weka = WekaSegmentation(newImp)

# classifierFile = "E:\\eglijan\\projects\\kraudomi\\classifier.model"
classifierFile = IJ.getFilePath("Please choose a classifier file")
weka.loadClassifier(classifierFile)

weka.applyClassifier(True)
result = weka.getClassifiedImage()

#result.show()
# TODO get substack (only Cell probablity)

# Gaussian blur 3
IJ.run(result, "Gaussian Blur...", "sigma=3 slice")

#result.show()
# set Threshold(0.5, 1.0)
#IJ.setThreshold(0.5, 1.0)
result.getProcessor().setThreshold(0.5, 1.0, ImageProcessor.NO_LUT_UPDATE)

# find maxima -> count
IJ.run(result, "Find Maxima...", "noise=0.05 output=[Point Selection] above");

# resultsTable add (label, count)
points = result.getRoi()
newImp.show()
newImp.setRoi(points)
# print len(points.getXCoordinates())
rt = ResultsTable.getResultsTable()
rt.incrementCounter()
rt.addLabel(imp.getTitle())
rt.addValue("Number of cells", len(points.getXCoordinates()) )

rt.show("Results")
