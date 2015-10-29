__author__ = 'jimarlow'
from TabToMIDI import *
from GasparConfig import *
from os.path import *

lpSemiquaver = "16"
lpDottedSemiquaver = "16."
lpQuaver = "8"
lpDottedQuaver = "8."
lpCrotchet = "4"
lpDottedCrotchet = "4."
lpMinim = "2"
lpDottedMinim = "2."

lpSingleBar = ' \\undo \\omit Score.BarLine \\bar "|" '
lpBarberpole = ' \\undo \\omit Score.BarLine \\bar "." ' # This is a thick single barline
lpDoubleBar = ' \\undo \\omit Score.BarLine \\bar "||" '
lpThickThinBar = ' \\undo \\omit Score.BarLine \\bar ".|" '
lpThickThickBar = ' \\undo \\omit Score.BarLine \\bar ".." '
lpTripleBar = ' \\undo \\omit Score.BarLine \\bar "|.|" '
lpEndBar = ' \\undo \\omit Score.BarLine \\bar "|." '

lpOpenBody = """\\transpose c c' \\absolute {\\override Staff.TimeSignature #'stencil = ##f \\time 1000/4"""
lpOpenHeader = """\\header{ """


def cleanText(t):
    return t.replace("\\361", 'ñ')


def MIDINumberToLily(num):
    num = int(num)
    octaves = [",,,,", ",,,", ",,", ",", "", "'", "''", "'''"]
    notes = ["c", "cis", "d", "dis", "e", "f", "fis", "g", "gis", "a", "ais", "b"]
    octave, note = divmod(num, 12)
    return notes[note] + octaves[octave]


def noteToLily(note):
    return MIDINumberToLily( noteToMIDINumber(note) )


def courseFretToLily(courses, course, fret):
    return [ MIDINumberToLily(num) for num in courseFretToMIDINumbers(courses, course, fret)]


class GasparLilyCompiler:
    def __init__(self, filename, courses=GC.courses):
        self.filename = filename
        self.outputFilename = splitext(self.filename)[0] + "Lilypond.ly"
        self.lpCourses = courses
        self.duration = "16"
        self.header = lpOpenHeader
        self.body = lpOpenBody
        self.barlines = False

    def appendToHeader(self, s):
        self.header += s

    def appendToBody(self, s):
        self.body += s

    def write(self):
        f = open(self.outputFilename, 'w')
        print(self.header, file=f)
        print(self.body, file=f)
        f.close()

    def getCourse(self, num):
        return self.lpCourses[num-1]

    def parseNotes(self, line):
        notes = line.split()
        # Process a chord
        chordString=""
        chordString +=" < "
        for n in notes:
            course, fret = n.split('-')
            if fret.isnumeric():
                fret = int(fret)
                course = int(course)
                chordString = chordString + " " + courseFretToLily(self.lpCourses, course, fret)[0]
        if self.barlines:
            bl = "  \omit Score.BarLine"
        else:
            bl = ""
        self.appendToBody(chordString+" >" + self.duration + bl)

    def parseTimeSignature(self, line):
        ts = line.split("-")
        if len(ts) == 2:
            self.appendToBody('\\time ' + ts[1] + "/4")
        elif len(ts) == 3:
            self.appendToBody('\\time ' + ts[1] + "/" + ts[2])


    def parseLines(self):

        lines = [line.rstrip('\n') for line in open(self.filename)]

        for line in lines:
            line = line.strip()  # Get rid of any indentation
            if line.startswith("M "):
                self.duration = lpMinim
                self.parseNotes(line[2:])
            elif line.startswith("M. "):
                self.duration = lpDottedMinim
                self.parseNotes(line[3:])
            elif line.startswith("C "):
                self.duration = lpCrotchet
                self.parseNotes(line[2:])
            elif line.startswith("C. "):
                self.duration = lpDottedCrotchet
                self.parseNotes(line[3:])
            elif line.startswith("Q "):
                self.duration = lpQuaver
                self.parseNotes(line[2:])
            elif line.startswith("Q. "):
                self.duration = lpDottedQuaver
                self.parseNotes(line[3:])
            elif line.startswith("SQ "):
                self.duration = lpSemiquaver
                self.parseNotes(line[3:])
            elif line.startswith("SQ. "):
                self.duration = lpDottedSemiquaver
                self.parseNotes(line[4:])
            elif re.match('^[0-9]', line):
                self.parseNotes(line)
            elif line.startswith("COURSES "):
                self.lpCourses=[c.split("-") for c in toS(line, "COURSES ").split()]

            # Title and composer
            elif line.startswith("TITLE "):     self.appendToHeader(' title = "' + cleanText(toS(line, "TITLE ")) + '" ' )
            elif line.startswith("COMPOSER "):  self.appendToHeader(' composer = "' + toS(line, "COMPOSER ") + '" ')

            # Time signature
            #elif line.startswith("T-"):         self.parseTimeSignature(line)

            # Barlines
            elif line.startswith("SB-"): self.appendToBody(lpSingleBar) ; self.barlines = True
            elif line.startswith("TB-"): self.appendToBody(lpTripleBar) ; self.barlines = True
            elif line.startswith("DB-"): self.appendToBody(lpDoubleBar) ; self.barlines = True
            elif line.startswith("LSB-"): self.appendToBody(lpThickThinBar) ; self.barlines = True

            # Need to skip any unnumbered barlines that are may be placed
            # in justified tablature for cosmetic purposes
            elif re.match('B-[0-9]', line): self.appendToBody(lpSingleBar) ; self.barlines = True

            #elif line.startswith("B-"): self.appendToBody(lpSingleBar) ; self.barlines = True
            elif line.startswith("BP-"): self.appendToBody(lpBarberpole) ; self.barlines = True
            elif line.startswith("EB-"): self.appendToBody(lpEndBar) ; self.barlines = True

            else:
                pass
        self.appendToHeader("}")
        self.appendToBody("}")


if __name__ == "__main__":

    testCourses=[['E4'], ['B3', 'B2'], ['G3', 'G2'], ['D3', 'D2'], ['A3', 'A2']]

    p = GasparLilyCompiler("Rujero.sanz", courses=testCourses)
    p.parseLines()
    print(p.header)
    print(p.body)




    #p.write("Espanoletas.midi")


    # courses = [['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
    #
    # header = """\header{ title = "A scale in LilyPond" }"""
    #
    # openNotes = """\\absolute { """
    # closeNotes = """}"""
    #
    # print(MIDINumberToLily(48))
    # print(noteToLily("C#4"))
    #
    # print(noteToLily("G4"))
    # print(courseFretToLily(courses, 3, 24))
    #
    # notes = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5"]
    # print(header)
    # print(openNotes)
    # print(" ".join(map(noteToLily, notes)))
    # print(closeNotes)
