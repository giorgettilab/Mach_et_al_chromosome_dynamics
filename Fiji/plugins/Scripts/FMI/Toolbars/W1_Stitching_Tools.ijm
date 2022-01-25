// Action Bar description file : ND Stitching Tools
IJ.redirectErrorMessages();
eval("run(\"Action Bar\",\"/plugins/Scripts/FMI/Toolbars/W1_Stitching_Tools.ijm\");");
if (!isOpen("W1 Stitching Tools")) exit("Please activate the IBMP-CNRS update site, or contact help.imaging@fmi.ch");
exit();

<text>   Drop an ND file on any of the buttons
<DnD>
<line>
<button>
label=Stitch .nd file MIP
icon=noicon
bgcolor=0
arg=<macro>
run("Stitch nd Dataset");
</macro>
<DnDAction>
file=getArgument();
if (endsWith(file, ".nd")) {
	file = replace(file, "\\\\", "\\\\\\\\");
	run("Stitch nd Dataset", "ndfile=" + file + " domip=true doquick=false");
} else {
	print("This is not an ND file.");
}
</DnDAction>
<button>
label=Stitch .nd file MIP (quick)
icon=noicon
bgcolor=1
arg=<macro>
run("Stitch nd Dataset");
</macro>
<DnDAction>
file=getArgument();
if (endsWith(file, ".nd")) {
	file = replace(file, "\\\\", "\\\\\\\\");
	run("Stitch nd Dataset", "ndfile=" + file + " domip=true doquick=true");
} else {
	print("This is not an ND file.");
}
</DnDAction>
</line>
<line>
<button>
label=Stitch .nd file
icon=noicon
bgcolor=3
arg=<macro>
run("Stitch nd Dataset");
</macro>
<DnDAction>
file=getArgument();
if (endsWith(file, ".nd")) {
	file = replace(file, "\\\\", "\\\\\\\\");
	run("Stitch nd Dataset", "ndfile=" + file + " domip=false doquick=false");
} else {
	print("This is not an ND file.");
}
</DnDAction>
<button>
label=Stitch .nd file (quick)
icon=noicon
bgcolor=4
arg=<macro>
run("Stitch nd Dataset");
</macro>
<DnDAction>
file=getArgument();
if (endsWith(file, ".nd")) {
	file = replace(file, "\\\\", "\\\\\\\\");
	run("Stitch nd Dataset", "ndfile=" + file + " domip=false doquick=true");
} else {
	print("This is not an ND file.");
}
</DnDAction>
</line>
