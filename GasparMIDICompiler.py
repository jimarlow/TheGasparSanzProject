__author__ = 'jimarlow'
import re
from GasparConfig import *
from TabToMIDI import *
from os.path import *


# def midiNumberToNote(midiNumber):
#     """
#     Converts a MIDI number to a note string
#     :param midiNumber: 60
#     :return: "C4"
#     """
#     notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
#     octave, note = divmod(midiNumber, 12)
#     return notes[note] + str(octave -1)
#
#
# def noteToMIDINumber(noteString):
#     """
#     Converts a note string to a MIDI number
#     :param noteString: e.g. "C4"
#     :return: the MIDI number for a note e.g. "C4" (middle C) to 60
#     """
#     offsets = {"C":0, "C#":1, "D":2, "D#":3, "E":4, "F":5, "F#":6, "G":7, "G#":8, "A":9, "A#":10, "B":11}
#     note, octave, tmp = re.split('([0-9]*)', noteString.strip())
#     # The MIDI octave is 1 + the standard octave
#     return (int(octave)+1) * 12 + offsets[note]
#
#
# def coursesToMIDINumbers(courses):
#     """
#     Returns the MIDI numbers for a set of courses
#     :param courses: [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
#     :return: [[52], [47, 47], [43, 43], [50, 50], [57, 57]]
#     """
#     return [[noteToMIDINumber(s) for s in c] for c in courses]
#
#
# def courseFretToMIDINumbers(courses, course, fret):
#     """
#     Returns the MIDI numbers for a course/fret on a set of courses
#     :param courses: [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
#     :param course: 2
#     :param fret: 3
#     :return: [55,55]
#     """
#     midiCourses= coursesToMIDINumbers(courses)
#     # Remember that courses are numbered 1,2,3 etc. whereas Python arrays are numbered 0,1,2 etc.
#     return [s + fret for s in midiCourses[course-1]]


semiquaver = 4
dottedSemiquaver = 6
quaver = 8
dottedQuaver = 12
crotchet = 16
dottedCrotchet = 24
minim = 32
dottedMinim = 48


class HeaderChunk:
    # Format 0 MIDI files consist of a header-chunk and a single track-chunk.
    def __init__(self, format=0, tracks=1, ticks=20):
        self.type = bytes(b'MThd')
        self.length = 6
        self.format = format
        self.tracks = tracks
        self.ticks = ticks

    def write(self, file):
        file.write(self.type)
        file.write(self.length.to_bytes(length=4, byteorder='big'))
        file.write(self.format.to_bytes(length=2, byteorder='big'))
        file.write(self.tracks.to_bytes(length=2, byteorder='big'))
        file.write(self.ticks.to_bytes(length=2, byteorder='big'))


class TrackChunk:
    def __init__(self):
        self.type = bytes(b'MTrk')
        self.trackEvents = []
        self.length = 0

    def addTrackEvent(self, trackEvent):
        self.trackEvents.append(trackEvent)
        self.length += trackEvent.getLength()

    def write(self, file):
        file.write(self.type)
        file.write(self.length.to_bytes(length=4, byteorder='big'))
        for te in self.trackEvents:
            te.write(file)


# This is the only track event we need
class NoteOnMIDIEvent:
    # Keep deltaTime < 127 i.e. 1 byte so that we don't need MID variable length values
    def __init__(self, deltaTime=100, key=0x3C, velocity=0x40, channel=1):
        self.deltaTime = deltaTime
        self.channel = channel
        self.key = key
        self.velocity = velocity

    def getLength(self):
        return 4

    def write(self, file):
        file.write(self.deltaTime.to_bytes(length=1, byteorder='big'))
        file.write((0x90).to_bytes(length=1, byteorder='big'))
        file.write(self.key.to_bytes(length=1, byteorder='big'))
        file.write(self.velocity.to_bytes(length=1, byteorder='big'))


class SingleTrackMIDIFile:
    def __init__(self):
        self.headerChunk = HeaderChunk()
        self.trackChunk = TrackChunk()

    def addNoteOnEvent(self, deltaTime=100, key=0x3C, velocity=0x40, channel=1):
        self.trackChunk.addTrackEvent(NoteOnMIDIEvent(deltaTime, key, velocity, channel))

    def write(self, filename):
        midiFile = open(filename, 'wb')
        self.headerChunk.write(midiFile)
        self.trackChunk.write(midiFile)
        midiFile.close()


class GasparMIDICompiler:
    def __init__(self, filename, courses=GC.courses):
        self.filename = filename
        self.outputFilename = splitext(self.filename)[0] + ".midi"
        self.courses=courses
        self.delta = 0
        self.midiFile = SingleTrackMIDIFile()

    def write(self):
        self.midiFile.write(filename=self.outputFilename)

    def parseNotes(self, line):
        notes = line.split()
        # Process a chord
        tempDelta = self.delta # Only use a duration for the first note in the chord
        for n in notes:
            course, fret = n.split('-')
            if fret.isnumeric():
                midiKeys = courseFretToMIDINumbers(self.courses, int(course), int(fret))
                #print("Note: ", n, " Delta ", self.duration," Course ", course, " Fret ", fret, " MIDI key", midiKeys)
                # Add the first string in the course
                self.midiFile.addNoteOnEvent(deltaTime=tempDelta, key=midiKeys[0])
                tempDelta = 0
                # Add the second string in the course
                if len(midiKeys) == 2:
                    #print("Bourdon ", midiKeys[1])
                    self.midiFile.addNoteOnEvent(deltaTime=tempDelta, key=midiKeys[1])

    def parseLines(self):

        lines = [line.rstrip('\n') for line in open(self.filename)]

        for line in lines:
            line = line.strip()  # Get rid of any indentation
            if line.startswith("M "):
                self.parseNotes(line[2:])
                self.delta = minim
            elif line.startswith("M. "):
                self.parseNotes(line[3:])
                self.delta = dottedMinim
            elif line.startswith("C "):
                self.parseNotes(line[2:])
                self.delta = crotchet
            elif line.startswith("C. "):
                self.parseNotes(line[3:])
                self.delta = dottedCrotchet
            elif line.startswith("Q "):
                self.parseNotes(line[2:])
                self.delta = quaver
            elif line.startswith("Q. "):
                self.parseNotes(line[3:])
                self.delta = dottedQuaver
            elif line.startswith("SQ "):
                self.parseNotes(line[3:])
                self.delta = semiquaver
            elif line.startswith("SQ. "):
                self.parseNotes(line[4:])
                self.delta = dottedSemiquaver
            elif re.match('^[0-9]', line):
                self.parseNotes(line)
            elif line.startswith("COURSES "): self.courses=[c.split("-") for c in toS(line, "COURSES ").split()]
            else:
                pass


if __name__ == "__main__":

    mf = SingleTrackMIDIFile()
    mf.addNoteOnEvent(key=0x3C, deltaTime=0)
    mf.addNoteOnEvent(key=0x3D, deltaTime=30)
    mf.addNoteOnEvent(key=0x3E, deltaTime=10)
    mf.addNoteOnEvent(key=0x3F, deltaTime=20)
    mf.addNoteOnEvent(key=0x4C, deltaTime=quaver)
    mf.addNoteOnEvent(key=0x4D, deltaTime=crotchet)
    mf.addNoteOnEvent(key=0x4E, deltaTime=crotchet)
    mf.addNoteOnEvent(key=0x4F, deltaTime=crotchet)
    mf.write('test04.midi')

    bourdons = [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D3', 'D3'], ['A2', 'A2']]

    p = GasparMIDICompler(filename="Espanoletas.sanz", courses=bourdons)
    p.parseLines()
    p.write("Espanoletas.midi")

    #p = MIDIParser("Rujero.sanz")
    #p.parseLines()
    #p.write("Rujero.midi")

    #p = MIDIParser("Paradetas.sanz")
    #p.parseLines()
    #p.write("Paradetas.midi")

