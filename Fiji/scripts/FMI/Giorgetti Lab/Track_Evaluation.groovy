#@ File (style="extensions:xml") xmlFile
#@ fiji.plugin.trackmate.Settings (required=false) tmSettings
#@output avgIoU
#@output avgMatchingSpots
#@output avgMatchingTracks
#@output avgOfTrackMaxIuO

import fiji.plugin.trackmate.io.TmXmlReader
import fiji.plugin.trackmate.SpotCollection
import fiji.plugin.trackmate.tracking.LAPUtils
import fiji.plugin.trackmate.tracking.sparselap.SparseLAPTrackerFactory
import fiji.plugin.trackmate.TrackMate
import fiji.plugin.trackmate.Settings


def getTrackMap(trackModel) {
	tracks = trackModel.trackIDs(true)
	// fill map of GT track IDs
	trackMap = [:]
	
	for (t in tracks) {
		spotMap = [:]
		for (s in trackModel.trackSpots(t)) {
			spotMap[s.getFeature("FRAME") as int] = s.ID()
		}
		trackMap[t] = spotMap.sort()
	}
	return trackMap
}

def defaultSettings() {
	settings = new Settings()
	settings.trackerFactory = new SparseLAPTrackerFactory()
	settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
	settings.trackerSettings[ 'LINKING_MAX_DISTANCE' ]      = 2.5d
    settings.trackerSettings[ 'GAP_CLOSING_MAX_DISTANCE' ]  = 2.5d
    settings.trackerSettings[ 'MAX_FRAME_GAP' ]             = 1
	return settings
}

def runTracking(m) {
	if (tmSettings != null) {
		settings = tmSettings
	} else {
		settings = defaultSettings()
	}
	trackMate = new TrackMate(m, settings)

	if (!trackMate.execTracking()) {
		println trackMate.getErrorMessage()
	}
}

def commonSpots(t1, t2) {
	intersection = 0
	t1.each { frame, id ->
		if (t2[frame] == id) {
			intersection++
		}
	}
	return intersection
}

def computeScore(gtMap, map2) {
	sumIoU = 0
	nTracksGT = 0
	sizeTracksGT = 0
	sumMatchingSpots = 0
	sumMatchingTracks = 0
	sumMaxIoU = 0
	for (track1 in gtMap) {
		maxIoU = 0.0
		nTracksGT++
		sizeTracksGT += track1.value.size()
		//println "Ground truth track $nTracksGT: ${track1.value.size()} spots"
		for (track2 in map2) {
			//println "Comparing track ${track1.key} with ${track2.key}"
			nCommonSpots = commonSpots(track1.value, track2.value)
			if (nCommonSpots > 0) {
				sumMatchingTracks++
				sumMatchingSpots += nCommonSpots
				//println "************ ${track1.key} and ${track2.key} have $nCommonSpots common spots."
				//println "IoU = ${nCommonSpots/(track1.value.size() + track2.value.size())}"
				iou = nCommonSpots/(track1.value.size() + track2.value.size())
				maxIoU = Math.max(maxIoU, iou)
				sumIoU += iou
			}
		}
		sumMaxIoU += maxIoU
	}
	avgMatchingSpots = sumMatchingSpots / sizeTracksGT
	avgMatchingTracks = sumMatchingTracks / nTracksGT
	avgIoU = sumIoU / nTracksGT
	avgOfTrackMaxIuO = sumMaxIoU / nTracksGT
	println "Average IoU = $avgIoU"
	println "Ratio of matched spots per track = $avgMatchingSpots"
	println "Average matched tracks per track = $avgMatchingTracks"
	println "Average maximum IoU per GT track = $avgOfTrackMaxIuO"
}

def readModelFromFile(file) {
	reader = new TmXmlReader(file)
	if (!reader.isReadingOk()) {
		println "Error reading XML file"
		return
	}
	return reader.getModel()
}

// read model from file
model = readModelFromFile(xmlFile)
trackModel = model.getTrackModel()
gtMap = getTrackMap(trackModel)
println "Ground Truth has " + gtMap.size() + " tracks."

// new tracking on model
println "Now retracking"
model.getSpots().setVisible(true)
runTracking(model)
trackModel2 = model.getTrackModel()
newMap = getTrackMap(trackModel2)
println "New tracking has " + newMap.size() + " tracks."

// evaluate tracking, populate outputs
computeScore(gtMap, newMap)
