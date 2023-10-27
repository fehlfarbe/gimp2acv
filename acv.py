from __future__ import annotations

from enum import Enum, auto
import struct
from typing import AnyStr

import numpy as np
from numpy.polynomial.polynomial import Polynomial
from scipy.interpolate import lagrange


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
        if curves is None:
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
                    y = readInt16(data, 0x4 + offset + 0x2 + p * 0x4, True)
                    x = readInt16(data, 0x4 + offset + 0x4 + p * 0x4, True)
                    curve.append([x, y])
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
                    # read all samples and convert to 0-255 range
                    samples = np.array(line.split(' ')[2:]).astype(np.float64) * 255
                    # interpolate lagrange polynom and extract the important points
                    curve = cls._interpolateLagrangeFromSamples(samples)
                # extract original points
                # if line.startswith("(points"):
                #     curve = []
                #     values = line.split(' ')[2:]
                #     for x, y in zip(values[0::2], values[1::2]):
                #         x, y = int(np.round(float(x) * 255)), int(np.round(float(y) * 255))
                #         curve.append((y, x))
                    curves.append(curve)
        return cls(curves=curves)

    @staticmethod
    def _interpolateLagrangeFromSamples(samples: np.array, numberOfPoints: int = 16) -> list[tuple[int, int]]:
        x_values = np.arange(0, len(samples))
        # fit a polynom that approximates the samples
        fittedPolynom = Polynomial.fit(x_values, samples, 21)
        # get points on fittedPolynom for chebyshev nodes
        def chebyshev_nodes(a, b, n):
            nodes = [(a + b) / 2 + ((b - a) / 2) * np.cos((2 * k - 1) * np.pi / (2 * n)) for k in range(1, n + 1)]
            return np.array(sorted(nodes))
        chebyshevX = chebyshev_nodes(0, x_values[-1], numberOfPoints)
        chebyshevY = fittedPolynom(chebyshevX)
        # calculate lagrange polynom and extract y values for chebyshev nodes
        lagrangePoly = lagrange(chebyshevX, chebyshevY)
        importance = np.abs(lagrangePoly.coeffs)
        indices = np.sort(np.argsort(importance)[-numberOfPoints:])
        lagrangePoints = lagrangePoly(chebyshevX[indices])
        # export values for chebyshev nodes and cast them to int
        lagrangePoints = [(int(x), int(y)) for x, y in zip(chebyshevX[indices], lagrangePoints)]
        return lagrangePoints

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
                        curve.append([points[i], points[i + 1]])
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

    def plot(self) -> None:
        import matplotlib.pyplot as plt

        for curve in self._curves:
            points = np.array([(x, y) for x, y in curve])
            plt.plot(points[:, 0], points[:, 1])
            plt.scatter(points[:, 0], points[:, 1], marker='o')
        plt.xlim(0, 255)
        plt.ylim(0, 255)
        plt.show()

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
                for x, y in c:
                    f.write(struct.pack('>h', y))
                    f.write(struct.pack('>h', x))

    def __eq__(self, other: ACVCurve) -> bool:
        for c1, c2 in zip(self._curves, other.getCurves()):
            for p1, p2 in zip(c1, c2):
                if p1[0] != p2[0] or p1[1] != p2[1]:
                    return False
        return True
