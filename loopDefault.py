import track
from trackStates import TrackState

class LoopDefault:

    def getType():
        return 'LoopDefault'

    """ when track started """
    def onBeat(track):
        if track.state == TrackState.readyToPlay:
            track.state = TrackState.play
            track.beat = 0
            track.redraw()

    def onBar(track):
        if track.state == TrackState.readyToRecord:
            track.state = TrackState.record
            track.beat = 0
            track.redraw()

    def onTrackStarted(track):
        pass
 
    def onTrackEnded(track):
        if track.state == TrackState.record:
            track.state = TrackState.default
            if track.playAfterRecord:
                track.state = TrackState.play
                track.playAfterRecord = False
            track.startSmoothAfter(10000)
            track.redraw()
 
    def onGlobalLoop(track):
        if track.state == TrackState.awaitingChanges:
            track.state = TrackState.default
            track.beat = 0
            track.redraw()

    def onRecordDemanded(track):
        track.state = TrackState.readyToRecord
        track.resetMemory()
        track.redraw()

    def onRecordDisabled(track):
        track.state = TrackState.default
        track.redraw()

    def onPlayDemanded(track):
        track.state = TrackState.readyToPlay
        track.redraw()

    def onPlayStop(track):
        track.state = TrackState.default
        track.redraw()