'''
Created on 03.11.2015

@author: Marcus Degenkolbe

Adobe ACV file format doc: https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_pgfId-1056330
'''
import struct

def read_int16(array, start, big_endian=False):
    if big_endian:
        return struct.unpack('>h', (array[start:start+2]))[0]
    return struct.unpack('h', (array[start:start+2]))[0]

class ACVCurve():
    
    version = 4
    curves = []
    
    def __init__(self):
        pass
    
    @property
    def curve_count(self):
        return len(self.curves)
    
    def __str__(self):
        return "<ACVCurve version=%d, curves=%d>" % \
                (self.version, self.curve_count)
                
    def to_file(self, filename):
        with open(filename, 'wb') as f:
            # write version default: 4
            f.write(struct.pack('>h', self.version))
            # write count of curves in the file
            f.write(struct.pack('>h', self.curve_count))
            # write points for each curve
            for c in self.curves:
                # count of points in the curve
                f.write(struct.pack('>h', len(c)))
                # curve points
                for v in c:
                    f.write(struct.pack('>h', v[0]))
                    f.write(struct.pack('>h', v[1]))