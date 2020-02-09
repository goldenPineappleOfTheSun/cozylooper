import track
from trackStates import TrackState

class LoopDefault:

    """ when track started """
    def onBeat(track):
    	pass

    def onBar(track):
    	if track.state == TrackState.readyToRecord:
    		track.state = TrackState.record
    		track.redraw()

    def onTrackStarted(track):
    	pass
 
    def onTrackEnded(track):
    	if track.state == TrackState.readyToRecord:
    		track.state = TrackState.record
    		track.redraw()

    def onRecordDemanded(track):
        track.state = TrackState.readyToRecord
        track.redraw()

    def onRecordDisabled(track):
        track.state = TrackState.default
        track.redraw()

    def onPlayDemanded(track):
        track.state = TrackState.play
        track.redraw()

    def onPlayStop(track):
        track.state = TrackState.default
        track.redraw()

