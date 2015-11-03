#!/usr/bin/env python
'''
Created on 03.11.2015

@author: Marcus Degenkolbe
'''
#import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser
from acv import ACVCurve


if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", metavar="FILE",
                  help="Input GIMP curve filename", default=None)
    parser.add_option("-o", "--output", dest="output", metavar="FILE",
                  help="Output Adobe *.acv curve filename", default=None)
    (options, args) = parser.parse_args()
    
    if options.input == None:
        parser.print_help()
        exit(-1)
    if options.output == None:
        output = options.input + ".acv"
    else:
        output = options.output
    
    with open(options.input, 'rb') as f:
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

        acv_curve.to_file(output)