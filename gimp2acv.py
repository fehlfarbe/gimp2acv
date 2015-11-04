#!/usr/bin/env python
'''
Created on 03.11.2015

@author: Marcus Degenkolbe
'''
#import matplotlib.pyplot as plt
import sys
import numpy as np
from optparse import OptionParser
from acv import ACVCurve

def is_old_format(f):
    line = f.readline()
    f.seek(0)
    if line.startswith("# GIMP Curves File"):
        return True
    return False

def convert_new_format(f):
        acv_curve = ACVCurve()

        for l in f.readlines():
            l = l.lstrip().replace(')', '').replace('\n', '')
            if l.startswith('(samples'):
                curve = []
                values = l.split(' ')[2:]
                y_values = [float(v)*255 for v in values]
                y_values = np.array(values)
                y_values = y_values.astype(np.float64)
                x_values = np.arange(0, 1, 1/256.0)
                z = np.polyfit(x_values, y_values, 5)
                f = np.poly1d(z)
                x_new = np.linspace(x_values[0], x_values[-1], 16)
                y_new = f(x_new)
                #plt.plot(x_values, y_values, 'g')
                #plt.scatter(x_new, y_new, marker='o', color='b')
                #plt.show()
                
                
                for x,y in zip(x_new, y_new):
                    y, x = int(np.round(x*255)), int(np.round(y*255))
                    y = max(y, 0)
                    x = max(x, 0)
                    x = min(x, 255)
                    y = min(y, 255)
                    curve.append([x, y])
                #plt.scatter([v[1] for v in curve], [v[0] for v in curve], marker='o', color='r')
                #plt.show()  
                acv_curve.curves.append(curve)
        return acv_curve
        #acv_curve.to_file(output)
        
def convert_old_format(f):
    acv_curve = ACVCurve()
    
    for line in f.readlines():
        line = line.replace('\n', '')
        # ignore comments
        if line.startswith('#'):
            continue
        
        curve = []
        points = [int(val) for val in line.strip().split(' ')]
        for i in xrange(0,len(points)-1,2):
            # ignore points with -1 value
            if points[i] != -1:
                # x,y swapped?
                curve.append([points[i+1], points[i]])
        if len(curve) > 16:
            print "Warning: %d points in curve! Photoshop point limit is <= 16 points." % len(curve)
        acv_curve.curves.append(curve)    
    return acv_curve
    
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
        input = options.input
    else:
        input = args[0]
    
    if options.output is None:
        output = input + ".acv"
    else:
        output = options.output
        if not output.endswith('.acv'):
            output += ".acv"
    
    with open(input, 'rb') as f:
        if is_old_format(f):
            print "curve is in old format"
            curve = convert_old_format(f)
        else:
            print "curve is in new format"
            curve = convert_new_format(f)
        
        curve.to_file(output)
        print "converted %s to %s" % (input, output)