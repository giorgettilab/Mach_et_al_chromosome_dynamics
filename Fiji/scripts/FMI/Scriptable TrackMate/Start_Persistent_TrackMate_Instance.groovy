#@ ImagePlus imp
#@ ObjectService os
#@ ScriptService scriptService

import fiji.plugin.trackmate.Model
import fiji.plugin.trackmate.Settings
import fiji.plugin.trackmate.TrackMate
import fiji.plugin.trackmate.gui.TrackMateGUIController

/*
 * Add alias to allow easy script parameter usage
 */
scriptService.addAlias(TrackMate.class)

/*
 * Create TrackMate instance linked to imp
 */
model = new Model()
settings = new Settings()
settings.setFrom(imp)
trackmate = new TrackMate(model, settings)

/*
 * Remove any registered TrackMate instances, and
 * 
 * Add current TrackMate instance to ObjectService
 * for later retrieval
 */
os.getObjects(TrackMate.class).each {
	os.removeObject(it)
}
os.addObject(trackmate, "Scriptable TrackMate Session")

/*
 * Start TrackMate GUI
 */
controller = new TrackMateGUIController( trackmate )
frame = controller.getGUI()
//frame.setTitle("Interactive TrackMate Session")
null
