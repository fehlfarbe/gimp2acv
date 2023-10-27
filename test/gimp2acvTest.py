import unittest
from acv import ACVCurve


class Gimp2AcvTest(unittest.TestCase):

    def testLoadSaveLoad(self):
        acvFile = "/tmp/curve.acv"
        curve1 = ACVCurve.fromGIMPCurve("../res/testcurves.gcv")
        curve1.toFile(acvFile)
        curve2 = ACVCurve.fromACVFile(acvFile)

        self.assertEqual(curve1.curveCount, curve2.curveCount)
        self.assertEqual(curve1, curve2)

    # def testLoadGCVAndPlot(self):
    #     gcvFile = "../res/arthurrackham.gcv"
    #     curve = ACVCurve.fromGIMPCurve(gcvFile)
    #     curve.plot()
    #     curve.toFile(f"{gcvFile}.acv")


if __name__ == '__main__':
    unittest.main()
