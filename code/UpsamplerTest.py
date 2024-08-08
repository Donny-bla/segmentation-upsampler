from UpsampleMultiLabels import upsample
import numpy as np
import unittest

class TestAddArraysFunction(unittest.TestCase):
    def testNBTrueFillFalse(self):
        originalMatrix = np.load("../data/multilabelTestShape.npy")
        outputMatrix = np.load("../data/NBTrueFillGapsFalse.npy")
        sigma = 0.6
        targetVolume = 0
        scale = [0.5, 0.5, 0.5]
        spacing = [1, 1, 1]
        iso = 0.4
        fillGaps = False
        NB = True

        newMatrix = upsample(originalMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)
        np.testing.assert_array_equal(newMatrix, outputMatrix, "test not passed with NB speed up and no post gap filling")

    def testNBFalseFillFalse(self):
        originalMatrix = np.load("../data/multilabelTestShape.npy")
        outputMatrix = np.load("../data/NBFalseFillGapsFalse.npy")
        sigma = 0.6
        targetVolume = 0
        scale = [0.5, 0.5, 0.5]
        spacing = [1, 1, 1]
        iso = 0.4
        fillGaps = False
        NB = False

        newMatrix = upsample(originalMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)
        np.testing.assert_array_equal(newMatrix, outputMatrix, "test not passed with no NB speed up and no post gap filling")

    def testNBFalseFillTrue(self):
        originalMatrix = np.load("../data/multilabelTestShape.npy")
        outputMatrix = np.load("../data/NBFalseFillGapsTrue.npy")
        sigma = 0.6
        targetVolume = 0
        scale = [0.5, 0.5, 0.5]
        spacing = [1, 1, 1]
        iso = 0.4
        fillGaps = True
        NB = False

        newMatrix = upsample(originalMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)
        np.testing.assert_array_equal(newMatrix, outputMatrix, "test not passed with no NB speed up and post gap filling")

    def testNBTrueFillTrue(self):
        originalMatrix = np.load("../data/multilabelTestShape.npy")
        outputMatrix = np.load("../data/NBTrueFillGapsTrue.npy")
        sigma = 0.6
        targetVolume = 0
        scale = [0.5, 0.5, 0.5]
        spacing = [1, 1, 1]
        iso = 0.4
        fillGaps = True
        NB = True

        newMatrix = upsample(originalMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)
        np.testing.assert_array_equal(newMatrix, outputMatrix, "test not passed with NB speed up and post gap filling")        


if __name__ == '__main__':
    unittest.main()
