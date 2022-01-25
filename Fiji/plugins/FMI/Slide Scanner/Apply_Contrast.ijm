// Written by Moritz.Kirschmann@fmi.ch 2013

contains="merge"; //only file containing this string are processed

requires("1.39u");
inDir = getDirectory("Choose directory images");
//outDir = getDirectory("Choose Directory for TIFF Output ");
outDir = inDir;

Dialog.create("Select number of Channels");
Dialog.addNumber("Number of channels", 5);
Dialog.show();
n_channels=Dialog.getNumber();

setBatchMode(true);
changeThisChannel= newArray(n_channels+1);
mi= newArray(n_channels+1);
ma= newArray(n_channels+1);
for (j=1; j<n_channels+1; j++) {
	Dialog.create("Enter min and max of Channel " +j);
	Dialog.addCheckbox("Change contrast of Channel " +j, false);
	Dialog.addNumber("CH" +j +" min", 0);
	Dialog.addNumber("CH" +j +" max", 15000);
	Dialog.show();
	changeThisChannel[j]=Dialog.getCheckbox();
	mi[j]=Dialog.getNumber();
	ma[j]=Dialog.getNumber();
}
processFiles(inDir, outDir, "", changeThisChannel, mi, ma);
print("-- Done --");

function processFiles(inBase, outBase, sub, ctc, min, max) {
	//print("inbase" +inBase);
  	flattenFolders = false; // this flag controls output directory structure
  	//print("-- Processing folder: " + sub + " --");
  	list = getFileList(inBase + sub);
 	if (!flattenFolders) File.makeDirectory(outBase + sub);
  	for (i=0; i<list.length; i++) {
    		path = sub + list[i];
    		upath = toUpperCase(path);
    		print("list(i)=" +list[i]);
    		//print(startsWith(list[i], "Position_list"));
    		if (endsWith(path, "/")) {
      			// recurse into subdirectories
      			processFiles(inBase, outBase, path, ctc, min, max);
    		}
    		else if (!(indexOf(list[i], contains)==-1)) {
    	
      		print("pos_list found");
      		print("-- Processing file: " + path + " --");
      		print(inBase + path );
		open(inBase + path);
		if (bitDepth()<16) {
			Dialog.create("Enter min and max of Channel" +j);
			Dialog.show();
			waitForUser("WARNING!!! If you continue you will \n modify the oringinal data!");
		}
	
		for (j=1; j<n_channels+1; j++) {
			if (ctc[j]) {
				Stack.setChannel(j);
				setMinAndMax(min[j], max[j]);
			}
		}
		setOption("Changes", false);
		save(inBase + path);	
		close();
      		if (flattenFolders) outFile = replace(replace(outFile, "/", "_"), "Position_list_", "";

      		run("Collect Garbage");
      
    		}
  	}
}