__author__ = 'jimarlow'

import math
from GasparPostscript import *
import re

# To redirect print statements for debugging:
# import sys
# sys.stdout = open('gaspar.ps', 'w')

def mapFret(fret):
    """Splits a fret into the fret number and any adornments (e.g. T)
    Maps the fret number according to the CG.fretMapping dictionary.
    Note: the first parameter of Dictionary.get is the key, the second,
    the value to return if the key is missing.
    :param fret: 10:.
    :return: X:.
    """
    m = re.match("([0-9]+)([a-zA-Z:.]+)", fret)
    if m:
        return GC.fretMapping.get(m.group(1), m.group(1)) + m.group(2)
    else:
        return GC.fretMapping.get(fret, fret)


def italianOrFrench(c):
    if GC.french:
        return GC.numberOfCourses + 1 - c
    else:
        return c


class TimeSignatureDouble:
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def placeOnStave(self, stave):
        self.stave = stave
        self.fontSize = stave.height / 2
        self.bottomX = stave.x
        self.bottomY = stave.y + self.fontSize / 5
        self.topX = stave.x
        self.topY = stave.y + stave.height / 2 + self.fontSize / 5

    def pad(self, padding):
        pass

    def render(self, f):
        print(psText(self.top, self.topX, self.topY, self.fontSize), file=f)
        print(psText(self.bottom, self.bottomX, self.bottomY, self.fontSize), file=f)


class TimeSignatureSingle:
    def __init__(self, glyph):
        self.glyph = glyph

    def placeOnStave(self, stave):
        self.fontSize = stave.height / 2
        self.bottomX = stave.x
        self.bottomY = stave.y + stave.height / 2 - self.fontSize / 3

    def pad(self, padding):
        pass

    def render(self, f):
        print(psText(self.glyph, self.bottomX, self.bottomY, self.fontSize), file=f)


class CommonTime(TimeSignatureSingle):
    def __init__(self):
        TimeSignatureSingle.__init__(self, "C")

    def pad(self, padding):
        pass

    def render(self, f):
        print(psText(self.glyph, self.bottomX, self.bottomY, self.fontSize), file=f)


class SplitCommonTime(TimeSignatureSingle):
    def __init__(self):
        TimeSignatureSingle.__init__(self, "C")

    def placeOnStave(self, stave):
        super().placeOnStave(stave)
        self.lineBottomX = self.bottomX + self.fontSize / 3
        self.lineBottomY = self.bottomY - self.fontSize / 4
        self.lineHeight = self.fontSize + self.fontSize / 4

    def pad(self, padding):
        pass

    def render(self, f):
        print(psText(self.glyph, self.bottomX, self.bottomY, self.fontSize), file=f)
        print(psVerticalLine(self.lineBottomX, self.lineBottomY, self.lineHeight, lineWidth=1), file=f)


class Alfabeto:
    def __init__(self, slot, chord):
        self.slot = slot
        self.chord = chord

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.y + getStaveHeight()/2 - GC.alfabetoSize/3

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        print(psText(text=self.chord, x=self.x, y=self.y, size=GC.alfabetoSize, face=GC.alfabetoFace), file=f)



class Strum:
    def __init__(self, slot, pattern):
        self.slot = slot
        self.pattern = pattern

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.y

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        offset = GC.fretSize/2
        print(psRGBColor(255, 0, 0), file=f)
        for s in self.pattern:
            offset += GC.fretSize/2
            if s == 'U':
                print(psVerticalLine(self.x+offset, self.y, GC.fretSize*3/4, 1), file=f)
            elif s =='D':
                print(psVerticalLine(self.x+offset, self.y, - GC.fretSize*3/4, 1), file=f)
        print(psRGBColor(), file=f)


class OverSemicircle:
    def __init__(self, slot=0, course=1):
        self.slot = slot
        self.course = course
        self.radius = GC.semicircleRadius

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot) + self.radius / 2
        self.y = stave.getSlotY(self.course) * stave.courseSpacing + stave.courseSpacing * 0.8 - self.radius

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        print(psOverSemicircle(self.x, self.y, self.radius), file=f)


class UnderSemicircle:
    def __init__(self, slot=0, course=1):
        self.slot = slot
        self.course = course
        self.radius = GC.semicircleRadius

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot) + self.radius / 2
        self.y = stave.getSlotY(self.course) - (stave.courseSpacing * 0.8 - self.radius)

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        print(psUnderSemicircle(self.x, self.y, self.radius), file=f)


class Slur:
    def __init__(self, slot1=0, course1=1, slot2=0, course2=1):
        self.slot1 = slot1
        self.course1 = course1
        self.slot = self.slot2 = slot2
        self.course2 = course2
        self.x = 0

    def placeOnStave(self, stave):
        c1 = italianOrFrench(self.course1)
        c2 = italianOrFrench(self.course2)
        print(self.course1, c1)
        # Start of slur
        self.x1 = stave.getSlotX(self.slot1)
        self.y1 = stave.y + (c1 - 1) * stave.courseSpacing + stave.courseSpacing*3/4
        # End of slur
        self.x3 = stave.getSlotX(self.slot2)
        self.y3 = stave.y + (c2 - 1) * stave.courseSpacing + stave.courseSpacing*3/4
        # Middle of slur
        self.x2 = (self.x1 + self.x3)/2
        if GC.french:
            self.y1 -= 1.5*stave.courseSpacing
            self.y2 = min(self.y1, self.y3) - 2*stave.courseSpacing - stave.courseSpacing
            self.y3 -= 1.5*stave.courseSpacing
        else:
            self.y2 = max(self.y1, self.y3) + 2*stave.courseSpacing

    def pad(self, padding):
        self.x1 += self.slot1 * padding
        self.x3 += self.slot2 * padding
        self.x2 = (self.x1 + self.x3)/2

    def render(self, f):
        print(psCurveTo(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3,), file=f)


class Section:
    def __init__(self, slot=0):
        self.slot = slot

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.y + stave.height*3/2

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        print(psText("\\247", self.x, self.y, GC.sectionSymbolSize), file=f)


def renderBox(x, y, width, height, lw, f):
    print(psVerticalLine(x, y, height, lw), file=f)
    print(psVerticalLine(x + width, y, height, lw), file=f)
    print(psHorizontalLine( x, y, width, lw), file=f)
    print(psHorizontalLine( x, y+height, width, lw), file=f)

def renderCrossBox(x, y, width, height, lw, f):
    renderBox( x, y, width, height, lw, f)
    print(psLine( x, y, x+width, y+height, lw), file=f)
    print(psLine( x, y+height, x+width, y, lw), file=f)

def renderTriangle(x, y, width, height, lw, f):
    apexX = x + width/2
    apexY = y + height
    print(psHorizontalLine( x, y, width, lw), file=f)
    print(psLine(x, y, apexX, apexY, lw), file=f)
    print(psLine(x+width, y, apexX, apexY, lw), file=f)

def renderBarberpole(x, y, file, startCourse=1, endCourse=GC.numberOfCourses, isHollow=False):
    triangleHeight = GC.courseSpacing * 0.75
    bottomTriangleY = y + getCourseYOffset(startCourse)
    bottomTriangleHeight = -getCourseYOffset(startCourse) - GC.courseSpacing * 0.75

    topTriangleY = y + getCourseYOffset(endCourse)
    topTriangleHeight = getStaveHeight() - getCourseYOffset(endCourse) + GC.courseSpacing * 0.75

    circleR = GC.barberpoleSpacing/2.5
    circleX = x + GC.barberpoleSpacing/2
    circleYBottom = y - triangleHeight - circleR
    circleYTop = y + getStaveHeight() + triangleHeight + circleR
    renderTriangle(x, topTriangleY, GC.barberpoleSpacing, topTriangleHeight, LINEWIDTH, file)
    renderTriangle(x, bottomTriangleY, GC.barberpoleSpacing, bottomTriangleHeight, LINEWIDTH, file)
    print(psCircle(circleX, circleYBottom, circleR, LINEWIDTH), file=file)
    print(psCircle(circleX, circleYTop, circleR, LINEWIDTH), file=file)
    if isHollow:
        renderBox(x , y + getCourseYOffset(startCourse), GC.barberpoleSpacing, getCourseYOffset(endCourse) - getCourseYOffset(startCourse), LINEWIDTH, file)
    else:
        [renderCrossBox(x, y + getCourseYOffset(c), GC.barberpoleSpacing, GC.courseSpacing, LINEWIDTH, file) for c in range(startCourse,  endCourse)]


# Barlines
class Barline:
    def __init__(self, number=0, slot=0):
        self.slot = slot
        self.number = number

    def placeOnStave(self, stave):
        self.stave = stave
        self.x = stave.getSlotX(self.slot)
        self.y = stave.y

    def pad(self, padding):
        self.x += self.slot * padding

    def renderBarlineText(self, textX, textY, f):
        print(psRGBColor(0, 0, 255), file=f)
        print(psText(text=str(self.number), x=textX, y=textY, size=GC.barlineSize, face=GC.barlineFace), file=f)
        print(psRGBColor(), file=f)

    def render(self, f):
        print(psVerticalLine(self.x, self.y, self.stave.height), file=f)
        self.renderBarlineText(self.x - GC.barlineSize / 2, self.y + self.stave.height + GC.barlineSize / 2, f)

class Barberpole(Barline):
    def __init__(self, slot, startCourse=1, endCourse=GC.numberOfCourses, isHollow=False):
        Barline.__init__(self, 1, slot)
        self.startCourse = startCourse
        self.endCourse = endCourse
        self.isHollow = isHollow

    def render(self, f):
        renderBarberpole(self.x, self.y, startCourse=self.startCourse, endCourse=self.endCourse, file=f, isHollow=self.isHollow)


class DoubleBarline(Barline):
    def __init__(self, number, slot):
        Barline.__init__(self, number, slot)

    def render(self, f):
        print(psVerticalLine(self.x - GC.barlineSpacing, self.y, self.stave.height), file=f)
        print(psVerticalLine(self.x, self.y, self.stave.height), file=f)
        self.renderBarlineText(self.x - GC.barlineSize / 2,self.y + self.stave.height + GC.barlineSize / 2,f)


class ShortBarline(Barline):
    def __init__(self, slot):
        Barline.__init__(self, 1, slot)

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.y + stave.courseSpacing
        self.height = (stave.numberOfCourses - 3) * stave.courseSpacing

    def render(self, f):
        print(psVerticalLine(self.x - GC.barlineSpacing, self.y, self.height), file=f)
        print(psVerticalLine(self.x, self.y, self.height), file=f)


class LongShortBarline(Barline):
    def __init__(self, slot):
        Barline.__init__(self, 1, slot)

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.longY = stave.y
        self.shortY = stave.y + stave.courseSpacing
        self.longHeight = stave.height
        self.shortHeight = (stave.numberOfCourses - 3) * stave.courseSpacing

    def render(self, f):
        print(psVerticalLine(self.x - GC.barlineSpacing, self.longY, self.longHeight), file=f)
        print(psVerticalLine(self.x, self.shortY, self.shortHeight), file=f)
        self.renderBarlineText(self.x - GC.barlineSize / 2,self.longY + self.longHeight + GC.barlineSize / 2,f)


class TripleBarline(LongShortBarline):
    def __init__(self, slot):
        LongShortBarline.__init__(self, slot)

    def render(self, f):
        print(psVerticalLine(self.x, self.longY, self.longHeight), file=f)
        print(psVerticalLine(self.x + GC.barlineSpacing, self.shortY, self.shortHeight), file=f)
        print(psVerticalLine(self.x - GC.barlineSpacing, self.shortY, self.shortHeight), file=f)
        self.renderBarlineText(self.x - GC.barlineSize / 2,self.longY + self.longHeight + GC.barlineSize / 2,f)


class EndBarline(Barline):
    def __init__(self, slot):
        Barline.__init__(self, 1, slot)

    def render(self, f):
        # TO DO - SHOULD THIS ALWAYS BE AT THE END OF THE STAVE???
        self.x = self.stave.getSlotX(self.stave.slots)
        print(psVerticalLine(self.x - GC.barlineSpacing, self.y, self.stave.height), file=f)
        print(psVerticalLine(self.x, self.y, self.stave.height, 2), file=f)


class Tick:
    def __init__(self, slot, duration=1, dot=False, body=True, height=14):
        self.slot = slot
        self.duration = duration
        self.height = height
        self.body = body
        self.dot = dot

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot) + 2 * GC.tickBodyRadius
        self.y = stave.y + stave.height + stave.courseSpacing

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        # Print the stem
        if self.duration >= 0:
            print(psStem(self.x, self.y, self.height), file=f)
        # Print the tails
        print(psDrawTails(self.x, self.y, self.height, self.duration), file=f)
        if self.body:
            if self.duration <= 0:
                print(psTickBody(self.x, self.y), file=f)
            else:
                print(psTickBodyFilled(self.x, self.y), file=f)
        # Print the dot if there is one
        if self.dot:
            print(psTickDot(self.x, self.y), file=f)


class Note:
    # In tablature, these notes are numbers or letters indicating a fret
    # 0 = open string
    # 1 = fret 1
    # etc.
    def __init__(self, slot, course, glyph=""):
        self.slot = slot
        self.course = course
        self.glyph = glyph
        self.size = GC.fretSize
        self.face = GC.fretFace

    def placeOnStave(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.getSlotY(self.course) - math.floor(self.size / 3)

    def placeOnStaveBetween(self, stave):
        self.x = stave.getSlotX(self.slot)
        self.y = stave.getSlotY(self.course) - math.floor(self.size / 3) - math.floor(stave.courseSpacing / 2)

    def pad(self, padding):
        self.x += self.slot * padding

    def render(self, f):
        t = self.glyph
        if GC.mapFrets:
            t = mapFret(self.glyph)
        print(psText(text=t, x=self.x, y=self.y, size=GC.fretSize, face=GC.fretFace), file=f)


class Stave:

    def __init__(self, x=100, y=100, l=400):
        self.numberOfCourses = GC.numberOfCourses
        self.courseSpacing = GC.courseSpacing
        self.height = (self.numberOfCourses - 1) * self.courseSpacing
        self.x = x
        self.y = y
        self.l = l
        self.slots = GC.slots
        self.glyphs = []
        self.currentSlot = 0
        self.slurStartSlot = None
        self.slurStartCourse = None
        self.firstStave=True

    def getSlotSpacing(self):
        return self.l/self.slots

    def justify(self):
        spareSlots = self.slots - self.currentSlot+1
        padding = spareSlots*self.getSlotSpacing()/(self.currentSlot-1)
        # If we are over 3/4 full on the stave, then pad it to be full
        if spareSlots < self.slots/4:
            for g in self.glyphs: g.pad(padding)

    def setSlurStart(self, slot, course):
        self.slurStartSlot = int(slot)
        self.slurStartCourse = int(course)

    def getSlurStart(self):
        return [self.slurStartSlot, self.slurStartCourse]

    def setPosition(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l

    def getSlotX(self, slot):
        return self.x + slot * self.l / self.slots

    def getSlotY(self, course):
        return self.y + self.getCourseY(course)
        #return self.y + self.getCourseY(course)

    def getCourseY(self, course):
        course = italianOrFrench(course)
        return (course - 1) * self.courseSpacing

    def appendSpace(self, n):
        self.currentSlot = self.currentSlot + n

    # N.B. The ticks appear above the stave and do NOT advance the slot
    def append(self, glyph):
        glyph.placeOnStave(self)
        self.glyphs.append(glyph)

    def appendBetween(self, glyph):
        glyph.placeOnStaveBetween(self)
        self.glyphs.append(glyph)

    def advance(self, n=1):
        self.currentSlot += n

    def getStringingY(self, course=0):
        course=italianOrFrench(course)
        return self.y - 0.3*GC.courseSize + (course-1)*GC.courseSpacing


    def render(self, f):
        # Print out the stringing only on the 1st stave on the 1st page
        if self.firstStave & GC.showCourses:
            # There are one or more courses
            c = 0
            for course in GC.courses:
                c += 1
                # Each course is an array that may have 1 or more strings
                for string in range(len(course)):
                    print(psText(text=course[string], x=self.x - (4-2*string)*GC.courseSize, y=self.getStringingY(c), size=GC.courseSize, face=GC.courseFace), file=f)

        # Print out the stave
        for course in range(self.numberOfCourses):
            print(psHorizontalLine(self.x, self.y + self.getCourseY(course + 1), self.l), file=f)
        # Print out the notes
        for n in self.glyphs:
            n.render(f)

    # def render(self, f):
    #     # Print out the stringing only on the 1st stave on the 1st page
    #     if self.firstStave & GC.showCourses:
    #         stringingY = self.y - 0.3*GC.courseSize
    #         # There are one or more courses
    #         for course in GC.courses:
    #             # Each course is an array that may have 1 or more strings
    #             for string in range(len(course)):
    #                 print(psText(text=course[string], x=self.x - (4-2*string)*GC.courseSize, y=stringingY, size=GC.courseSize, face=GC.courseFace), file=f)
    #             stringingY += GC.courseSpacing
    #
    #     # Print out the stave
    #     for course in range(self.numberOfCourses):
    #         print(psHorizontalLine(self.x, self.y + self.getCourseY(course + 1), self.l), file=f)
    #     # Print out the notes
    #     for n in self.glyphs:
    #         n.render(f)


class Page:

    def __init__(self, pageNumber=1):
        self.pageNumber = pageNumber
        self.firstPage=True
        self.topMargin = GC.topMargin
        self.bottomMargin = GC.bottomMargin
        self.leftMargin = GC.leftMargin
        self.rightMargin = GC.rightMargin
        self.pageWidth = GC.pageWidth
        self.pageHeight = GC.pageHeight
        self.staveSeparation = GC.staveSeparation
        self.staves = []
        self.courses = []
        self.title = ""
        self.composer = ""

    def append(self, stave):
        x = self.leftMargin
        y = self.pageHeight - self.topMargin - len(self.staves) * (stave.height + self.staveSeparation)
        l = self.pageWidth - self.leftMargin - self.rightMargin
        stave.setPosition(x, y, l)
        self.staves.append(stave)

    def extend(self, staves):
        for s in staves:
            self.append(s)

    def getMaxNumberOfStaves(self, stave):
        return math.floor((self.pageHeight - self.topMargin) / (stave.height + self.staveSeparation))

    def render(self, f):
        if not self.firstPage:
            # In a document, pages may start at any number,
            # so page 1 is not always the first page, sometimes it is page 2 etc.
            print("showpage ", file=f)
        if self.title:
            print(psCenteredText(text=self.title, pageWidth=GC.pageWidth, y=GC.titleYPosition, size=GC.titleSize, face=GC.titleFace), file=f)
        if self.composer:
            print(psRightJustifiedText(text=self.composer, pageWidth=GC.pageWidth - GC.leftMargin, y=GC.composerYPosition, size=GC.composerSize, face=GC.composerFace), file=f)
        for s in self.staves:
            if GC.justified: s.justify()
            s.render(f)


if __name__ == "__main__":
    mp = Page()
    s1 = Stave()

    numStaves = mp.getMaxNumberOfStaves(s1)

    for i in range(numStaves):
        mp.append(Stave())

    mp.staves[1].append(Note(slot=1, course=1, glyph="1T"))
    mp.staves[1].append(Note(slot=2, course=2, glyph="2V"))
    mp.staves[1].append(Note(slot=3, course=3, glyph="3"))
    mp.staves[1].append(Note(slot=4, course=4, glyph="4"))
    mp.staves[1].append(Note(slot=5, course=5, glyph="5"))

    mp.staves[2].append(Note(slot=1, course=1, glyph="1"))
    mp.staves[2].append(Note(slot=1, course=2, glyph="2"))
    mp.staves[2].append(Note(slot=1, course=3, glyph="3"))
    mp.staves[2].append(Note(slot=1, course=4, glyph="4"))
    mp.staves[2].append(Note(slot=1, course=5, glyph="5"))

    mp.staves[2].append(Note(slot=1, course=0, glyph="Under"))
    mp.staves[2].append(Note(slot=1, course=6, glyph="Over"))

    mp.staves[2].appendBetween(Note(slot=4, course=1, glyph="a"))
    mp.staves[2].appendBetween(Note(slot=4, course=2, glyph="b"))
    mp.staves[2].appendBetween(Note(slot=4, course=3, glyph="c"))
    mp.staves[2].appendBetween(Note(slot=4, course=4, glyph="d"))
    mp.staves[2].appendBetween(Note(slot=4, course=5, glyph="e"))

    mp.staves[3].append(Barline(number=25, slot=5))
    mp.staves[3].append(DoubleBarline(number=26, slot=6))
    mp.staves[3].append(EndBarline(number=27, slot=7))
    mp.staves[3].append(ShortBarline(number=28, slot=8))
    mp.staves[3].append(Barberpole(number=30, slot=9))

    mp.staves[1].append(Tick(slot=2, duration=0))
    mp.staves[1].append(Tick(slot=3, duration=1))
    mp.staves[1].append(Tick(slot=4, duration=2))
    mp.staves[1].append(Tick(slot=5, duration=3))
    mp.staves[1].append(Tick(slot=6, duration=4))
    mp.staves[1].append(Tick(slot=7, duration=4, dot=True))

    mp.staves[1].append(Tick(slot=8, duration=0, body=False))
    mp.staves[1].append(Tick(slot=9, duration=1, body=False))
    mp.staves[1].append(Tick(slot=10, duration=2, body=False))
    mp.staves[1].append(Tick(slot=11, duration=3, body=False))
    mp.staves[1].append(Tick(slot=12, duration=4, body=False))
    mp.staves[1].append(Tick(slot=13, duration=4, dot=True, body=False))

    mp.staves[1].append(TimeSignatureDouble(top="4", bottom="4"))
    mp.staves[2].append(TimeSignatureSingle("3"))
    mp.staves[3].append(CommonTime())
    mp.staves[4].append(SplitCommonTime())

    mp.staves[5].append(OverSemicircle(slot=3, course=4, radius=3))
    mp.staves[5].append(Note(slot=3, course=4, glyph="1"))
    mp.staves[5].append(UnderSemicircle(slot=4, course=2, radius=3))
    mp.staves[5].append(Note(slot=4, course=2, glyph="7"))

    mp.staves[4].append(Slur(slot1=4, course1=3, slot2=6, course2=1))

    mp.staves[5].append(Strum(slot=5, pattern="UDUD"))


    f = open('test4.ps', 'w')
    print(psMapTimesRoman, file=f)
    mp.render(f)
    f.close()
