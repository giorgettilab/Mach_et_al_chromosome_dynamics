"""
Stitch multiple positions in separate channels
"""
from fiji.util.gui import GenericDialogPlus
from ij import IJ
from ij.plugin import ZProjector
import re, os
from functools import partial

"""
Define regular expression patterns for image and config matches
"""
imagePattern = "^(?P<basename>\w+)_(?P<channel>w\d\w+)_s\d+\.(tif|TIF|tiff|TIFF)$"
tileConfPattern = "^TileConfiguration(?P<pos>\d+)\.txt$"

def getFileLists():
    """
    Display a dialog and get lists of images and config files
    """
    gd = GenericDialogPlus("Stitch files via MIP")
    gd.addDirectoryField("Folder_containing_the_images", "")
    gd.showDialog()
    if (gd.wasCanceled()):
        return None, None, None
    srcDir = gd.getNextString()
    if not os.path.isdir(srcDir):
        print "Not a directory"
        return None, None, None
    # get file list
    for root, folders, files in os.walk(srcDir):
        break  # we just want to get `files`, no subfolders

    r_image = re.compile(imagePattern)
    r_conf = re.compile(tileConfPattern)
    return srcDir, filter(r_image.match, files), filter(r_conf.match, files)

def getOptions(channels, basenames, positions):
    """
    Display an options dialog
    """
    gd = GenericDialogPlus("Multiposition Stitching - Options")
    gd.addChoice("Reference channel", sorted(channels), "")
    # TODO basename selection if more than one
    for p in sorted(positions):
        gd.addCheckbox("Position_" + p, True)
    gd.addDirectoryField("Save files to:", "")
    gd.addCheckbox("Use_maximum_intensity_projection for robust stitching", True)
    gd.showDialog()
    if (gd.wasCanceled()):
        return None, None, None, None, None
    position_choice = {} # dict
    for p in sorted(positions):
        position_choice[p] = gd.getNextBoolean()
    
    return gd.getNextChoice(), basenames.pop(), position_choice, gd.getNextString(), gd.getNextBoolean()

def createMIP(source, imageFile, dest):
    """
    Create a maximum intensity projection of a given (stack) file
    """
    print "Creating MIP from", imageFile
    stackImp = IJ.openImage(os.path.join(source, imageFile))
    zp = ZProjector(stackImp)
    zp.setMethod(ZProjector.MAX_METHOD)
    zp.doProjection()
    IJ.saveAs(zp.getProjection(), "TIFF", os.path.join(dest, imageFile))

def replace_closure(subgroup, replacement, m):
    """
    Replace given subgroup of match object by replacement string
    
    See http://stackoverflow.com/a/33655644/1919049
    """
    if m.group(subgroup) not in [None, '']:
        start = m.start(subgroup)
        end = m.end(subgroup)
        return m.group()[:start] + replacement + m.group()[end:]

def run():
    srcDir, image_files, conf_files = getFileLists()
    if not image_files:
        print "No image files found"
        return
    #print "Images", image_files
    #print "TileConf", conf_files
    
    # select which positions (from TileConf)
    pos_set = set()
    basename_set = set()
    channel_set = set()

    for f in image_files:
        m = re.match(imagePattern, f)
        basename_set.add(m.group("basename")) # supposedly unique
        channel_set.add(m.group("channel"))

    for f in conf_files:
        m = re.match(tileConfPattern, f)
        pos_set.add(m.group("pos"))

    print pos_set
    print basename_set
    print channel_set

    # ask for reference channel
    # ask for basename (if more than one is present)
    # ask for positions
    # directory for saving
    reference, basename, positions, dstDir, useMIP = getOptions(channel_set, basename_set, pos_set)
    print reference, basename, positions, dstDir, useMIP
    if not dstDir or dstDir == srcDir:
        print "No valid output directory"
        return

    # filter image_list by basename
    # filter by reference channel
    ref_pattern = re.sub('\(\?P<channel>[^\)]*\)', reference, imagePattern)
    r_reference = re.compile(ref_pattern)
    ref_images = filter(r_reference.match, image_files)
    if not useMIP:
        print ("Stitching without MIP not yet implemented. Please use the previous workflow (Laurent's macro).")
        return
    for f in ref_images:
        createMIP(srcDir, f, dstDir)
        # TODO force MIP into different folder, abort when srcDir = dstDir?
        # TODO only create MIPs for selected positions?
    for f in conf_files:
        pos = re.match(tileConfPattern, f)
        if not positions[pos.group("pos")]: # look up dict entry TODO: refactor to set/list?
            continue
        # Read template TileConfiguration file
        template = open(os.path.join(srcDir, f))
        content = template.read()
        template.close()
        lines = content.splitlines()
        # Write 2D config file into dstDir
        print "Processing config file", f
        # open new TileConfig file for writing
        outname = f[0:-4] + "_MIP.txt"
        outfile = open(os.path.join(dstDir, outname), 'w')
        # write header for 2D
        outfile.write("# Define the number of dimensions we are working on\n")
        outfile.write("dim = 2\n")
        outfile.write("\n")
        outfile.write("# Define the image coordinates\n")
        for l in lines:
            parts = l.split(";")
            if l.startswith("#") or len(parts) < 2:
                continue
            # m = re.match(imagePattern, parts[0])
            # replace name by basename in filename
            # replace channel by reference in filename
            parts[0] = parts[0].replace("Name", basename + "_" + reference) # TODO make more general
            # replace 3d by 2d in coordinates
            coord_pattern = "\s*\(([0-9-\.]*,\s+[0-9-\.]*),\s+[0-9-\.]*\)"
            # print parts[2]
            m = re.match(coord_pattern, parts[2])
            # print m
            parts[2] = " (" + m.group(1) + ")"
            # write line
            # print ";".join(parts)
            outfile.write(";".join(parts) + "\n")
        # close new TileConfig file
        outfile.close()
        # stitch new TileConfig with write TileConfig only option
        IJ.run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=[" + dstDir + "] layout_file=[" + outname + "] fusion_method=[Do not fuse images (only write TileConfiguration)] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)]");
        # read registered TileConf
        regname = outname[0:-4] + ".registered.txt"
        reg_template = open(os.path.join(dstDir, regname))
        content = reg_template.read()
        reg_template.close()
        lines = content.splitlines()
        # write 3d tileconfs per channel
        for c in channel_set:
            print "Writing", basename + "_" + c + "_registered-via-mip.txt"
            outfileName = basename + "_" + c + "_pos" + pos.group("pos") + "_registered-via-mip.txt"
            outfile = open(os.path.join(srcDir, outfileName), 'w')
            # write header for 2D
            outfile.write("# Define the number of dimensions we are working on\n")
            outfile.write("dim = 3\n")
            outfile.write("\n")
            outfile.write("# Define the image coordinates\n")
            for l in lines:
                parts = l.split(";")
                if l.startswith("#") or len(parts) < 2:
                    continue
                parts[0] = re.sub(imagePattern, partial(replace_closure, 'channel', c), parts[0])
                # replace 3d by 2d in coordinates
                coord_pattern = "\s*\(([0-9-\.]*,\s+[0-9-\.]*)\s*\)"
                # print parts[2]
                m = re.match(coord_pattern, parts[2])
                if not m:
                    continue
                # print m
                parts[2] = " (" + m.group(1) + ", 0.0)"
                outfile.write(";".join(parts) + "\n")
            outfile.close()
            # stitch final images (per channel)
            IJ.run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=[" + srcDir + "] layout_file=[" + outfileName + "] fusion_method=[Linear Blending] computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
            imp = IJ.getImage()
            IJ.saveAs(imp, "TIFF", os.path.join(srcDir, outfileName))
            imp.close()
    print "Done"

run()
