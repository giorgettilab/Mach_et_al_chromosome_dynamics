#@ String (choices={"horizontal", "vertical", "diagonal"}) direction
#@ Double (value=10) frequency
#@ Long (label="Image Size", value=256) size
// disabled #@ Double (label="Noise Level", value=0) noise
#@ OpService ops

result = ops.run("create.img", [size, size])
switch (direction) {
	case "horizontal":
		formula = {x,y -> 255*(Math.cos((y)/(size/(frequency*2*Math.PI)))/2+0.5)}
		break
	case "vertical":
		formula = {x,y -> 255*(Math.cos((x)/(size/(frequency*2*Math.PI)))/2+0.5)}
		break
	case "diagonal":
		formula = {x,y -> 255*(Math.cos((x+y)/(size/(frequency*2*Math.PI)))/2+0.5)}
		break
}

ops.image().equation(result, formula)

//noiseOp = ops.op("addNoise", result.firstElement(), result.firstElement(), 0d, 255d, noise)
//noisy = ops.run("create.img", result)
//ops.run("map", noisy, result, noiseOp)
