from __future__ import annotations

from enum import Enum, auto
import struct
from typing import AnyStr

import numpy as np


def readInt16(array: AnyStr, start: int, big_endian: bool = False) -> int:
    if big_endian:
        return struct.unpack('>h', (array[start:start + 2]))[0]
    return struct.unpack('h', (array[start:start + 2]))[0]


class GIMPCurveFormat(Enum):
    OLD = auto()
    NEW = auto()


class ACVCurve:

    def __init__(self, version: int = 4, curves: list[list[(int, int)]] | None = None):
        self._version = version
        if not curves:
            self._curves: list[list[(int, int)]] = []
        else:
            self._curves: list[list[(int, int)]] = curves

    @classmethod
    def fromACVFile(cls, filename: str) -> ACVCurve:
        version = 4
        curves = []
        with open(filename, "rb") as fp:
            data = fp.read()
            version = readInt16(data, 0x0, True)
            curveCount = readInt16(data, 0x2, True)
            offset = 0x0
            for c in range(curveCount):
                curve = []
                point_count = readInt16(data, 0x4 + offset, True)
                for p in range(point_count):
                    a = readInt16(data, 0x4 + offset + 0x2 + p * 0x4, True)
                    b = readInt16(data, 0x4 + offset + 0x4 + p * 0x4, True)
                    curve.append([a, b])
                offset += 0x2 + point_count * 4
                curves.append(curve)

        return cls(version=version, curves=curves)

    @classmethod
    def fromGIMPCurve(cls, filename: str) -> ACVCurve:
        fileFormat = cls.CheckFormat(filename)
        if fileFormat == GIMPCurveFormat.OLD:
            return cls.fromOldGIMPFormat(filename)
        elif fileFormat == GIMPCurveFormat.NEW:
            return cls.fromNewGIMPFormat(filename)
        return cls()

    @staticmethod
    def CheckFormat(filename: str) -> GIMPCurveFormat:
        with open(filename, "r") as fp:
            line = fp.readline()
            if line.startswith("# GIMP Curves File"):
                return GIMPCurveFormat.OLD
            return GIMPCurveFormat.NEW

    @classmethod
    def fromNewGIMPFormat(cls, filename: str) -> ACVCurve:
        curves = []

        with open(filename, "r") as fp:
            for line in fp.readlines():
                line = line.lstrip().replace(')', '').replace('\n', '')
                if line.startswith('(samples'):
                    curve = []
                    values = line.split(' ')[2:]
                    # y_values = [float(v)*255 for v in values]
                    y_values = np.array(values)
                    y_values = y_values.astype(np.float64)
                    x_values = np.arange(0, 1, 1 / 256.0)
                    z = np.polyfit(x_values, y_values, 5)
                    filepointer = np.poly1d(z)
                    x_new = np.linspace(x_values[0], x_values[-1], 16)
                    y_new = filepointer(x_new)
                    # plt.plot(x_values, y_values, 'g')
                    # plt.scatter(x_new, y_new, marker='o', color='b')
                    # plt.show()

                    for x, y in zip(x_new, y_new):
                        y, x = int(np.round(x * 255)), int(np.round(y * 255))
                        y = max(y, 0)
                        x = max(x, 0)
                        x = min(x, 255)
                        y = min(y, 255)
                        curve.append([x, y])
                    # plt.scatter([v[1] for v in curve], [v[0] for v in curve], marker='o', color='r')
                    # plt.show()
                    curves.append(curve)
        return cls(curves=curves)

    @classmethod
    def fromOldGIMPFormat(cls, filename: str) -> ACVCurve:
        curves = []

        with open(filename, "r") as fp:
            for line in fp.readlines():
                line = line.replace('\n', '')
                # ignore comments
                if line.startswith('#'):
                    continue
                curve = []
                points = [int(val) for val in line.strip().split(' ')]
                for i in range(0, len(points) - 1, 2):
                    # ignore points with -1 value
                    if points[i] != -1:
                        # x,y swapped?
                        curve.append([points[i + 1], points[i]])
                if len(curve) > 16:
                    print(f"Warning: {len(curve)} points in curve! Photoshop point limit is <= 16 points.")
                curves.append(curve)
        return cls(curves=curves)

    @property
    def curveCount(self) -> int:
        return len(self._curves)

    def appendCurve(self, curve: list[(int, int)]) -> None:
        self._curves.append(curve)

    def getCurves(self) -> list[list[(int, int)]]:
        return self._curves

    def __str__(self):
        return f"<ACVCurve version={self._version}, curves={self.curveCount}>"

    def toFile(self, filename: str) -> None:
        with open(filename, 'wb') as f:
            # write version default: 4
            f.write(struct.pack('>h', self._version))
            # write count of curves in the file
            f.write(struct.pack('>h', self.curveCount))
            # write points for each curve
            for c in self._curves:
                # count of points in the curve
                f.write(struct.pack('>h', len(c)))
                # curve points
                for v in c:
                    f.write(struct.pack('>h', v[0]))
                    f.write(struct.pack('>h', v[1]))

    def __eq__(self, other: ACVCurve) -> bool:
        for c1, c2 in zip(self._curves, other.getCurves()):
            for p1, p2 in zip(c1, c2):
                if p1[0] != p2[0] or p1[1] != p2[1]:
                    return False
        return True
