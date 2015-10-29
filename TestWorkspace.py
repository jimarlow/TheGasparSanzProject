__author__ = 'jimarlow'
from GasparConfig import *
import re

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




if __name__ == "__main__":
    print(mapFret("J"))
    print(mapFret("5"))
    print(mapFret("5T"))
    print(mapFret("10"))
    print(mapFret("10:."))

