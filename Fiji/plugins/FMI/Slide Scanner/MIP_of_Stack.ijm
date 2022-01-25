// Written by Moritz.Kirschmann@fmi.ch 2013

contains="Z001.tif"; //only file containing this string are processed

requires("1.39u");
inDir = getDirectory("Choose directory");
//outDir = getDirectory("Choose Directory for TIFF Output ");
outDir = inDir;

Dialog.create("Select number of Channels");
Dialog.addNumber("Number of channels", 3);
Dialog.show();
n_channels=Dialog.getNumber();

setBatchMode(true);
//changeThisChannel= newArray(n_channels+1);
//mi= newArray(n_channels+1);
//ma= newArray(n_channels+1);
/*for (j=1; j<n_channels+1; j++) {
	Dialog.create("Enter min and max of Channel " +j);
	Dialog.addCheckbox("Change contrast of Channel " +j, false);
	Dialog.addNumber("CH" +j +" min", 0);
	Dialog.addNumber("CH" +j +" max", 15000);
	Dialog.show();
	changeThisChannel[j]=Dialog.getCheckbox();
	mi[j]=Dialog.getNumber();
	ma[j]=Dialog.getNumber();
}
*/
processFiles(inDir, "", n_channels);
print("-- Done --");

function processFiles(inBase, sub, nch) {
	//print("inbase" +inBase);
  	flattenFolders = false; // this flag controls output directory structure
  	//print("-- Processing folder: " + sub + " --");
  	list = getFileList(inBase + sub);
 	//if (!flattenFolders) File.makeDirectory(outBase + sub);
  	for (i=0; i<list.length; i++) {

    		path = sub + list[i];
    		upath = toUpperCase(path);
    		print("list(i)=" +list[i]);
    		//print(startsWith(list[i], "Position_list"));
    		if (endsWith(path, "/")) {
      			// recurse into subdirectories
      			processFiles(inBase, path, nch);
    		} 
    		else if (!(indexOf(list[i], contains)==-1)) {
    			print("-- Processing file: " + path + " --");
    			for (j=1; j<n_channels+1; j++) {
				run("Image Sequence...", "open=" + inBase + replace(path,"C001", "C00" + j) + " starting=1 increment=1 scale=100 file=C00" + j + " sort");
				//seqDim = getDimensions(slices);
				title=getTitle();
				dire=getDirectory("image");
				run("Z Project...", "start=1 stop="+nSlices+" projection=[Max Intensity]");
				//print("savepath "+inBase + title+ "_MIP.tif");
				//print("composed from dire "+dire);
				//print("and title "+replace(title, ".tif", "MIP.tif"));
				saveAs("Tiff", inBase + title+ "_CH"+j+"_MIP.tif");
				run("Close All");
			}
      			
      			print(inBase + path );
			//run("Image Sequence...", "open="+inBase+path starting=1 increment=1 scale=100 file=C001 sort");
		
	
		
			//close();
      		

      			run("Collect Garbage");
    			}
    		}
  	}
