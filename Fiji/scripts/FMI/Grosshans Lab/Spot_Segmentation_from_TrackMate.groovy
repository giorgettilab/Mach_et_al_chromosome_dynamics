#@ Dataset img
#@ TrackMate trackmate
#@ OpService ops
#@ ConvertService cs
#@ DatasetService ds
#@output resultImp

import ij.ImagePlus
import net.imglib2.algorithm.dog.DifferenceOfGaussian

/*
 * Segment image taking spots as seeds
 */
// Get calibration
xSpacing = img.averageScale(0)
ySpacing = img.averageScale(1)
zSpacing = img.averageScale(2)

// Generate spot mask
spotImg = ops.create().img(img)

randomAccess = spotImg.randomAccess()

for (spot in trackmate.getModel().getSpots().iterable(true)) {
	randomAccess.setPosition(spot.getDoublePosition(0) / xSpacing as long, 0)
	randomAccess.setPosition(spot.getDoublePosition(1) / ySpacing as long, 1)
	randomAccess.setPosition(spot.getDoublePosition(2) / zSpacing as long, 2)

	randomAccess.get().setReal(1.0)
}

// Convert to ImagePlus for MorphoLibJ
type = ops.create().integerType(255)
spots = ops.create().img(spotImg, type)
ops.convert().imageType(spots, spotImg, ops.op("normalizeScale", spots.firstElement(), spotImg.firstElement()))

spotImp = cs.convert(spots, ImagePlus.class)
println spotImp
spotImp.setTitle("spots")
// we need to duplicate to get rid of the virtual stack (for MorphoLibJ)
spotImp2 = spotImp.duplicate()

// Get radius setting from spot collection
radius = trackmate.getSettings().detectorSettings.get('RADIUS')
println "radius: $radius"

// DoG filter image
converted = ops.run("convert.float32", img)
sigma1 = radius / Math.sqrt( img.numDimensions() ) * 0.9
sigma2 = radius / Math.sqrt( img.numDimensions() ) * 1.1

sigmas = DifferenceOfGaussian.computeSigmas( 0.5, 2, [xSpacing, ySpacing, zSpacing] as double[], sigma1, sigma2 )

filtered = ops.run("filter.dog", converted, sigmas[0], sigmas[1])

type = ops.create().integerType(255)
result = ops.create().img(filtered, type)
ops.convert().imageType(result, filtered, ops.op("normalizeScale", result.firstElement(), filtered.firstElement()))

dogImp = cs.convert(result, ImagePlus.class)
println dogImp
dogImp.setTitle("filtered")
// we need to duplicate to get rid of the virtual stack (for MorphoLibJ)
dogImp2 = dogImp.duplicate()

// Impose maxima/minima
import inra.ijpb.morphology.MinimaAndMaxima3D

imposedMinima = MinimaAndMaxima3D.imposeMinima( dogImp2.getStack(), spotImp2.getStack())
extendedMinima = MinimaAndMaxima3D.extendedMinima( imposedMinima, 150.0 )

resultImp = new ImagePlus("Segmented Spots", extendedMinima)
//resultImp.show()
