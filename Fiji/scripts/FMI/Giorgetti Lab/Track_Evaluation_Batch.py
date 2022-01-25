#@ File (style="extensions:xml") xmlFile
#@ ScriptService scriptService
#@output resultsTable

from itertools import product
from java.io import File
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate import Settings
from org.scijava.table import DefaultGenericTable

from ch.fmi.trackmate.tracking import PointCloudRegistrationTrackerFactory
from ch.fmi.trackmate.tracking import PointDescriptorTrackerFactory

def runScript(settings):
    paramMap = {
        'xmlFile': xmlFile,
        'tmSettings': settings
    }
    scriptModule = scriptService.run(File("scripts/FMI/Giorgetti Lab/Track_Evaluation.groovy"), False, paramMap).get()
    return (scriptModule.getOutput('avgIoU'), scriptModule.getOutput('avgMatchingSpots'), scriptModule.getOutput('avgMatchingTracks'), scriptModule.getOutput('avgOfTrackMaxIuO'))

# SparseLAPTracker settings
def lapTrackerSettings(dist, allow_gap, max_gap, gap_dist, allow_merge, merge_dist, allow_split, split_dist):
    settings = Settings()
    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
    settings.trackerSettings[ 'LINKING_MAX_DISTANCE' ]      = dist
    settings.trackerSettings[ 'ALLOW_GAP_CLOSING' ]         = allow_gap
    settings.trackerSettings[ 'MAX_FRAME_GAP' ]             = max_gap
    settings.trackerSettings[ 'GAP_CLOSING_MAX_DISTANCE' ]  = gap_dist
    settings.trackerSettings[ 'ALLOW_TRACK_MERGING' ]       = allow_merge
    settings.trackerSettings[ 'MERGING_MAX_DISTANCE' ]      = merge_dist
    settings.trackerSettings[ 'ALLOW_TRACK_SPLITTING' ]     = allow_split
    settings.trackerSettings[ 'SPLITTING_MAX_DISTANCE' ]    = split_dist
    return settings

# PointCloudRegistrationTracker settings
def pointCloudRegistrationTrackerSettings(num_inliers, frame_range):
    settings = Settings()
    settings.trackerFactory = PointCloudRegistrationTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
    settings.trackerSettings[ 'MIN_NUM_INLIERS' ]     = num_inliers
    settings.trackerSettings[ 'FRAME_RANGE' ]         = frame_range
    return settings

# PointDescriptorTracker settings
def pointDescriptorTrackerSettings(subset_size, num_neighbors, max_interval, cost_threshold, square_dist_threshold, prune_graph):
    settings = Settings()
    settings.trackerFactory = PointDescriptorTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
    settings.trackerSettings[ 'SUBSET_NEIGHBORS' ]     = subset_size
    settings.trackerSettings[ 'NUM_NEIGHBORS' ]        = num_neighbors
    settings.trackerSettings[ 'MAX_INTERVAL' ]         = max_interval
    settings.trackerSettings[ 'COST_THRESHOLD' ]       = cost_threshold
    settings.trackerSettings[ 'MAX_LINKING_DISTANCE' ] = square_dist_threshold
    settings.trackerSettings[ 'PRUNE_GRAPH' ]          = prune_graph
    return settings

# Set up results table
resultsTable = DefaultGenericTable()
resultsTable.appendColumn('tracker')

# Results
resultsTable.appendColumn('avgIoU')
resultsTable.appendColumn('avgMatchingSpots')
resultsTable.appendColumn('avgMatchingTracks')
resultsTable.appendColumn('avgOfTrackMaxIoU')

# LAPTracker params
resultsTable.appendColumn('dist')
resultsTable.appendColumn('allow_gap')
resultsTable.appendColumn('max_gap')
resultsTable.appendColumn('gap_dist')
resultsTable.appendColumn('allow_merge')
resultsTable.appendColumn('merge_dist')
resultsTable.appendColumn('allow_split')
resultsTable.appendColumn('split_dist')

# PointCloudRegistrationTracker params
resultsTable.appendColumn('num_inliers')
resultsTable.appendColumn('frame_range')

# PointDescriptorTracker params
resultsTable.appendColumn('subset_size')
resultsTable.appendColumn('num_neighbors')
resultsTable.appendColumn('max_interval')
resultsTable.appendColumn('cost_threshold')
resultsTable.appendColumn('square_dist_threshold')
resultsTable.appendColumn('prune_graph')

rowCounter = -1

# SparseLAPTracker parameter sweep
runLAPTracker = True
dist_values = [0.5, 1.0, 2.5]
allow_gap_values = [True]
max_gap_values = [2, 4]
gap_dist_values = [2.0]
allow_merge_values = [False]
merge_dist_values = [0.0]
allow_split_values = [False]
split_dist_values = [0.0]

if (runLAPTracker):
  for (
    dist, allow_gap, max_gap, gap_dist,
    allow_merge, merge_dist,
    allow_split, split_dist
    ) in product(
        dist_values, allow_gap_values, max_gap_values, gap_dist_values,
        allow_merge_values, merge_dist_values,
        allow_split_values, split_dist_values
        ):
    resultsTable.appendRow()
    rowCounter += 1
    resultsTable.set('tracker', rowCounter, "SparseLAPTracker")
    resultsTable.set('dist', rowCounter, dist)
    resultsTable.set('allow_gap', rowCounter, allow_gap)
    resultsTable.set('max_gap', rowCounter, max_gap)
    resultsTable.set('gap_dist', rowCounter, gap_dist)
    resultsTable.set('allow_merge', rowCounter, allow_merge)
    resultsTable.set('merge_dist', rowCounter, merge_dist)
    resultsTable.set('allow_split', rowCounter, allow_split)
    resultsTable.set('split_dist', rowCounter, split_dist)
    print "Running SparseLAPTracker with", dist, allow_gap, max_gap, gap_dist, allow_merge, merge_dist, allow_split, split_dist
    s =  lapTrackerSettings(dist, allow_gap, max_gap, gap_dist, allow_merge, merge_dist, allow_split, split_dist)
    (avgIoU, avgMatchingSpots, avgMatchingTracks, avgOfTrackMaxIoU) = runScript(s)
    resultsTable.set('avgIoU', rowCounter, avgIoU)
    resultsTable.set('avgMatchingSpots', rowCounter, avgMatchingSpots)
    resultsTable.set('avgMatchingTracks', rowCounter, avgMatchingTracks)
    resultsTable.set('avgOfTrackMaxIoU', rowCounter, avgOfTrackMaxIoU)

# PointCloudRegistrationTracker parameter sweep
runPointCloudRegistrationTracker = True
num_inliers_values = [25]
frame_range_values = [7]

if (runPointCloudRegistrationTracker):
  for (
    num_inliers, frame_range
    ) in product(
        num_inliers_values, frame_range_values
        ):
    resultsTable.appendRow()
    rowCounter += 1
    resultsTable.set('tracker', rowCounter, "PointCloudRegistrationTracker")
    resultsTable.set('num_inliers', rowCounter, num_inliers)
    resultsTable.set('frame_range', rowCounter, frame_range)
    print "Running PointCloudRegistrationTracker with", num_inliers, frame_range
    s =  pointCloudRegistrationTrackerSettings(num_inliers, frame_range)
    (avgIoU, avgMatchingSpots, avgMatchingTracks, avgOfTrackMaxIoU) = runScript(s)
    resultsTable.set('avgIoU', rowCounter, avgIoU)
    resultsTable.set('avgMatchingSpots', rowCounter, avgMatchingSpots)
    resultsTable.set('avgMatchingTracks', rowCounter, avgMatchingTracks)
    resultsTable.set('avgOfTrackMaxIoU', rowCounter, avgOfTrackMaxIoU)

# PointDescriptorTracker parameter sweep
runPointDescriptorTracker = True
subset_size_values = [4]
num_neighbors_values = [5]
max_interval_values = [3]
cost_threshold_values = [1.0]
square_dist_threshold_values = [1.0]
prune_graph_values = [False]

if (runPointDescriptorTracker):
  for (
    subset_size, num_neighbors, max_interval, cost_threshold, square_dist_threshold, prune_graph
    ) in product(
        subset_size_values, num_neighbors_values, max_interval_values,
        cost_threshold_values, square_dist_threshold_values, prune_graph_values
        ):
    resultsTable.appendRow()
    rowCounter += 1
    resultsTable.set('tracker', rowCounter, "PointDescriptorTracker")
    resultsTable.set('subset_size', rowCounter, subset_size)
    resultsTable.set('num_neighbors', rowCounter, num_neighbors)
    resultsTable.set('max_interval', rowCounter, max_interval)
    resultsTable.set('cost_threshold', rowCounter, cost_threshold)
    resultsTable.set('square_dist_threshold', rowCounter, square_dist_threshold)
    resultsTable.set('prune_graph', rowCounter, prune_graph)
    print "Running PointDescriptorTracker with", subset_size, num_neighbors, max_interval, cost_threshold, square_dist_threshold, prune_graph
    s =  pointDescriptorTrackerSettings(subset_size, num_neighbors, max_interval, cost_threshold, square_dist_threshold, prune_graph)
    (avgIoU, avgMatchingSpots, avgMatchingTracks, avgOfTrackMaxIoU) = runScript(s)
    resultsTable.set('avgIoU', rowCounter, avgIoU)
    resultsTable.set('avgMatchingSpots', rowCounter, avgMatchingSpots)
    resultsTable.set('avgMatchingTracks', rowCounter, avgMatchingTracks)
    resultsTable.set('avgOfTrackMaxIoU', rowCounter, avgOfTrackMaxIoU)
