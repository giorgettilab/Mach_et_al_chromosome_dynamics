/**
 * This script assigns cellIDs from a set of segmented frames
 * - first to single spots by selecting the closest segmented frame in time
 * - then to entire tracks by selecting the most frequent spot cellID (except 0)
 */

#@ TrackMate trackmate
#@ ImagePlus imp
#@ String labeledFrames

// Get model/spotmodel/trackmodel from trackmate
model = trackmate.getModel()
spots = model.getSpots()

// get annotated frame list
frameList = parseFrames(labeledFrames)

cal = imp.getCalibration()

// for each spot, look up cellID in closest frame
// put feature CellID
model.beginUpdate()
for (spot in spots.iterable(false)) {
	x = spot.getDoublePosition(0)
	y = spot.getDoublePosition(1)
	frame = (int) spot.getFeature("FRAME")
	targetSlice = getClosestFrame(frame, frameList)
	ip = imp.getImageStack().getProcessor(targetSlice+1)
	spot.putFeature("MANUAL_INTEGER_SPOT_FEATURE", getCellID(ip, x, y, cal))
}
model.endUpdate()


println "Updated spot features."

trackModel = model.getTrackModel()
trackIDs = trackModel.trackIDs(false)
featureModel = model.getFeatureModel()

model.beginUpdate()
for (trackID in trackIDs) {
	trackSpots = trackModel.trackSpots(trackID)
	cellIDs = []
	for (spot in trackSpots) {
		cellIDs << (int) spot.getFeature("MANUAL_INTEGER_SPOT_FEATURE")
	}
	freqMap = cellIDs.countBy {it}
	println freqMap
	// TODO remove 0 from freqMap
	dominantID = freqMap.max{it.value}.key
	println dominantID
	featureModel.putTrackFeature(trackID, "MANUAL_INTEGER_TRACK_FEATURE", dominantID)
}
model.endUpdate()

// for each track, list cellIDs of all spots
// remove zeros
// compute mode (most frequent cellID in track)
// set track cellID

// for each spot in track, set cellID to track cellID

// for each cellID
//   - filter spots
//   - apply registration model (global optimization)

def parseFrames(text) {
	result = text.split(",").collect {
		Integer.parseInt(it)
	}
}

def getClosestFrame(current, list) {
	diffs = list.collect {
		Math.abs(current - it)
	}
	m = diffs.min()
	index = diffs.eachWithIndex { v, i ->
		if (v == m) {
			minIndex = i
		}
	}
	minIndex
}

/**
 * Measure segmentation ID in label image
 */
def getCellID(ip, x, y, cal) {
	return ip.getPixel(Math.round(x / cal.pixelWidth) as int, Math.round(y / cal.pixelHeight) as int)
}
