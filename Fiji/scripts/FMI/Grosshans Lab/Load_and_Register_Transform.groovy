#@ ObjectService os
#@ IOService io
#@ StatusService ss
#@ File transformFile

transform = io.open(transformFile.getAbsolutePath())
if (transform != null) {
	os.addObject(transform, transformFile.getName())
	ss.showStatus("Transform ${transformFile.getName()} successfully registered.")
}
