#@ ImagePlus (label = "Input stack for spot detection") imp
#@ ImagePlus (label = "Initial cell segmentation") labelImage
#@ Integer (label = "Labels belong to frame (0-indexed)", value = 0) labelFrame
#@ Integer (label = "Minimal number of inliers per pair of frames", value = 10) minInliers
#@ File (style="directory", label = "Directory for output files") outputDir
#@ String (label = "File name for list of all spots", value = "allSpots.csv") spotsFilename

#@ ObjectService os
#@ TrackMate trackMate

import fiji.plugin.trackmate.Spot

import mpicbg.imglib.algorithm.scalespace.DifferenceOfGaussian.SpecialPoint
import mpicbg.imglib.algorithm.scalespace.DifferenceOfGaussianPeak
import mpicbg.imglib.type.numeric.real.FloatType
import mpicbg.models.RigidModel3D
import mpicbg.models.PointMatch

import plugin.DescriptorParameters
import process.Matching

import com.google.common.collect.Lists

// get Model and SpotCollection
model = trackMate.getModel()
spots = model.getSpots()

// perform registration




peakListList = convertSpotsToPeaks(spots, imp.getNFrames())
// labelMap = createLabelMapping(peakListList[labelFrame], labelImage, imp.getCalibration())

comparePairs = Matching.descriptorMatching(peakListList, imp.getNFrames(), defaultParameters(), 1.0f)
//models = Matching.globalOptimization(comparePairs, imp.getNFrames(), defaultParameters())

model.beginUpdate()
comparePairs.each { pair ->
	if (pair.inliers.size < minInliers) return
	thisFrameSpotList = Lists.newArrayList(spots.iterable(pair.indexA, false))
	otherFrameSpotList = Lists.newArrayList(spots.iterable(pair.indexB, false))
	pair.inliers.each { pointMatch ->
		thisFrameIndex = pointMatch.getP1().getID()
		otherFrameIndex = pointMatch.getP2().getID() - peakListList[pair.indexA].size()
		
		model.addEdge(thisFrameSpotList.get(thisFrameIndex as int), otherFrameSpotList.get(otherFrameIndex as int), -1)
	}
}
model.endUpdate()

// TODO export graph at this point
// export spotID, x,y,z, trackID, cellID
exportSpotsWithCellID(outputDir, spotsFilename, spots, model.getTrackModel(), labelImage.getProcessor(), imp.getCalibration())

// TODO add track feature for cellID
updateCellIDs(labelImage, spots.iterable(labelFrame, false), model, imp.getCalibration())

/**
 * Export SpotCollection with CellID (for all spots) to CSV
 * 
 * NB: we are ignoring labelFrame here!
 */
def exportSpotsWithCellID(dir, filename, spots, trackModel, ip, cal) {
	new File(dir, filename).withWriter { writer ->
		writer.writeLine "spotID,frame,x,y,z,trackID,cellID"
		spots.iterable(false).each { spot ->
			id = spot.ID()
			frame = (int) spot.getFeature(Spot.FRAME)
			x = spot.getDoublePosition(0)
			y = spot.getDoublePosition(1)
			z = spot.getDoublePosition(2)
			track = trackModel.trackIDOf(spot)
			cell = getCellID(ip, x, y, cal)
			writer.writeLine "$id,$frame,$x,$y,$z,$track,$cell"
		}
	}	
}

/**
 * Measure segmentation ID in label image
 */
def getCellID(ip, x, y, cal) {
	return ip.getPixel(Math.round(x / cal.pixelWidth) as int, Math.round(y / cal.pixelHeight) as int)
}

/**
 * Update Track Features with Cell IDs
 */
def updateCellIDs(imp, spots, model, cal) {
	model.beginUpdate()
	featureModel = model.getFeatureModel()
	trackModel = model.getTrackModel()
	ip = labelImage.getProcessor()
	spots.each { s->
		track = trackModel.trackIDOf(s)
		if (track!=null) {
			cellID = getCellID(ip, s.getDoublePosition(0), s.getDoublePosition(1), cal)
			// FIXME use manual track feature instead of messing with TRACK_ID
			featureModel.putTrackFeature(track, "TRACK_ID", (int) cellID *10000 + track)
		}
	}
	model.endUpdate()
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
def convertSpotsToPeaks(spotCollection, nFrames) {
	listList = []
	nFrames.times { frame ->
		list = []
		loc = new int[3]
		dloc = new double[3]
		spotCollection.iterable(frame, false).each { spot ->
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
 * Default Registration Parameters
 */
def defaultParameters() {
	DescriptorParameters params = new DescriptorParameters()
	params.model = new RigidModel3D()
	params.dimensionality = 3
	//params.localization = 1
	params.numNeighbors = 3
	params.significance = 3
	params.similarOrientation = true
	params.ransacThreshold = 5
	//params.channel1 = 0
	//params.channel2 = 0
	params.redundancy = 1
	//params.fuse = 2; // no Overlay image
	params.globalOpt = 1
	params.range = 10
	return params
}
