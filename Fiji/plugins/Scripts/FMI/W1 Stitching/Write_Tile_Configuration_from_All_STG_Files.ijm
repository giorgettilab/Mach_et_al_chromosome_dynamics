// @File(label = "Input directory", style = "directory") input
// @String(label = "File suffix", value = ".stg") suffix
// @double(label = "Pixel size of nd dataset") pixelSize

processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder("" + input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, list[i]);
	}
}

function processFile(input, file) {
	// Do the processing here by adding your own code.
	// Leave the print statements until things work, then remove them.
	print("Processing: " + input + File.separator + file);
	run("Write Tile Configuration from STG File", "log=[org.scijava.log.StderrLogService [priority = -100.0]] fs=[io.scif.services.DefaultFormatService [priority = 0.0]] stgfile=[" + input + File.separator +file + "] override=true pixelsize=" + pixelSize);
}
