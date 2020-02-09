from trackStates import TrackState

class LoopDefault:

    """ when track started """
    def onBeat(self):
    	pass

    def onBar(self):
    	pass

    def onTrackStarted(self):
    	pass
 
    def onTrackEnded(self):
    	pass

    def onRecordDemanded(self):
        self.state = TrackState.readyToRecord

    def onRecordDisabled(self):
        self.state = TrackState.default

    def onPlayDemanded(self):
        self.state = TrackState.play

    def onPlayStop(self):
        self.state = TrackState.default

