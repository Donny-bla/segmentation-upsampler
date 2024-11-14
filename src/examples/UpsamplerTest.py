from src.SegmentationUpsampler.UpsampleMultiLabels import upsample
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
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBTrueFillGapsFalse.npy"))
        fillGaps = False
        NB = True

        newMatrix = upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with NB speedup and no gap filling")

    def testNBFalseFillFalse(self):
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBFalseFillGapsFalse.npy"))
        fillGaps = False
        NB = False

        newMatrix = upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with no NB speedup and no gap filling")

    def testNBFalseFillTrue(self):
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBFalseFillGapsTrue.npy"))
        fillGaps = True
        NB = False

        newMatrix = upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with no NB speedup and gap filling")

    def testNBTrueFillTrue(self):
        originalMatrix = np.load(os.path.join(self.data_dir, 
                                  "multilabelTestShape.npy"))
        outputMatrix = np.load(os.path.join(self.data_dir, 
                                 "NBTrueFillGapsTrue.npy"))
        fillGaps = True
        NB = True

        newMatrix = upsample(originalMatrix, self.sigma, 
                             self.targetVolume, self.scale, 
                             self.spacing, self.iso, fillGaps, NB)

        np.testing.assert_array_equal(newMatrix, outputMatrix, 
            "test not passed with NB speedup and gap filling")

if __name__ == '__main__':
    unittest.main()
