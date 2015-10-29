__author__ = 'jimarlow'

# Page layout
A4WIDTH = 595
A4HEIGHT = 842

# Graphics
LINEWIDTH = 0.5

# Durations
BREVE = -1
MINIM = 0
CROTCHET = 1
QUAVER = 2
SEMIQUAVER = 3

DOTTED = True

class GlobalContext:
    def __init__(self):
        self.reset()

    def reset(self):
        # Page
        self.pageWidth=A4WIDTH
        self.pageHeight=A4HEIGHT

        # Margins
        self.topMargin = 200
        self.bottomMargin = 72
        self.leftMargin = 72
        self.rightMargin = 72

        # Stave layout
        self.staveSeparation = 48
        self.numberOfCourses=5
        self.courseSpacing=10
        self.slots=30
        self.courses=[['E4'], ['B3', 'B3'], ['G3', 'G3'], ['D4', 'D4'], ['A4', 'A4']]
        self.courseFace = "ArialMT"
        self.courseSize=8
        self.showCourses=False
        self.justified=False

        # Barlines
        self.barlineSpacing = 4
        self.barberpoleSpacing = 8
        self.barlineFace = "ArialMT"
        self.barlineSize = 8

        # Rythm
        self.tickBodyRadius = 2.5

        # Text
        self.titleFace = "Zapfino"
        self.titleSize = 24
        self.titleYPosition = self.pageHeight-100
        self.composerFace = "Times-Roman"
        self.composerSize = 12
        self.composerYPosition = self.titleYPosition-20
        self.fretFace="ArialMT"
        self.fretSize=10
        self.sectionSymbolSize = 18

        # Alfabeto
        self.alfabetoFace = "Times-Roman"
        self.alfabetoSize = 0.8 * self.courseSpacing * self.numberOfCourses

        # Ornamentation
        # Short slur over/under notes
        self.semicircleRadius = self.fretSize/2

        # Fret mapping
        self.fretMapping = {"10":"X"}
        self.mapFrets = True
        self.french = False


GC = GlobalContext()


def getStaveHeight(): return (GC.numberOfCourses-1) * GC.courseSpacing


def getCourseYOffset(courseNumber=1): return (courseNumber-1) * GC.courseSpacing


def toS(line, pattern="-"): return line.split(pattern)[1].lstrip()


def toI(line, pattern="-"): return int(line.split(pattern)[1].lstrip())
