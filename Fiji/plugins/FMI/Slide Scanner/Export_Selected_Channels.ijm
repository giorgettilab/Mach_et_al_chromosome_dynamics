// Written Moritz.Kirschmann@fmi.ch 2013

contains="merge"; //only files conataining this string in 
// their titles are processed

// dialog for inital paramters
formatchoices = newArray("TIF", "JPEG");
Dialog.create("Export parameters");
Dialog.addNumber("Number of channels in imported images", 5);
Dialog.addChoice("Output file format", formatchoices, formatchoices[0]);
Dialog.addCheckbox("save in input folder", true);
Dialog.show();
n_channels=Dialog.getNumber();
format=Dialog.getChoice();
flatten=!Dialog.getCheckbox();

requires("1.39u");
setBatchMode(true);

inDir = getDirectory("Choose Directory Containing TIFF Files ");
if (flatten) {
	outDir = getDirectory("Choose Directory for TIFF Output ");
}
else {
	outDir = inDir;
}

// dialog for each channel
c= newArray(n_channels+1);
lut=newArray(n_channels+1);
colors = newArray("Red", "Green", "Blue", "Cyan", "Grays", "Magenta", "Yellow");

for (j=1; j<n_channels+1; j++) {
	Dialog.create("CH "+j);
	Dialog.addCheckbox("Export CH" + j, false);
	Dialog.addChoice("Color of CH" + j, colors, colors[j-1]);
	Dialog.show();
	c[j]=Dialog.getCheckbox();
	lut[j]=Dialog.getChoice();
}

// start subfunction
processFiles(inDir, outDir, "", c, flatten);
print("-- Done --");


function processFiles(inBase, outBase, sub, ch, flattenFolders) {

	list = getFileList(inBase + sub);
	// if (!flattenFolders) File.makeDirectory(outBase + sub);
	for (i=0; i<list.length; i++) {
    		path = sub + list[i];
    		upath = toUpperCase(path);

    		if (endsWith(path, "/")) {
			// recurse into subdirectories
			processFiles(inBase, outBase, path, ch, flattenFolders);
    		}
    		//process all files in sub dir: open file, delete unwanted channels and apply LUT
    		else if (!(indexOf(list[i], contains)==-1)) {

			print("found");
			print("-- Processing file: " + path + " --");
			print(inBase + path );
			open(inBase + path);
			run("Make Composite", "display=Composite");
			for (j=n_channels; j>0; j--) {
				if (ch[j]) {
					if (nSlices()>1) {
						Stack.setChannel(j);
					}
					run(lut[j]);
				}
				if (!ch[j]) { 
					if (nSlices>1) {
						Stack.setChannel(j);
					}
					run("Delete Slice", "delete=channel");
				}
			}
			
			// creating title for exported files
			savestring="CH";
			for (j=1; j<n_channels+1; j++) {
				if (ch[j]) {
					//mergestring=mergestring+"c" + j + "=[C" + j + "-" + list[i] + "] ";
					savestring=savestring+"_"+j;
				}
			}


			if (format=="JPEG") {
				//run("8-bit");
				run("RGB Color");
			}

			if (!flattenFolders) {
				savetitle=outBase + replace(replace(path, ".tif", savestring), contains, "") + "."+format;
				print(savetitle);
			}
			else {
				savetitle=outBase + replace(replace(replace(path, ".tif", savestring), contains, "") + "." + format, "/", "_");
				print(savetitle);
			}

			saveAs(format, savetitle);
			close();

      			run("Collect Garbage");
      
    		}
	}
}