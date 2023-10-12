#!/usr/bin/env python
import sys
from optparse import OptionParser
from acv import ACVCurve

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", metavar="FILE",
                      help="Input GIMP curve filename", default=None)
    parser.add_option("-o", "--output", dest="output", metavar="FILE",
                      help="Output Adobe *.acv curve filename", default=None)
    (options, args) = parser.parse_args()
    if options.input is None and len(args) == 0:
        parser.print_help()
        sys.exit(-1)
    if options.input is not None:
        inputFile = options.input
    else:
        inputFile = args[0]

    if options.output is None:
        outputFile = f"{inputFile}.acv"
    else:
        outputFile = options.outputFile
        if not outputFile.endswith('.acv'):
            outputFile = f"{outputFile}.acv"

    curve = ACVCurve.fromGIMPCurve(inputFile)
    curve.toFile(outputFile)
    print(f"converted {inputFile} to {outputFile}")
