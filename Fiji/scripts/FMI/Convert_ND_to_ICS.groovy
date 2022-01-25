#!groovy

/**
 * Resave an ND dataset to ICS/IDS
 * 
 * The MetaMorph ND format creates datasets of many small files.
 * This script resaves these datasets into ics/ids format and
 * creates a single pair of ics/ids files (optionally per channel)
 * 
 * @author Jan Eglinger, FMI Basel
 */

#@File(label="Input dataset (nd file)") file
#@boolean(label="Separate channels") separateChannels
#@LogService log

import loci.plugins.BF
import loci.plugins.in.ImporterOptions
import ij.IJ
import ij.plugin.ChannelSplitter

/**
 * Verify the given closure and log any assertion error
 */
def verify(Closure closure) {
	try {
		closure()
		return true
	} catch (AssertionError e) {
		log.error(e.toString())
		return false
	}
}

/**
 * Save a given imp to savePath using bio-formats
 */
def saveWithoutOverwrite(imp, savePath) {
	if (!verify {assert(!new File(savePath).exists())}) return
	IJ.run(imp, "Bio-Formats Exporter", "save=[$savePath]" );
}

/**
 * Main method: open an ND dataset, save as ICS/IDS
 */
def main() {
	path = file.getPath()
	options = new ImporterOptions()
	options.setId(path)
	options.setOpenAllSeries(false)
	options.setSeriesOn(0, true)
	imps = BF.openImagePlus(options)
	try {
		if (separateChannels) {
			channels = ChannelSplitter.split(imps[0])
			channels.eachWithIndex { ch, index ->
				newPath = path.take(path.lastIndexOf('.')) + "_w${index + 1}.ids"
				saveWithoutOverwrite(ch, newPath)
			}
		} else {
			newPath = path.take(path.lastIndexOf('.')) + ".ids"
			saveWithoutOverwrite(imps[0], newPath)
		}
	} finally {
		imps[0].close()
		log.info("Done with resaving. All images closed.")
	}
	return
}

main()
