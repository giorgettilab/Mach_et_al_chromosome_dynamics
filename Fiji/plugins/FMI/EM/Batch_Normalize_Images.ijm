/*
 * Normalize images in a folder and all subfolders
 * to a given mean and standard deviation
 */

input = getDirectory("Input directory");
output = getDirectory("Output directory");

Dialog.create("File type");
Dialog.addString("File_suffix: ", ".tif", 5);
Dialog.addNumber("Mean", 128);
Dialog.addNumber("Standard deviation", 40);
Dialog.show();
suffix = Dialog.getString();
newMean = Dialog.getNumber();
newStd = Dialog.getNumber();

setBatchMode(true);
processFolder(input);

function processFolder(input) {
	list = getFileList(input);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(list[i]))
			processFolder("" + input + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
	}
}

function processFile(input, output, file) {
	open(input + file);
	run("32-bit");
	getRawStatistics(nPixels, mean, min, max, std, histogram);
	run("Subtract...", "value="+mean+" slice");
	run("Divide...", "value="+std+" slice");
	run("Multiply...", "value="+newStd+" slice");
	run("Add...", "value="+newMean+" slice");
	setMinAndMax(0, 255);
	run("8-bit");
	saveAs("TIFF", output + file);
}
