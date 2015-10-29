__author__ = 'jimarlow'
from GasparConfig import *

# Postscript commands to map Times-Roman to Times-Roman-ISOLatin1
# We need to do this mapping to get access to special characters for Spanish etc.
psMapTimesRoman = '''/Times-Roman findfont dup length dict begin { 1 index /FID ne {def}
{pop pop} ifelse
} forall
/Encoding ISOLatin1Encoding def currentdict
end
/Times-Roman-ISOLatin1 exch definefont pop'''

# These text strings are Postscript commands
newpath = "newpath"
show = "show"
moveto = "moveto"
rmoveto = "rmoveto"
lineto = "lineto"
arc = "arc"
arcn = "arcn"
curveto = "curveto"
stroke = "stroke"
fill = "fill"
setlinewidth = "setlinewidth"
findfont = "findfont"
setfont = "setfont"
scalefont = "scalefont"
stringwidth = "stringwidth"
div = "div"
dup = "dup"
pop = "pop"
neg = "neg"
sub = "sub"
setrgbcolor = "setrgbcolor"
showpage = "showpage"


# Postscript utility functions
# Convert the args into a space delimited string
def ps(*args): return " ".join([str(x) for x in args])


# Convert the argument to a Postscript string
def psStr(s): return '(' + str(s) + ')'


# Escape the argument with a forward slash
def psEsc(s): return '/' + str(s)


# Font mapping
def psMapFont(name="Times-Roman"): return psMapTimesRoman.replace("Times-Roman", name)


# Postscript graphics primitives
def psRGBColor(r=0, g=0, b=0): return ps(r, g, b, setrgbcolor)


def psCircle(x, y, radius, lineWidth=LINEWIDTH):
    return ps(newpath, x, y, radius, "0", "360", arc, lineWidth, setlinewidth, stroke)


def psFilledCircle(x, y, radius, lineWidth=LINEWIDTH):
    return ps(newpath, x, y, radius, "0", "360", arc, fill, lineWidth, setlinewidth, stroke)


def psCurveTo(x1, y1, x2, y2, x3, y3, lineWidth=LINEWIDTH):
    return ps(newpath, x1, y1, moveto, x1, y1, x2, y2, x3, y3, curveto, lineWidth, setlinewidth, stroke)


def psLine(x1, y1, x2, y2, lineWidth=LINEWIDTH):
    return ps(newpath, x1, y1, moveto, x2, y2, lineto, lineWidth, setlinewidth, stroke)


def psHorizontalLine(x, y, length, lineWidth=LINEWIDTH): return psLine(x, y, x + length, y, lineWidth)


def psVerticalLine(x, y, height, lineWidth=LINEWIDTH): return psLine(x, y, x, y + height, lineWidth)


def psPage(): return showpage


# Postscript text functions
def toMappedFontName(name):
    if "-ISOLatin1" in name:
        return name
    else:
        return name + "-ISOLatin1"


def psCenteredText(text="Hello world", pageWidth=595, y=742, size=28, face="Times-Roman"):
    return ps(psEsc(toMappedFontName(face)), findfont, size, scalefont, setfont, pageWidth, "2", div, y, moveto,
              psStr(text), dup, stringwidth, pop, "2", div, neg, "0", rmoveto, show)


def psRightJustifiedText(text="Hello world", pageWidth=595, y=720, size=14, face="Times-Roman"):
    return ps(psEsc(toMappedFontName(face)), findfont, size, scalefont, setfont, pageWidth, psStr(text), stringwidth,
              pop, sub, y, moveto, psStr(text), show)


def psLeftJustifiedText(text="Hello world", leftMargin=200, y=720, size=14, face="Times-Roman"):
    return ps(psEsc(toMappedFontName(face)), findfont, size, scalefont, setfont, leftMargin, psStr(text), stringwidth,
              pop, sub, y, moveto, psStr(text), show)


# Gaspar visual syntax
def psOverSemicircle(x, y, radius, lineWidth=1):
    return ps(newpath, x, y, radius, "0", "180", arc, lineWidth, setlinewidth, stroke)


def psUnderSemicircle(x, y, radius, lineWidth=1):
    return ps(newpath, x, y, radius, "0", "180", arcn, lineWidth, setlinewidth, stroke)


def psStem(x, y, height, lineWidth=LINEWIDTH): return psLine(x, y, x, y + height, lineWidth)


# The start of the tail is the top of the note line
# The end of the tail is {-TAILENDOFFSET, -TAILENDOFFSET} down and the to the right of the start
TAILENDOFFSET = 4
# The vertical separation between tails
TAILVERTICALSPACING = 3


# tailNum = the number of the tail
# The first tail (tailNum = 1) goes from the top of the tick, the next tail from the top-TAILVERTICALSPACING etc.
# tailNum < 1 - nothing to draw
def psTail(x, y, height, tailNum, lineWidth=LINEWIDTH):
    if tailNum < 1: return ""

    tailNum = tailNum -1
    x1 = x
    y1 = y + height - tailNum * TAILVERTICALSPACING
    x2 = x + TAILENDOFFSET
    y2 = y + height - TAILENDOFFSET - tailNum * TAILVERTICALSPACING
    return psLine(x1, y1, x2, y2, lineWidth)


def psDrawTails(x, y, height, numberOfTails, lineWidth=LINEWIDTH):
    return " ".join([psTail(x, y, height, tailNum, lineWidth) for tailNum in range(1, numberOfTails)])


def psTickBody(x, y, radius=GC.tickBodyRadius, lineWidth=LINEWIDTH):
    return psCircle(x - radius, y, radius, lineWidth)


def psTickBodyFilled(x, y, radius=GC.tickBodyRadius, lineWidth=LINEWIDTH):
    return psFilledCircle(x - radius, y, radius, lineWidth)


def psTickDot(x, y, radius=1, lineWidth=LINEWIDTH):
    return psFilledCircle(x + 3, y, radius, lineWidth)


def psText(text="Hello world", x=100, y=100, size=12.5, face="Times-Roman-ISOLatin1"):
    return ps(psEsc(face), findfont, size, scalefont, setfont, newpath, x, y, moveto, psStr(text), show)


if __name__ == "__main__":
    print(psDrawTails(100, 100, 10, 3))
