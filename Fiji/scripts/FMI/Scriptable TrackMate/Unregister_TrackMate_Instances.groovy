#@ ObjectService objectService

import fiji.plugin.trackmate.TrackMate

objectService.getObjects(TrackMate.class).each {
	objectService.removeObject(it)
}
null
