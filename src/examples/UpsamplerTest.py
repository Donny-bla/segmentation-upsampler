from SegmentationUpsampler import UpsampleMultiLabels
import numpy as np
import unittest
import os

class TestUpsampleFunction(unittest.TestCase):
    def setUp(self):
        # Setup paths relative to the script location
        base_path = os.path.dirname(__file__)
        self.data_dir = os.path.join(base_path, "../data/")
        self.sigma = 0.6
        self.targetVolume = 0
        self.scale = [0.5, 0.5, 0.5]
        self.spacing = [1, 1, 1]
        self.iso = 0.4

    def testNBTrueFillFalse(self):
        print("Running testcase: NBTrueFillFalse")
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBTrueFillGapsFalse.npy"))
        fillGaps = False
        NB = True

        newMatrix = UpsampleMultiLabels.upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with NB speedup and no gap filling")
        print("Success: testNBTrueFillFalse")
        
    def testNBFalseFillFalse(self):
        print("Running testcase: NBFalseFillFalse")
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBFalseFillGapsFalse.npy"))
        fillGaps = False
        NB = False

        newMatrix = UpsampleMultiLabels.upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with no NB speedup and no gap filling")
        print("Success: testNBFalseFillFalse")

    def testNBFalseFillTrue(self):
        print("Running testcase: NBFalseFillTrue")
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBFalseFillGapsTrue.npy"))
        fillGaps = True
        NB = False

        newMatrix = UpsampleMultiLabels.upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with no NB speedup and gap filling")
        print("Success: testNBFalseFillTrue")

    def testNBTrueFillTrue(self):
        print("Running testcase: NBTrueFillTrue")
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBTrueFillGapsTrue.npy"))
        fillGaps = True
        NB = True

        newMatrix = UpsampleMultiLabels.upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with NB speedup and gap filling")
        print("Success: testNBTrueFillTrue")

if __name__ == '__main__':
    unittest.main()
