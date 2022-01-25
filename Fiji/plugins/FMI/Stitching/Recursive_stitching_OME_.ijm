// Written by Moritz.Kirschmann@fmi.ch 2013

// stitches all mosaics assosiated with Position list files found within a folder.
// If you use the Matlab xuvtoposlist_3D.m converter use this script.


requires("1.39u");
inDir = getDirectory("Choose Directory Containing Position List Files ");
outDir = getDirectory("Choose Directory for Mosaic Output ");
//outDir = inDir;
setBatchMode(true);
processFiles(inDir, outDir, "");
print("-- Done --");

function processFiles(inBase, outBase, sub) {
  print("inbase" +inBase);
  flattenFolders = true; // this flag controls output directory structure
  print("-- Processing folder: " + sub + " --");
  list = getFileList(inBase + sub);
  //if (!flattenFolders) File.makeDirectory(outBase + sub);
  for (i=0; i<list.length; i++) {
    path = sub + list[i];
    upath = toUpperCase(path);
    print("list(i)=" +list[i]);
    print(startsWith(list[i], "Position_list"));
    if (endsWith(path, "/")) {
      // recurse into subdirectories
      processFiles(inBase, outBase, path);
    }
    else if ((startsWith(list[i], "Position_list")) && !(endsWith(list[i], "registered.txt"))) {
      print("pos_list found");
      print("-- Processing file: " + path + " --");
      print(inBase + path );
      
      	run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=[" + inBase+ sub + "] layout_file=[" + list[i] + "] fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
      //run("Bio-Formats Importer", "open='" + inBase + path + "' color_mode=Default view=[Standard ImageJ] stack_order=Default use_virtual_stack");
          		// create a mosaic name form the 
		poslisttext=File.openAsString(inBase+path);
		
     		notfound=true;
  		m1=0;
      		while (notfound) {
      	
      			m1=indexOf(poslisttext, "\n", m1);
      			m2=indexOf(poslisttext, "\n", m1+1);
			nameofmosaic=substring(poslisttext, m1 , m2);
      			print(nameofmosaic);
      			if (!startsWith(nameofmosaic, "#") && (endsWith(nameofmosaic, ")")) ) {
      				notfound=false;
      				m3=indexOf(nameofmosaic, "; ");
      				m4=1;
      				/*
      				if (indexOf(nameofmosaic, "/")>-1) {
      					m4=indexOf(nameofmosaic, "/");
      				}
      				*/
      				nameofmosaic=substring(nameofmosaic,m4, m3);
      				nameofmosaic=nameofmosaic;
      				nameofmosaic=replace(nameofmosaic,"/","__");
      				nameofmosaic=nameofmosaic+"_stitched.ome.tif";
      				// was before >                                      nameofmosaic=substring(nameofmosaic,m4+1, m3);
      				print("name is : "+nameofmosaic);
      				//print("save path is: "+replace(outBase +path+ nameofmosaic , suf, "_stitched.ome.tif"));
      			}
      			m1++;
      		}
      

      
      if (!(flattenFolders)) {
	  run("Bio-Formats Exporter", "save=[" + outBase + nameofmosaic + "] write_each_channel compression=Uncompressed");
      //saveAs("Tiff", outBase + nameofmosaic);
      close();
      print(path);
    }
      //outFile = outBase + replace(path, 'lsm', '') + 'tif' ;
      else { 
      	run("Bio-Formats Exporter", "save=[" + outBase + nameofmosaic + "] write_each_channel compression=Uncompressed");
      	//saveAs("Tiff", outBase + nameofmosaic);
      	//saveAs("Tiff", replace(replace(replace(outBase + path , ".txt", "_stitched.tif"), "Position_list_", ""), "/", "_" ));
      close();
      print(path);
      }
      //outFile = replace(replace(outFile, "/", "_"), "Position_list_", "";
      //run("Bio-Formats Exporter", "save=[" + outFile + "] compression=Uncompressed");
      //close();
      run("Collect Garbage");
    }
  }
}