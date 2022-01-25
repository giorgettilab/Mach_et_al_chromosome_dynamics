/*
 * Macro template to process multiple images in a folder
 */

input = getDirectory("Input directory");
output = getDirectory("Output directory");

Dialog.create("File type");
Dialog.addString("File suffix: ", ".nd", 5);
Dialog.show();
suffix = Dialog.getString();

setBatchMode(true);
processFolder(input);
setBatchMode(false);

function processFolder(input) {
	list = getFileList(input);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + list[i]))
			processFolder("" + input + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
	}
}

function processFile(input, output, file) {
	print("Processing: " + input + file);
	IJ.redirectErrorMessages();
	run("Stitch ND Dataset", "ndfile=[" + input + file + "] domip=false doquick=false");
	print("Saving to: " + output);
	if (isOpen("Fused")) {
		run("Bio-Formats Exporter", "save=[" + output + file + ".ids]");
		close();
	}
}
