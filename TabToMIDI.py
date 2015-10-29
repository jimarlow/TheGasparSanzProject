__author__ = 'jimarlow'
import re

def MIDINumberToNote(num):
    """
    Converts a MIDI number to a note string
    :param midiNumber: 60
    :return: "C4"
    """
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave, note = divmod(num, 12)
    octave = octave - 1
    return notes[note] + str(octave)


def noteToMIDINumber(noteString):
    """
    Converts a note string to a MIDI number
    :param noteString: e.g. "C4"
    :return: the MIDI number for a note e.g. "C4" (middle C) to 60
    """
    offsets = {"C":0, "C#":1, "D":2, "D#":3, "E":4, "F":5, "F#":6, "G":7, "G#":8, "A":9, "A#":10, "B":11}
    note, octave, tmp = re.split('([0-9]*)', noteString.strip())
    octave = int(octave) + 1
    return octave * 12 + offsets[note]


def coursesToMIDINumbers(courses):
    """
    Returns the MIDI numbers for a set of courses
    :param courses: [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
    :return: [[52], [47, 47], [43, 43], [50, 50], [57, 57]]
    """
    return [[noteToMIDINumber(s) for s in c] for c in courses]


def courseFretToMIDINumbers(courses, course, fret):
    """
    Returns the MIDI numbers for a course/fret on a set of courses
    :param courses: [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
    :param course: 2
    :param fret: 3
    :return: [55,55]
    """
    midiCourses= coursesToMIDINumbers(courses)
    # Remember that courses are numbered 1,2,3 etc. whereas Python arrays are numbered 0,1,2 etc.
    return [s + fret for s in midiCourses[course-1]]


if __name__ == "__main__":

    import unittest

    class TabToMIDITest(unittest.TestCase):
        def setUp(self):
            self.courses = [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
            self.coursesMIDI = [[64], [59, 59], [55, 55], [62, 62], [69, 69]]
            self.middleCNote = "C4"
            self.middleCMIDINumber = 60
            self.course=2
            self.fret=2
            self.courseFretMIDINumbers = [61, 61]

        def testMIDINumberToNote(self):
            self.assertEqual(MIDINumberToNote(self.middleCMIDINumber), self.middleCNote)

        def testNoteToMIDINumber(self):
            self.assertEqual(noteToMIDINumber(self.middleCNote), self.middleCMIDINumber)

        def testCoursesToMIDINumbers(self):
            self.assertEqual(coursesToMIDINumbers(self.courses), self.coursesMIDI)

        def testCourseFretToMIDINumbers(self):
            self.assertEqual(courseFretToMIDINumbers(self.courses, self.course, self.fret), self.courseFretMIDINumbers)

    unittest.main()

