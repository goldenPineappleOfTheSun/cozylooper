import enum

class TrackState(enum.Enum):
    error = 0,
    default = 1,
    setSize = 2,
    record = 3,
    readyToRecord = 4,
    play = 5
    readyToPlay = 6,
    awaitingChanges = 7,