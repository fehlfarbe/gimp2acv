#!/usr/bin/env python
'''
Created on 03.11.2015

@author: Marcus Degenkolbe
'''
from acv import read_int16, ACVCurve

INPUT = "curve3.acv"
INPUT = "curve2_ps.acv"

if __name__ == '__main__':
    
    with open(INPUT, 'rb') as f:
        acv_curve = ACVCurve()
        data = f.read()
        version = read_int16(data, 0x0, True)
        curve_count = read_int16(data, 0x2, True)
        print "version:", version
        print "curve count:", curve_count
        
        acv_curve.version = version
        
        offset = 0x0
        for c in range(curve_count):
            curve = []
            point_count = read_int16(data, 0x4+offset, True)
            print "curve", c, "points:", point_count
            for p in range(point_count):
                a = read_int16(data, 0x4+offset+0x2+p*0x4, True)
                b = read_int16(data, 0x4+offset+0x4+p*0x4, True)
                curve.append([a, b])
                print "\t", a, b
            offset += 0x2 + point_count*4
            #print curve, point_count, offset
            acv_curve.curves.append(curve)
            
        print acv_curve
        acv_curve.to_file(INPUT+"_new.acv")