// Written by Moritz.Kirschmann@fmi.ch 2013
// merges single channel images which are exported via the 
// "original data" option of the slide scanner 

requires("1.39u");
inDir = getDirectory("Choose Directory Containing Files to merge ");
//outDir = getDirectory("Choose Directory for TIFF Output ");
outDir = inDir;
setBatchMode(true);
processFiles(inDir, outDir, "");
print("-- Done --");

function processFiles(inBase, outBase, sub) {
	//print("inbase" +inBase);
	flattenFolders = false; // this flag controls output directory structure NOT IMPLEMENTED !
  	//print("-- Processing folder: " + sub + " --");
  	list = getFileList(inBase + sub);
  	if (!flattenFolders) File.makeDirectory(outBase + sub);
  	for (i=0; i<list.length; i++) {
    		path = sub + list[i];
    		upath = toUpperCase(path);
    		//print("list(i)=" +list[i]);
    		//print(startsWith(list[i], "Position_list"));
    		if (endsWith(path, "/")) {
      			// recurse into subdirectories
      			processFiles(inBase, outBase, path);
    		}
    		else if (endsWith(list[i], "c1_ORG.tif")) {
			print("File found");
			print("-- Processing file: " + path + " --");
			print(inBase + path );
			fullpath=inBase + path;

			// determines the number of channels
			j=2;
			while (File.exists(replace(fullpath,"c1_ORG.tif", "c"+ j+ "_ORG.tif"))) {
				//print("nun  " + replace(fullpath,"c1_ORG.tif", "c"+ j + "_ORG.tif"));
				j=j+1;
			}
	
			n_channels=j-1;
			print("numberofchannels="+n_channels);
			listch= newArray(n_channels+1);
			listch[0]="empty";
			listch[1]=list[i];

			// creation of the channel specific postfix
			for (j=2; j<=n_channels; j++) {
				listch[j]=replace(list[i], "c1_ORG.tif", "c"+ j+ "_ORG.tif");
				print(listch[j]);
			}

			// creation of the string for merging and subsequent merging
			mergestring ="";
			for (j=1; j<=n_channels; j++) {
				open(replace(fullpath,"c1_ORG.tif", "c"+ j+ "_ORG.tif"));
				print("opening " + listch[j]);
				mergestring=mergestring+"c"+j+"=["+ listch[j]+ "] ";
			}
			//mergestring= "c1=" + listch[1] + "c2=" + listch[2] + " c3=" + listch[3] + " c4=" + listch[4] +" c5=" + listch[5] ;
			run("Merge Channels...",  mergestring + " create");
			
  			 // save the resulting merged composite image
      			prep = inBase + path;
      			mertit=replace(prep, "c1_ORG.tif", "");
      
      			mergetitle=mertit+"_merge.tif" ;
      			saveAs("Tiff", mergetitle);

      			//if (flattenFolders) outFile = replace(replace(outFile, "/", "_"), "Position_list_", "";
      			//run("Bio-Formats Exporter", "save=[" + outFile + "] compression=Uncompressed");
      			//close();
      			run("Collect Garbage");
    		}
	}
}