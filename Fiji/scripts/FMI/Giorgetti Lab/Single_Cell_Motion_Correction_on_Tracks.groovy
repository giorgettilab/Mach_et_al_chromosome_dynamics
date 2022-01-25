/**
 * This script performs single-cell motion correction
 * by selecting all spots with a given targetCellID
 * and performing descriptor-based registration.
 * 
 * Global optimization of models is performed
 * all-to-all-within-range for a range of 10 frames
 * (i.e. sliding window).
 * 
 * The resulting transformation models per frame
 * are applied to all spots for this cellID
 * and the corrected spot coordinates are written to disk.
 */
#@ TrackMate trackmate
#@ Integer targetCellID
#@ File (style="directory", label = "Directory for output files") outputDir

import mpicbg.imglib.algorithm.scalespace.DifferenceOfGaussian.SpecialPoint
import mpicbg.imglib.algorithm.scalespace.DifferenceOfGaussianPeak
import mpicbg.imglib.type.numeric.real.FloatType
import fiji.plugin.trackmate.features.FeatureFilter
import fiji.plugin.trackmate.Spot
//import fiji.plugin.trackmate.SpotCollection

import plugin.DescriptorParameters
import process.Matching
import mpicbg.models.AffineModel3D
import mpicbg.models.RigidModel3D

// Get all spots of tracks with a given cellID
// (and optionally all orphan spots with that same cell ID?)
// Or: Get all spots with a given cellID (irrespective of track cellID)

model = trackmate.getModel()
cellSpots = model.getSpots()

aboveFilter = new FeatureFilter("MANUAL_INTEGER_SPOT_FEATURE", targetCellID - 0.5, true)
belowFilter = new FeatureFilter("MANUAL_INTEGER_SPOT_FEATURE", targetCellID + 0.5, false)

cellSpots.filter([aboveFilter, belowFilter])
println cellSpots

peakListList = convertSpotsToPeaks(cellSpots)

//println peakListList[0].size

// export (filtered) spots before correction (x,y,z,frame,trackID)
exportSpots(outputDir, "beforeCorrection.csv", cellSpots, model.getTrackModel())

// perform matching and globalOpimization on peaks
nFrames = cellSpots.keySet().size()
params = defaultParameters()
comparePairs = Matching.descriptorMatching(peakListList, nFrames, params, 1.0f)
models = Matching.globalOptimization(comparePairs, nFrames, params)

// different strategy avoiding RANSAC, just iterative filtering for the model
// create ComparePairs


for (frame in cellSpots.keySet()) {
	for (spot in cellSpots.iterable(frame, true)) {
		if (likelyIsIdentity(models[frame])) {
			models[frame] = models[frame-1]
		}
		correctSpot(spot, models[frame])
	}
	println models[frame]
}

// export peak coordinates? linked to spots? re-link to tracks?
exportSpots(outputDir, "afterCorrection.csv", cellSpots, model.getTrackModel())

/**
 * Return true if this model is (likely) an identity transform
 */
def likelyIsIdentity(model) {
	m = new double[12]
	model.toArray(m)
	return (m[0]==1 && m[1]==0 && m[2]==0 && m[3]==0 && m[4]==1 && m[5]==0 &&
		m[6]==0 && m[7]==0 && m[8]==1 && m[9]==0 && m[10]==0 && m[11]==0) 
}

/**
 * Apply a given model to the coordinates of a spot
 */
def correctSpot(spot, model) {
	pos = new double[3]
	spot.localize(pos)
	model.applyInPlace(pos)
	spot.putFeature("POSITION_X", pos[0])
	spot.putFeature("POSITION_Y", pos[1])
	spot.putFeature("POSITION_Z", pos[2])	
}

/**
 * Create DifferenceOfGaussianPeak<FloatType>
 */
def createPeak(dloc, loc) {
	p = new DifferenceOfGaussianPeak<>(loc, new FloatType(), SpecialPoint.MAX)
	p.setSubPixelLocationOffset((float) (dloc[0] - loc[0]), 0)
	p.setSubPixelLocationOffset((float) (dloc[1] - loc[1]), 1)
	p.setSubPixelLocationOffset((float) (dloc[2] - loc[2]), 2)
	//println loc
	return p
}

/**
 * Convert TrackMate Spots to DoGPeaks
 */
def convertSpotsToPeaks(spotCollection) {
	listList = []
	spotCollection.keySet().each { frame ->
		list = []
		loc = new int[3]
		dloc = new double[3]
		spotCollection.iterable(frame, true).each { spot ->
			spot.localize(dloc)
			loc[0] = (int) dloc[0]
			loc[1] = (int) dloc[1]
			loc[2] = (int) dloc[2]
			peak = createPeak(dloc, loc)
			list << peak
		}
		listList << list
	}
	return listList
}

/**
 * Export SpotCollection to CSV
 */
def exportSpots(dir, filename, spots, trackModel) {
	new File(dir, filename).withWriter { writer ->
		writer.writeLine "spotID,frame,x,y,z,trackID"
		spots.iterable(true).each { spot ->
			id = spot.ID()
			frame = (int) spot.getFeature(Spot.FRAME)
			x = spot.getDoublePosition(0)
			y = spot.getDoublePosition(1)
			z = spot.getDoublePosition(2)
			track = trackModel.trackIDOf(spot)
			writer.writeLine "$id,$frame,$x,$y,$z,$track"
		}
	}	
}

/**
 * Default Registration Parameters
 */
def defaultParameters() {
	DescriptorParameters params = new DescriptorParameters()
	params.model = new RigidModel3D()
	params.dimensionality = 3
	//params.localization = 1
	params.numNeighbors = 2
	params.significance = 3
	params.similarOrientation = true
	params.ransacThreshold = 3
	//params.channel1 = 0
	//params.channel2 = 0
	params.redundancy = 3
	//params.fuse = 2; // no Overlay image
	params.globalOpt = 1
	params.range = 10
	return params
}
