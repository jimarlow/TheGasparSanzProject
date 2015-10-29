__author__ = 'jimarlow'

from GasparPostscriptCompiler import *
import os.path
import argparse

parser = argparse.ArgumentParser(description='Compile a .sanz file to Postscript.')
parser.add_argument('sanzFileName', help='The name of the .sanz file to convert to Postscript')

args = parser.parse_args()

if os.path.isfile(args.sanzFileName):
    tabset(args.sanzFileName)
else:
    print("File ", args.sanzFileName, " does not exist")
