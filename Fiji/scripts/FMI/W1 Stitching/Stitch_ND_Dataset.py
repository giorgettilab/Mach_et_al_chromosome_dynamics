# @File (label="File to be stitched (.nd)") ndFile
# @boolean (label="Only stitch maximum intensity projection (MIP)") doMIP
# @boolean (label="Quick mode (without overlap computation)") doQuick

import csv, os, re
from ij import IJ
from ij.plugin import ZProjector
from loci.plugins import BF
from loci.plugins.in import ImporterOptions

def getMIP(stackImp):
    """
    Create a maximum intensity projection (MIP) from an ImagePlus stack

    @return ImagePlus maximum projection
    """
    zp = ZProjector(stackImp)
    zp.setMethod(ZProjector.MAX_METHOD)
    zp.setStopSlice(stackImp.getNSlices())
    zp.doHyperStackProjection(False)
    return zp.getProjection()

def doGridStitching(folder, pattern, nd, xSize, ySize, quick):
	######################### Perform stitching
	# temporarily rename ndFile (only if not doMIP and not multichannel)
	tmpPath = nd + ".tmp" # TODO only if pattern ends in ".stk"
	os.rename(nd, tmpPath)
	#print os.path.isfile(tmpPath)
	# stitch files
	#config = "type=[Grid: row-by-row] order=[Right & Down                ]"
	config = "type=[Grid: column-by-column] order=[Down & Right                ]" # always assumed for slide scan files from W1

	IJ.run("Grid/Collection stitching", "" + config + " " +
	"grid_size_x=" + str(xSize) + " grid_size_y=" + str(ySize) + " tile_overlap=20 first_file_index_i=1 " +
	"directory=[" + folder + "] " +
	"file_names=[" + pattern + "] " +
	"output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] " +
	"regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 " +
	("" if quick else "compute_overlap ") +
	"computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]")

	# undo renaming of ndFile
	os.rename(tmpPath, nd)

def writeTileConfig(tileConfPath, tifBaseName, positions, xPos, yPos, dim2d):
	fout = open(tileConfPath, 'w')
	# write header info
	header = "# Define the number of dimensions we are working on\n"
	header += "dim = 2\n" if dim2d else "dim = 3\n"
	header += "\n# Define the image coordinates\n"

	fout.write(header)
	for index, pos in enumerate(positions):
		fout.write(tifBaseName + "_s" + pos + ".tif; ; (" + str(xPos[index]) + ", " + str(yPos[index]) + ("" if dim2d else ", 0") + ")\n")
	fout.close()

def doTileStitching(folder, basename, nd, channelname, ext, quick, dim2d, scaleX, scaleY):
	tileConfPath = os.path.join(folder, basename + "_" + channelname + "_TileConfiguration.txt")
	stgPath = os.path.join(folder, basename[:-1] + ".stg")
	print stgPath
	# Check if TileConfiguration file exists
	if (os.path.exists(tileConfPath)):
		# read folder + basename + channel1? + "_TileConfiguration.txt"
		# Open and parse TileConfiguration.txt file
		f = open(tileConfPath)
		content = f.read()
		f.close()
	
		# Get list of image files for the template
		lines = content.splitlines()

		# TODO
		# factor out file writing to method
		fout = open(os.path.join(folder, basename + "_temp_TileConfiguration.txt"), 'w')
		for line in lines:
			if dim2d:
				line = line.replace("dim = 3", "dim = 2")
				line = line.replace(", 0)", ")")
			line = line.replace(basename + "_" + channelname, basename)
			line = line.replace(".stk", ext)
			fout.write(line + "\n")
		fout.close()
	elif (os.path.exists(stgPath)):
		# read stg file
		f = open(stgPath)
		reader = csv.reader(f)
		positionNames = []
		posX = []
		posY = []
		for row in reader:
			# TODO
			# match row[0] to 'Position(\d+)'
			m = re.match(r'Position(\d+)', row[0])
			if m:
				positionNames.append(m.group(1))
				posX.append(float(row[1])/scaleX)
				posY.append(float(row[2])/scaleY)
		print positionNames
		print "Trying to read stg file:", stgPath
		f.close()
		writeTileConfig(os.path.join(folder, basename + "_temp_TileConfiguration.txt"), basename, positionNames, posX, posY, dim2d)

	# temporarily rename ndFile (only if not doMIP and not multichannel)
	tmpPath = nd + ".tmp" # TODO only if pattern ends in ".stk"
	os.rename(nd, tmpPath)
	# run stitching plugin
	IJ.run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] " +
	"directory=[" + folder + "] " +
	"layout_file=[" + basename + "_temp_TileConfiguration.txt]" + " fusion_method=[Linear Blending] " +
	"regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 " +
	("" if quick else "compute_overlap ") +
	"computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
	# set scale from original
	#IJ.run("Set Scale...", "distance=1 known=" + str(scaleX) + " unit=um")
	#IJ.run(imp, "Properties...", "unit=um pixel_width=" + str(scaleX) + " pixel_height=" + str(scaleX) + " voxel_depth=" + str(scaleX) + "");

	# undo renaming of ndFile
	os.rename(tmpPath, nd)

#################### Initialize info for stitching

# Read file content
ndPath = ndFile.getPath()
#print ndPath
m0 = re.match('(.+[/\\\\])([^/^\\\\]+)\.nd', ndPath)
#print m0.group(1)
folder = m0.group(1)
# folder = ndFile.getParentPath() ??
basename = m0.group(2)

fo = open(ndPath)
reader = csv.reader(fo)

rows = set()
cols = set()
stages = []
channels = dict()
filesToDelete = []

for row in reader:
	if row[0] == "NStagePositions":
		nPos = int(row[1])
	elif row[0] == "DoWave":
		multichannel = row[1].strip() == "TRUE"
	elif row[0] == "DoZSeries":
		zstack = row[1].strip() == "TRUE"
	elif row[0].startswith("WaveName"):
		m3 = re.match('WaveName(\d+)', row[0])
		channels[m3.group(1)] = row[1].strip(" \"")
	elif row[0].startswith("Stage"):
		### match 'Stage(\d+)' to get '_s1' suffix
		m1 = re.match('Stage(\d+)', row[0])
		stages.append(m1.group(1))
		# switch "Row_Col" or "Position"
		if row[1].strip(" \"").startswith("Position"):
			mode = "tiles"
			pass
		else:
			mode = "grid"
			### match row and col
			m2 = re.match('.*Row(\d+)_Col(\d+).*', row[1])
			#print m2.group(1), m2.group(2)
			# TODO determine row-by-row or other setup?
			### add to set
			if m2:
				rows.add(m2.group(1))
				cols.add(m2.group(2))

fo.close()

#print nPos
#print len(rows), len(cols)
print "Stitching mode: ", mode
print "Multichannel:", multichannel
print "Z-Stack:", zstack
print "Do MIPs:", doMIP
print "Quick mode:", doQuick
"""
print channels
print stages
print folder
print basename
for c in channels:
	for s in stages:
		print basename+"_w"+c+channels[c]+"_s"+s+".stk"
"""

######################### Pre-process image files
# load all series from nd file, optionally create MIP, save merged channel files
# "raw" stitching (with tmp-renamed nd) only if not multichannel and not doMIP or not zstack
if (zstack and doMIP) or multichannel:
	print "Resaving intermediate files"
	options = ImporterOptions()
	options.setId(ndPath)
	options.setOpenAllSeries(True)
	# TODO get number of series and loop over each series instead of opening all at once
	imps = BF.openImagePlus(options)
	pixelWidth = imps[0].getCalibration().pixelWidth
	pixelHeight = imps[0].getCalibration().pixelHeight
	fileNamePattern = basename + "_s{i}.tif"
	for imp in imps:
		m4 = re.match('.+Stage(\d+).+', imp.getTitle())
		savePath = folder + basename + "_s" + m4.group(1) + ".tif"
		if doMIP:
			mip = getMIP(imp)
			imp.close()
			print "Saving MIP as", savePath
			IJ.saveAs(mip, "Tiff", savePath);
			mip.close()
		else:
			print "Saving multichannel stack as", savePath
			IJ.saveAs(imp, "Tiff", savePath);
			imp.close()
		filesToDelete.append(savePath)
	if mode == "grid":
		doGridStitching(folder, fileNamePattern, ndPath, len(cols), len(rows), doQuick)
	elif mode == "tiles":
		doTileStitching(folder, basename, ndPath, "w1" + channels['1'], ".tif", doQuick, zstack and doMIP, pixelWidth, pixelHeight)
	# Transfer calibration from original image
	imp = IJ.getImage()
	imp.setCalibration(imps[0].getCalibration())

else:
	# do raw stitching => stitch stk
	fileNamePattern = basename + "_s{i}."
	fileNamePattern += "stk" if zstack else "tif"
	if mode == "grid":
		doGridStitching(folder, fileNamePattern, ndPath, len(cols), len(rows), doQuick)
	elif mode == "tiles":
		doTileStitching(folder, basename, ndPath, "w1" + channels['1'], ".stk", doQuick, True, 1.0, 1.0) # TODO no change in TileConfiguration

# delete intermediate files
print "Deleting temporary files..."
for p in filesToDelete:
	print "Deleting", p
	os.remove(p)
print "Done."
