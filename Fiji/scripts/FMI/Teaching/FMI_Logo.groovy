#@ OpService ops

import net.imglib2.roi.geom.GeomMasks
import net.imglib2.roi.Masks
import net.imglib2.view.Views
import net.imglib2.FinalInterval
import net.imglib2.realtransform.AffineTransform2D
import net.imglib2.type.numeric.integer.UnsignedByteType

offset = -0.5
outputSize = 100

f = GeomMasks.polygon2D([0, 22, 22, 10, 10, 20, 20, 10, 10, 0] as double[], [0, 0, 9, 9, 13, 13, 21, 21, 32, 32] as double[])
m = GeomMasks.polygon2D([26, 26, 37, 43, 50, 61, 61, 50, 50, 43, 36, 36] as double[], [32, 0, 0, 7, 0, 0, 32, 32, 15, 22, 15, 32] as double[])
i = GeomMasks.polygon2D([65, 76, 76, 65] as double[], [0, 0, 32, 32] as double[])

fmi = f.or(m).or(i)

/* Translate and scale ROI */

transform = new AffineTransform2D()
transform.scale(outputSize / 100)
transform.translate(offset, offset)

transformedRoi = fmi.transform(transform.inverse())


mask = Masks.toRealRandomAccessibleRealInterval(transformedRoi)

img = Views.interval(Views.raster(mask), new FinalInterval(
						[mask.realMin( 0 ), mask.realMin( 1 ) ] as long[],
						[mask.realMax( 0 ), mask.realMax( 1 ) ] as long[] )
)


ops.run("multiply", ops.run("convert.uint8", img), new UnsignedByteType(255))
