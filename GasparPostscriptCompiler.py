__author__ = 'jimarlow'
import re

from GasparTablature import *
from GasparMIDICompiler import *
from GasparLilyCompiler import *
from os.path import *
import os

DEBUG=False


# Note - fonts and sizes and other globals are collected from the top of the .sanz file in GC
class GasparPostscriptCompiler:
    def __init__(self, filename):
        GC.reset()
        self.filename = filename
        self.outputFilename = splitext(self.filename)[0] + ".ps"
        self.currentStave = None
        self.currentPage = None
        self.pages=[]

    def isFirstPage(self):
        return len(self.pages)==0

    def isFirstStave(self):
        # The first stave in the piece is the first stave on the first page
        return (len(self.currentPage.staves)==0) & (len(self.pages)==1)

    def getCurrentSlot(self):
        return self.currentStave.currentSlot

    def advance(self, n=1):
        # Ensure we have a current stave before we try to advance it
        if self.currentStave != None:
            self.currentStave.currentSlot +=n

    def parsePage(self, line):
        items = line.split()
        pageNumber = items[0].split('-')[1]
        self.currentPage = Page(pageNumber)
        self.currentPage.firstPage = self.isFirstPage()
        self.pages.append(self.currentPage)

    def parseStave(self, line):
        self.currentStave = Stave()
        self.currentStave.firstStave = self.isFirstStave()
        self.currentPage.append(self.currentStave)

    # def parseTimeSignature(self, line):
    #     vars = line.split()
    #     if len(vars) == 1:
    #         ts = vars[0].split("-")
    #         if len(ts) == 2:
    #             self.currentStave.append(TimeSignatureSingle(ts[1]))
    #         elif len(ts) == 3:
    #             self.currentStave.append(TimeSignatureDouble(ts[1], ts[2]))
    #         self.advance(3)

    def parseTimeSignature(self, line):
        ts = line.split("-")
        if len(ts) == 2:
            self.currentStave.append(TimeSignatureSingle(ts[1]))
        elif len(ts) == 3:
            self.currentStave.append(TimeSignatureDouble(ts[1], ts[2]))
        self.advance(3)

    def parseBarline(self,line):
        self.currentStave.append(Barline(number=toS(line), slot=self.getCurrentSlot()))
        self.advance()

    def parseShortBarline(self,line):
        self.currentStave.append(ShortBarline(slot=self.getCurrentSlot()))
        self.advance()

    def parseTripleBarline(self,line):
        self.currentStave.append(TripleBarline(slot=self.getCurrentSlot()))
        self.advance()

    def parseDoubleBarline(self,line):
        self.currentStave.append(DoubleBarline(number=toS(line), slot=self.getCurrentSlot()))
        self.advance()

    def parseLongShortBarline(self,line):
        self.currentStave.append(LongShortBarline(slot=self.getCurrentSlot()))
        self.advance()

    def parseEndBarline(self, line):
        self.currentStave.append(EndBarline(slot=self.getCurrentSlot()))

    def parseBarberpole(self, line, isHollow=False):
        """
        Draws a barberpole
        :param line: BP- or e.g. BP-2-3
        :return:
        BP-         the default barberpole that extends across all the courses
        BP-2-4      a short barberpole from course 2 to course 4
        Barberpoles are not numbered
        """
        tokens=line.split("-")
        numTokens = len(tokens)
        if numTokens == 3:
            self.currentStave.append(Barberpole(slot=self.getCurrentSlot(), startCourse=int(tokens[1]), endCourse=int(tokens[2]),isHollow=isHollow))
        else:
            self.currentStave.append(Barberpole(slot=self.getCurrentSlot(), isHollow=isHollow))

    def parseSpace(self, line):
        self.advance()

    def parseNotes(self, line):
        self.debugSlot('parseNotes', line)
        # If the line does not begin with a number, then it begins with a duration that we must discard
        if not re.match('^[0-9]', line):
            notes = line.split()[1:]
        else:
            notes = line.split()
        for n in notes:
            course, fret = n.split('-')
            course = int(course)
            if fret == "{":
                self.currentStave.append(OverSemicircle(slot=self.getCurrentSlot(),course=course))
            elif fret == "}":
                self.currentStave.append(UnderSemicircle(slot=self.getCurrentSlot(),course=course))
            elif fret == "[":
                self.currentStave.setSlurStart(slot=self.getCurrentSlot(), course=course)
            elif fret == "]":
                self.currentStave.append(Slur(slot1=self.currentStave.slurStartSlot, course1=self.currentStave.slurStartCourse,
                                              slot2=self.getCurrentSlot(), course2=course))
            else:
                self.currentStave.append(Note(slot=self.getCurrentSlot(),course=course, glyph=fret))

        # Move to the next slot
        self.advance()


    def parseSection(self, slot):
        self.currentStave.append(Section(self.getCurrentSlot()-1))

    def parseRasgueado(self, line):
        self.currentStave.append(Strum(slot=self.getCurrentSlot()-1, pattern=toS(line)))

    def parseAlfabeto(self, chord):
        # Do not automatically advance alfabeto! It is too complex
        self.currentStave.append(Alfabeto(slot=self.getCurrentSlot(), chord=chord))

    def debugSlot(self, method, line):
        if DEBUG: print("Method: ", method, " current slot: ", self.getCurrentSlot(), " line: , line")

    # Parse the duration
    def parseDuration(self, line, duration, dotted=False):
        self.currentStave.append(Tick(self.getCurrentSlot(), duration=duration, dot=dotted))
        self.parseNotes(line)


    def parseCourses(self, line):
        GC.courses=[c.split("-") for c in toS(line, "COURSES ").split()]
        GC.numberOfCourses=len(GC.courses)


    def parseFretmap(self, line):
        fmap = line.split("FRETMAP ")[1].split()
        if len(fmap) == 0:
            return
        GC.fretMapping = {}
        for f in fmap:
            k, v = f.split("-")
            GC.fretMapping[k]=v

    def parseLines(self):

        self.lines = [line.rstrip('\n') for line in open(self.filename)]

        for line in self.lines:
            line = line.strip()  # Get rid of any indentation

            # The tablature syntax
            # Page and stave
            if   line.startswith("P-"):         self.parsePage(line)
            elif line.startswith("S-"):         self.parseStave(line)
            # Time signature
            elif line.startswith("T-"):         self.parseTimeSignature(line)
            # Barlines
            elif line.startswith("SB-"):        self.parseShortBarline(line)
            elif line.startswith("TB-"):        self.parseTripleBarline(line)
            elif line.startswith("DB-"):        self.parseDoubleBarline(line)
            elif line.startswith("LSB-"):       self.parseLongShortBarline(line)
            elif line.startswith("B-"):         self.parseBarline(line)
            elif line.startswith("BP-"):        self.parseBarberpole(line)
            elif line.startswith("EB-"):        self.parseEndBarline(line)
            # Note with duration
            elif line.startswith("W "):         self.parseDuration(line, BREVE)
            elif line.startswith("M "):         self.parseDuration(line, MINIM)
            elif line.startswith("M. "):        self.parseDuration(line, MINIM, DOTTED)
            elif line.startswith("C "):         self.parseDuration(line, CROTCHET)
            elif line.startswith("C. "):        self.parseDuration(line, CROTCHET, DOTTED)
            elif line.startswith("Q "):         self.parseDuration(line, QUAVER)
            elif line.startswith("Q. "):        self.parseDuration(line, QUAVER,DOTTED)
            elif line.startswith("SQ "):        self.parseDuration(line, SEMIQUAVER)
            elif line.startswith("SQ. "):       self.parseDuration(line, SEMIQUAVER, DOTTED)
            # Rasgueado
            elif line.startswith("R-"):         self.parseRasgueado(line)
            # Alphabeto
            elif line.startswith("AB-"):         self.parseAlfabeto(toS(line, "AB-"))
            # Section
            elif line.startswith("SECTION"):    self.parseSection(line)
            # Title and composer
            elif line.startswith("TITLE "):     self.currentPage.title = toS(line, "TITLE ")
            elif line.startswith("COMPOSER "):  self.currentPage.composer = toS(line, "COMPOSER ")
            # Space
            elif line=="":                      self.parseSpace(line)
            # Note without duration
            elif re.match('^[0-9]', line):      self.parseNotes(line)

            # Globals - these control the style of the document
            # Page
            elif line.startswith("PAGEWIDTH "):         GC.pageWidth=toI(line, "PAGEWIDTH ")
            elif line.startswith("PAGEHEIGHT "):        GC.pageHeight=toI(line, "PAGEHEIGHT")
            # Margins
            elif line.startswith("TOPMARGIN "):         GC.topMargin=toI(line, "TOPMARGIN ")
            elif line.startswith("BOTTOMMARGIN "):      GC.bottomMargin=toI(line, "BOTTOMMARGIN ")
            elif line.startswith("LEFTMARGIN "):        GC.leftMargin=toI(line, "LEFTMARGIN ")
            elif line.startswith("RIGHTMARGIN "):       GC.rightMargin=toI(line, "RIGHTMARGIN ")
            # Stave layout
            elif line.startswith("STAVESEPARATION "):   GC.staveSeparation=toI(line, "STAVESEPARATION ")
            elif line.startswith("SLOTS "):             GC.slots=toI(line, "SLOTS ")
            # Courses
            elif line.startswith("COURSES "):           self.parseCourses(line)
            elif line.startswith("NUMBEROFCOURSES "):   GC.numberOfCourses=toI(line, "NUMBEROFCOURSES ")
            elif line.startswith("SHOWCOURSES"):        GC.showCourses=True
            elif line.startswith("COURSESPACING "):     GC.courseSpacing=toI(line, "COURSESPACING ")
            elif line.startswith("JUSTIFIED"):          GC.justified=True
            # Barline
            elif line.startswith("BARLINESPACING "):    GC.barlineSpacing=toI(line, "BARLINESPACING ")
            elif line.startswith("BARBERPOLESPACING "): GC.barberpoleSpacing=toI(line, "BARBERPOLESPACING ")
            # Text
            elif line.startswith("TITLEFACE "):         GC.titleFace=toS(line, "TITLEFACE")
            elif line.startswith("TITLESIZE "):         GC.titleSize=toI(line, "TITLESIZE ")
            elif line.startswith("TITLEYPOSITION "):    GC.titleYPosition=toI(line, "TITLEYPOSITION ")
            elif line.startswith("COMPOSERFACE "):      GC.composerFace=toS(line,"COMPOSERFACE ")
            elif line.startswith("COMPOSERSIZE "):      GC.composerSize=toI(line, "COMPOSERSIZE")
            elif line.startswith("COMPOSERYPOSITION "): GC.titleYPosition=toI(line, "COMPOSERYPOSITION ")
            elif line.startswith("FRETFACE "):          GC.fretFace=toS(line, "FRETFACE ")
            elif line.startswith("FRETSIZE "):          GC.fretSize=toI(line, "FRETSIZE ")
            # Fret mapping
            elif line.startswith("FRETMAP "):           self.parseFretmap(line)
            elif line.startswith("FRETMAPPINGOFF"):     GC.mapFrets=False
            elif line.startswith("FRENCH"):             GC.french=True
            # Comment
            elif line.startswith(";"):                  pass

            else: pass

    def render(self, f):
        # First, map the fonts we are using to ISOLatin1 in order
        # to access the special characters needed for foreign languages
        print(psMapFont("Times-Roman"), file=f)         # Always map Times-Roman - it is the default font
        print(psMapFont(GC.composerFace), file=f)
        print(psMapFont(GC.titleFace), file=f)
        print(psMapFont(GC.fretFace), file=f)

        # Render the manuscript pages
        for p in self.pages:
            p.render(f)

    def write(self):
        f = open(self.outputFilename, 'w')
        self.render(f)
        f.close()


def tabset(filename):
    p = GasparPostscriptCompiler(filename)
    p.parseLines()
    p.write()


def midiset(filename):
    p = GasparMIDICompiler(filename)
    p.parseLines()
    p.write()


def lilyset(filename):
    p = GasparLilyCompiler(filename)
    p.parseLines()
    p.write()


def engrave(filename):
    tabset(filename)
    midiset(filename)
    lilyset(filename)

def main():
    workingDir = os.getcwd() + "/Instruccion/"
    testDir = os.getcwd() + "/TestMedia/"

    # engrave(workingDir+"Espanoletas.sanz")
    # engrave(workingDir+"EspanoletasPorOtro.sanz")
    # engrave(workingDir+"Rujero.sanz")
    # engrave(workingDir+"Paradetas.sanz")
    # engrave(workingDir+"Matachin.sanz")
    # engrave(workingDir+"Zarabanda.sanz")
    # engrave(workingDir+"Jacaras.sanz")
    # engrave(workingDir+"Chacona.sanz")
    # engrave(workingDir+"ChaconaJustified.sanz")
    # engrave(workingDir+"Pasacalles.sanz")
    # engrave(workingDir+"Gallardas.sanz")

    engrave(testDir+"CanariosFrench.sanz")
    engrave(testDir+"CanariosItalian.sanz")

    tabset(testDir+"TestCourses.sanz")
    tabset(testDir+"FretMappingTest.sanz")

    #midiset(testDir+"TestCourses.sanz")



if __name__ == "__main__":
    main()
