S = File.separator;
getMinAndMax(hMin, hMax);
ImageSource = getTitle();
setTool("zoom");

//_______________________Functions________________________________

function FindMaxima(Zcurrent, ZsearchRange, Xloc, Yloc, Xrange, Yrange) {
Maxstack=0; Minstack=65500; OptSlice=0; Max=0;
for (i=floor(Zcurrent-ZsearchRange/2)+1; i<floor(Zcurrent+ZsearchRange/2)+1; i++) {
	setSlice(maxOf(i, 1));
	makeRectangle(Xloc-floor(Xrange/2), Yloc-floor(Yrange/2), Xrange, Yrange);
	getStatistics(area, mean, min, max, std, histogram);
	if (max>Maxstack) {
		Maxstack=max;
		Minstack=min;
		OptSlice=i;
		}}
setSlice(OptSlice);
for (i=round(Xloc-Xrange/2); i<round(Xloc+Xrange/2); i++) {
	for (j=round(Yloc-Yrange/2); j<round(Yloc+Yrange/2); j++) {
		PixelValue=getPixel(i,j);
		if (PixelValue==Maxstack) {
			x2=i; y2=j;
		}}}
setMinAndMax(Minstack, Maxstack);
FindMaximaArray = newArray (x2, y2, OptSlice);
return FindMaximaArray;
}


//_______________________Format date______________________________

dateFileModif = File.dateLastModified(File.directory+File.name);
monthArray = newArray("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");
monthString = "JanFebMarAprMayJunJulAugSepOctNovDec";
monthNumber = (indexOf(monthString, substring(dateFileModif, 4, 7)))/3+1;
date = substring(dateFileModif, 8, 10)+"-"+monthNumber+"-"+substring(dateFileModif, lengthOf(dateFileModif)-4);

//_______________________Test location of user FMI vs. not FMI___________

pathTest=S+S+"imagestore"+S+"FAIM"+S+"Maintenance_All microscopes"+S+"TestFMI_DoNotMove.txt";
Loc = "";
if (File.exists(pathTest) == 1) Loc="FMI";


//_______________________Retrieve last saved Info________________________

microscope="microscope";
MA=100;
NA=1.4;
ImageName = getInfo("image.filename");
choice = 1;
choiceClose = 1;
choiceValues = 1;
LineThickness = 1;
choiceBead = 1;
Xrange = 12;
Yrange = 12;
Zrange = 12;

Directory = getDirectory("imagej");
path = Directory+"LogFileImageJ.txt";
index = newArray(30); index[0] = 0;
indexCount = 1; position = 0;
if (File.exists(path)==1) {
    Info = File.openAsString(path);
    if (Info!="") {
        firstK=substring(Info, 0, 1);
        if (firstK!="~") {
        	while (position<lengthOf(Info)-1) {
        		position = indexOf(Info, ";", index[indexCount-1])+1;
        		index[indexCount]= position;
        		indexCount = indexCount + 1;
        	}
	if (indexCount<17) exit("You must delete the old LogFileImageJ.txt\nin the Fiji folder");
               
        microscope=substring(Info, 0, index[1]-1);
        MA=substring(Info, index[1], index[2]-1);
        NA=substring(Info, index[2], index[3]-1);
        xyVoxel=substring(Info, index[3], index[4]-1);
        zVoxel=substring(Info, index[4], index[5]-1);
        UnitXY=substring(Info, index[6], index[7]-1);
        UnitZ=substring(Info, index[7], index[7]+1);
        choice=substring(Info, index[8], index[8]+1);
        choiceClose=substring(Info, index[9], index[9]+1);
        choiceValues=substring(Info, index[10], index[10]+1);
        choiceBead=substring(Info, index[11], index[11]+8);
        Xrange=substring(Info, index[12], index[13]-1);
        Yrange=substring(Info, index[13], index[14]-1);
        Zrange=substring(Info, index[14], index[15]-1);
        LineThickness=substring(Info, index[15], index[16]-1);
        
        }
    }
}
// _______________________Looping_____________________________________
/*
Looping=0;
while (Looping==0) {
selectWindow(ImageSource);
*/
// _______________________Get info on the setup_______________________

getVoxelSize(xyVoxel_Info, height, zVoxel_Info, unit_Info);
xyVoxel=xyVoxel_Info;
zVoxel=zVoxel_Info;
UnitXY = unit_Info;
UnitZ = unit_Info;
Unit = newArray("uM", "nm");
micList = newArray("Miescher", "Friedrich", "Euler", "LSM710", "SD1", "SIM", "TIRF", "Z1", "Franklin", "Johnson", "Levi", "Merian", "Other");
Dialog.create("Image information");
//  Dialog.addString("Microscope Name:", microscope);
  Dialog.addChoice("Microscope", micList, microscope);
  Dialog.addNumber("Magnification:", MA);
  Dialog.addString("NA:", NA);
  Dialog.addNumber("Pixel size :", xyVoxel);
  Dialog.addChoice("Unit", Unit, unit_Info);
  Dialog.addNumber("Distance between stacks :", zVoxel)
  Dialog.addChoice("Unit", Unit, unit_Info);
  Dialog.addString("Date (dd-mm-yyyy):", date);
  Dialog.addCheckbox("Automatic selection of bead", choice);
  Dialog.addCheckbox("Close source image when done", choiceClose);
  Dialog.addCheckbox("Display theoretical values", choiceValues);
  Dialog.addNumber("FWHMl estimation over (pixels):", LineThickness);
  Dialog.addMessage("Credits: Laurent Gelman, Friedrich Miescher Institut, Basel");
  
Dialog.show();
  microscope = Dialog.getChoice();
  MA = Dialog.getNumber();
  NA = Dialog.getString();
  xyVoxel = Dialog.getNumber();
  UnitStackXY = Dialog.getChoice();
  zVoxel=Dialog.getNumber();
  UnitStackZ = Dialog.getChoice();
  date = Dialog.getString();
  choice = Dialog.getCheckbox();
  choiceClose = Dialog.getCheckbox();
  choiceValues = Dialog.getCheckbox();
  LineThickness = Dialog.getNumber();

if (UnitStackXY==Unit[0]) xyVoxel=xyVoxel*1000;
if (UnitStackZ==Unit[0]) zVoxel=zVoxel*1000;

if (choice==false) {
  CheckBox = newArray("a pixel ", "a region");
  Dialog.create("Type of selection");
  Dialog.addMessage("The bead will be selected by the user by right-clicking on it.\nThe pixel clicked by the user can be:\n- The center of the bead.\n- The center of a small region (12x12 pixel in 8 adjacent planes) where the macro looks for a local maximum.");
  Dialog.setInsets(0, 40, 0);
  Dialog.addChoice("The mouse points to", CheckBox, choiceBead);
  Dialog.addMessage("If the mouse points to a region, please indicate:");
  Dialog.setInsets(0, 40, 0);
  Dialog.addNumber("Search range for XY (in pixels):", Xrange);
  Dialog.setInsets(0, 40, 0);
  Dialog.addNumber("Search range for Z (in planes):", Zrange);
  Dialog.show();
  choiceBead = Dialog.getChoice();
  Xrange = Dialog.getNumber();  Yrange = Xrange;
  Zrange = Dialog.getNumber();
}


//________________________Save Info on setup____________________________

Info = microscope+";"+MA+";"+NA+";"+xyVoxel+";"+zVoxel+";"+date+";"+UnitXY+";"+UnitZ+";"+choice+";"+choiceClose+";"+choiceValues+";"+choiceBead+";"+Xrange+";"+Yrange+";"+Zrange+";"+LineThickness+"; ; ; ; ; ; ; ; ;";
File.saveString(Info, path);


//________________________Change image properties________________________

ImageName = getInfo("image.filename");
MainName=ImageSource+"_"+date+"_"+microscope+"_"+MA+"x_"+NA;
setVoxelSize(xyVoxel, xyVoxel, zVoxel, "nm");
Stack.getPosition(channel, slice, frame);
run("Duplicate...", "duplicate range=1-"+nSlices);
rename("Stack");
Stack.setSlice(slice);
setMinAndMax(hMin,hMax);
if (choiceClose==1) {
	selectWindow(ImageSource);
	close();
	}

// _______________Select the slice with highest intensity and crop_________________

selectWindow("Stack");
setMinAndMax(hMin, hMax);
MaxPixel = newArray(3);
if (choice==false) {
		boucle=true;
		flags=1;
		while (boucle==true) {
		getCursorLoc(xLoc, yLoc, zLoc, flags);
		if (flags==4) boucle=false;
		}
		if (choiceBead == "a pixel ") {	
		x2=xLoc; y2=yLoc; OptSlice=zLoc+1;
		MaxPixel[0] = x2; MaxPixel[1] = y2; MaxPixel[2] = OptSlice;
		} else {
		MaxPixel = FindMaxima(zLoc+1, Zrange, xLoc, yLoc, Xrange, Yrange);
		x2 = MaxPixel[0]; y2 = MaxPixel[1]; OptSlice = MaxPixel[2];
		}
	} else {
	Stack.getDimensions(width, height, channels, slices, frames);
	MaxPixel = FindMaxima(floor(slices/2), slices, floor(width/2), floor(height/2), width, height);
	x2 = MaxPixel[0]; y2 = MaxPixel[1]; OptSlice = MaxPixel[2];
}

selectWindow("Stack");
ROIsize=round(15000/xyVoxel);
halfROIsize = round(ROIsize/2);
makeRectangle(x2-halfROIsize, y2-halfROIsize, ROIsize, ROIsize);
run("Crop");

if (x2>=halfROIsize) {	x2=halfROIsize;	}
if (y2>=halfROIsize) {	y2=halfROIsize;	}

ROIsizeBG = round(ROIsize/10);
makeRectangle(ROIsizeBG, ROIsizeBG, ROIsizeBG, ROIsizeBG);
getStatistics(area, mean, min, max, std, histogram);
run("Select None");
run("Subtract...", "stack value="+mean);


//__________Redimension stack and set OptSlice to plane 50_________

while (OptSlice+50>nSlices) {
	setSlice(nSlices);
	run("Add Slice");
	}
while (OptSlice+50<nSlices) {
	setSlice(nSlices);
	run("Delete Slice");
	}
while (nSlices>100) {
	setSlice(1);
	run("Delete Slice");
	}
while (nSlices<100) {
	setSlice(1);
	run("Add Slice");
	}

OptSlice=50;

// _______________________Projections_______________________

selectWindow("Stack");
setSlice(OptSlice);
makeLine(0, y2, ROIsize, y2);
run("Reslice [/]...", "input="+zVoxel+" output="+zVoxel+" slice=1");
rename ("xProj");
	ROIsizeBG = round(ROIsize/10);
	makeRectangle(ROIsizeBG, ROIsizeBG, ROIsizeBG, ROIsizeBG);
	getStatistics(area, mean, min, max, std, histogram);
	run("Select None");
	run("Subtract...", "value="+min);
H=getHeight();

selectWindow("Stack");
setSlice(OptSlice);
makeLine(x2, 0, x2, ROIsize);
run("Reslice [/]...", "input="+zVoxel+" output="+zVoxel+" slice=1 rotate");
rename ("yProj");
	ROIsizeBG = round(ROIsize/10);
	makeRectangle(ROIsizeBG, ROIsizeBG, ROIsizeBG, ROIsizeBG);
	getStatistics(area, mean, min, max, std, histogram);
	run("Select None");
	run("Subtract...", "value="+min);

selectWindow("Stack");
run("Z Project...", "start=1 stop=100"+" projection=[Max Intensity]");
	ROIsizeBG = round(ROIsize/10);
	makeRectangle(ROIsizeBG, ROIsizeBG, ROIsizeBG, ROIsizeBG);
	getStatistics(area, mean, min, max, std, histogram);
	run("Select None");
	run("Subtract...", "value="+min);
rename("Project");

ProjectWidth=ROIsize+H;
run("Canvas Size...", "width="+ProjectWidth+" height="+ProjectWidth+" position=Top-Left zero");
selectWindow("yProj");
run("Canvas Size...", "width="+ProjectWidth+" height="+ProjectWidth+" position=Top-Right zero");
selectWindow("xProj");
run("Canvas Size...", "width="+ProjectWidth+" height="+ProjectWidth+" position=Bottom-Left zero");
run("Image Calculator...", "image1=Project operation=Add image2=xProj");
selectWindow("Project");
run("Image Calculator...", "image1=Project operation=Add image2=yProj");
run("Size...", "width=550 height=550 constrain interpolation=None");

selectWindow("xProj");
close();
selectWindow("yProj");
close();

selectWindow("Project");
run("32-bit");
run("Square Root");
getStatistics(area, mean, min, max, std, histogram);
setMinAndMax(mean, max);
run("Invert");
run("8-bit");
run("LUTforPSFs");
run("RGB Color");

// _______________________FWHM axial_______________________ ;

selectWindow("Stack");

zProfileX = newArray(nSlices); zProfileY = newArray(nSlices);
for (i=0; i<nSlices; i++) {
	setSlice(i+1);
	zProfileX[i] = i;
	zProfileY[i] = getPixel(x2, y2);
	}

Fit.doFit("Gaussian", zProfileX, zProfileY); a=Fit.p(0); b=Fit.p(1); c=Fit.p(2); d=Fit.p(3);
r_two_z = Fit.rSquared;

// ________________________Plot

Amplitude = 40;
XplotLatReal = newArray(Amplitude); YplotLatReal = newArray(Amplitude);
MaxGraph = 0;
for (i=0; i<Amplitude; i++) {
	XplotLatReal[i] = (i-Amplitude/2)*zVoxel;
	YplotLatReal[i] = zProfileY[OptSlice-Amplitude/2+i];
	if (YplotLatReal[i]>=MaxGraph) {MaxGraph = YplotLatReal[i];}
	}
XplotLatFit = newArray(Amplitude*4);
YplotLatFit = newArray(Amplitude*4);
Ymin=66000;
Ymax=0;
for (i=0; i<Amplitude*4; i++) {
	XplotLatFit[i] = (i/4-Amplitude/2)*zVoxel;
	X = OptSlice-Amplitude/2+i/4;
	YplotLatFit[i] =  a + (b-a)*exp(-(X-c)*(X-c)/(2*d*d));
	if (YplotLatFit[i]>=MaxGraph) {MaxGraph = YplotLatFit[i];}
	if (Ymin>YplotLatFit[i]) {Ymin=YplotLatFit[i];}
	if (Ymax<YplotLatFit[i]) {Ymax=YplotLatFit[i];}
	}

HM=(Ymax-Ymin)/2; k=-2*d*d*log((HM-a)/(b-a)); FWHMa=2*zVoxel*sqrt(k);

Plot.create("FWHM axial", "Z", "Intensity", XplotLatFit, YplotLatFit);
Plot.setLimits(-4000, 4000, 0, MaxGraph*1.1);
Plot.add("circles", XplotLatReal, YplotLatReal);
Plot.addText("FWHM axial ="+d2s(FWHMa,0)+"nm", 0, 0);
Plot.show();
Plot.setFrameSize(460, 220);
run("Canvas Size...", "width=550 height=275 position=Bottom-Center");
run("Canvas Size...", "width=550 height=550 position=Bottom-Center zero");



// _______________________FWHM lateral_______________________ ;

selectWindow("Stack");
setSlice(OptSlice);

x = newArray(-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8);
y = newArray(17);
yy = newArray(17);

for (i=0; i<17; i++) {
	y[i]=0; yy[i]=0;
	for (k=-floor(LineThickness/2); k<-floor(LineThickness/2)+LineThickness; k++) {
	y[i] = y[i] + getPixel(x2-8+i,y2+k)/LineThickness;
	yy[i] = yy[i] + getPixel(x2+k,y2-8+i)/LineThickness;
	}
}
Fit.doFit("Gaussian", x, y); a=Fit.p(0); b=Fit.p(1); c=Fit.p(2); d=Fit.p(3);
r_two_x = Fit.rSquared;
Fit.doFit("Gaussian", x, yy); ay=Fit.p(0); by=Fit.p(1); cy=Fit.p(2); dy=Fit.p(3);
r_two_y = Fit.rSquared;

// ________________________Plot

XplotLatReal = newArray(17); YplotLatReal = newArray(17); YplotLatRealy = newArray(17);

Ymin=66000;
Ymax=0;
MaxGraph = 0;
for (i=0; i<17; i++) {
	XplotLatReal[i] = (i-8)*xyVoxel;
	YplotLatReal[i] = y[i];
	YplotLatRealy[i] = yy[i];
	if (maxOf(y[i], yy[i])>=MaxGraph) {MaxGraph = maxOf(y[i], yy[i]);}
	}
XplotLatFit = newArray(65); YplotLatFit = newArray(65); YplotLatFity = newArray(65);

for (i=0; i<65; i++) {
	XplotLatFit[i] = (i/4-8)*xyVoxel;
	X = i/4-8;
	YplotLatFit[i] =  a + (b-a)*exp(-(X-c)*(X-c)/(2*d*d));
	YplotLatFity[i] =  ay + (by-ay)*exp(-(X-cy)*(X-cy)/(2*dy*dy));
	if (maxOf(YplotLatFit[i], YplotLatFity[i])>=MaxGraph) {MaxGraph = maxOf(YplotLatFit[i], YplotLatFity[i]);}
	if (Ymin>minOf(YplotLatFit[i], YplotLatFity[i])) {Ymin=minOf(YplotLatFit[i], YplotLatFity[i]);}
	if (Ymax<maxOf(YplotLatFit[i], YplotLatFity[i])) {Ymax=maxOf(YplotLatFit[i], YplotLatFity[i]);}
	}

HM=(Ymax-Ymin)/2; 
k=-2*d*d*log((HM-a)/(b-a)); FWHMl=2*xyVoxel*sqrt(k);
ky=-2*dy*dy*log((HM-ay)/(by-ay)); FWHMly=2*xyVoxel*sqrt(ky);

Plot.create("FWHM lateral", "X (black) or Y (blue)", "Intensity", XplotLatFit, YplotLatFit);
Plot.setLimits(-8*xyVoxel, 8*xyVoxel, 0, MaxGraph*1.1);
Plot.setColor("blue");
Plot.add("line", XplotLatFit, YplotLatFity);
Plot.add("circles", XplotLatReal, YplotLatRealy);
Plot.setColor("black");
Plot.add("circles", XplotLatReal, YplotLatReal);
Plot.addText("FWHM lateral X ="+d2s(FWHMl,0)+"nm; FWHM lateral Y ="+d2s(FWHMly,0)+"nm; Average ="+d2s((FWHMl+FWHMly)/2,0)+"nm", 0, 0);
Plot.show();
Plot.setFrameSize(460, 220);
run("Canvas Size...", "width=550 height=275 position=Top-Center");
run("Canvas Size...", "width=550 height=550 position=Top-Center zero");
run("Image Calculator...", "image1=[FWHM lateral] operation=Add image2=[FWHM axial]");
run("Canvas Size...", "width=550 height=550 position=Center");
rename("FWHM");
run("RGB Color");
selectWindow("FWHM axial");
close();
selectWindow("Stack");
close();

MainName=MainName+" FWHMa="+d2s(FWHMa,0)+"nm FWHMl="+d2s(FWHMl,0)+"nm";
run("Images to Stack");
rename(MainName);

setFont("Arial", 14, " antialiased");
run("Colors...", "foreground=red background=white selection=yellow");
setSlice(1);
drawString(date, 250, 260);
String1="FWHM lateral: X = "+d2s(FWHMl,0)+"nm;  Y = "+d2s(FWHMly,0)+"nm";
String2="FWHM lateral average = "+d2s((FWHMl+FWHMly)/2,0)+"nm"; 
String3="FWHM axial = "+d2s(FWHMa,0)+"nm";
drawString(String1, 250, 280); drawString(String2, 250, 300); drawString(String3, 250, 320);

if (choiceValues==1) {
	run("Colors...", "foreground=blue background=white selection=yellow");
	setFont("Arial", 14, " antialiased");
	drawString("Theoretical values", 250, 340);
		
	if (NA=="1.4") {drawString("NA1.4 Oil FWHMl 188nm - FWHMa 696nm", 250, 360);}
	if (NA=="1.32") {drawString("NA1.32 Oil FWHMl 199nm - FWHMa 781nm", 250, 360);}
	if (NA=="1.3") {
		drawString("NA1.3 Oil FWHMl 202nm - FWHMa 803nm", 250, 360);
		drawString("NA1.3 Glyc FWHMl 202nm - FWHMa 771nm", 250, 380);
		}
	if (NA=="0.95") {drawString("NA0.95 Air FWHMl 276nm - FWHMa 996nm", 250, 360);}
	if (NA=="1.2") {drawString("NA1.2 Water FWHMl 213nm - FWHMa 799nm", 250, 360);}
	if (NA=="0.8") {
		drawString("NA0.8 Glyc FWHMl 328nm - FWHMa 2038nm", 250, 360);
		drawString("NA0.8 Air FWHMl 383nm - FWHMa 1403nm", 250, 380);
		}
	if (NA=="0.75") {drawString("NA0.75 Air FWHMl 350nm - FWHMa 1598nm", 250, 360);}
	if (NA=="1.45") {drawString("NA1.45 Oil FWHMl 181nm - FWHMa 649nm", 250, 360);}
	if (NA=="1.25") {drawString("NA1.25 Oil FWHMl 210nm - FWHMa 873nm", 250, 360);}
	
	if (NA!="0.75" && NA!="0.8" && NA!="1.3" && NA!="1.4" && NA!="1.45" && NA!="1.25" && NA!="1.2" && NA!="0.95" && NA!="1.32") {
		drawString("Values not determined yet", 250, 360);
		}
}
//__________Save FWHM values_____________________

InfoFWHM=fromCharCode(10)+ImageName+";"+date+";"+microscope+";"+MA+";"+NA+";"+MaxPixel[0]+";"+MaxPixel[1]+";"+MaxPixel[2]+";"+d2s(FWHMa,0)+";"+d2s(FWHMl,0)+";"+d2s(FWHMly,0)+";"+LineThickness+";"+d2s(r_two_z,3)+";"+d2s(r_two_x,3)+";"+d2s(r_two_y,3);
if (Loc == "FMI") {
	path2 = S+S+"imagestore"+S+"FAIM"+S+"Maintenance_All microscopes"+S+"FWHMValues_"+microscope+"_"+MA+"_"+NA+".txt";
} else {
	path = getDirectory("Choose a Directory");
	path2=path+"FWHMValues.txt";
}
if (File.exists(path2) == 1) {
	File.append(InfoFWHM, path2);
} else {
	headers = "ImageName;date;microscope;MA;NA;X;Y;Plane;FWHMa;FWHMl_X;FWHMl_Y;LineThickness;r2_a;r2_x;r2_y";
	File.append(headers, path2);
	File.append(InfoFWHM, path2);
}

//print(fromCharCode(10)+ImageName+" - Date: "+date+" - Microscope: "+microscope+" - MAG: "+MA+" - NA: "+NA+" - Coord. Max pixel: "+MaxPixel[0]+", "+MaxPixel[1]+", "+MaxPixel[2]+" - FWHMa: "+d2s(FWHMa,0)+" - FWHMx: "+d2s(FWHMl,0)+" - FWHMy: "+d2s(FWHMly,0)+" - Line Thick.: "+LineThickness+" - r_two2 in z: "+d2s(r_two_z,3)+" - r_two2 in x: "+d2s(r_two_x,3)+" - r_two2 in y: "+d2s(r_two_y,3));
print(InfoFWHM);

//________Save MIP __________________________

if (Loc == "FMI") {
path=S+S+"imagestore"+S+"FAIM"+S+"Maintenance_All microscopes"+S+MainName;
} else {path=path+MainName;}
i=2;
while (File.exists(path+".tif")==1) {
    path=S+S+"imagestore"+S+"FAIM"+S+"Maintenance_All microscopes"+S+MainName+"_"+i;
    i = i + 1;
    }
	saveAs("tiff", path+".tif");

//}