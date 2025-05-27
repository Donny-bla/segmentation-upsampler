import numpy as np
from SegmentationUpsampler.UpsampleMultiLabels import upsample
import os

base_path = os.path.dirname(__file__)
data_dir = os.path.join(base_path, "../data/")
image = np.load(os.path.join(data_dir, "multilabelTestShape.npy"))

def test_upsample_nbtrue_fillfalse():
    expected = np.load(os.path.join(data_dir, "NBTrueFillGapsFalse.npy"))
    scale = [0.5, 0.5, 0.5]
    sigma = 0.6
    iso = 0.4
    spacing = [1, 1, 1]
    fillGaps = False
    NB = True

    result = upsample(image, scale, sigma=sigma, iso=iso, spacing=spacing, fillGaps=fillGaps, NB=NB)
    np.testing.assert_array_equal(result, expected)

def test_upsample_nbfalse_fillfalse():
    expected = np.load(os.path.join(data_dir, "NBFalseFillGapsFalse.npy"))
    scale = [0.5, 0.5, 0.5]
    sigma = 0.6
    iso = 0.4
    spacing = [1, 1, 1]
    fillGaps = False
    NB = False

    result = upsample(image, scale, sigma=sigma, iso=iso, spacing=spacing, fillGaps=fillGaps, NB=NB)
    np.testing.assert_array_equal(result, expected)

def test_upsample_nbfalse_filltrue():
    expected = np.load(os.path.join(data_dir, "NBFalseFillGapsTrue.npy"))
    scale = [0.5, 0.5, 0.5]
    sigma = 0.6
    iso = 0.4
    spacing = [1, 1, 1]
    fillGaps = True
    NB = False

    result = upsample(image, scale, sigma=sigma, iso=iso, spacing=spacing, fillGaps=fillGaps, NB=NB)
    np.testing.assert_array_equal(result, expected)

def test_upsample_nbtrue_filltrue():
    expected = np.load(os.path.join(data_dir, "NBTrueFillGapsTrue.npy"))
    scale = [0.5, 0.5, 0.5]
    sigma = 0.6
    iso = 0.4
    spacing = [1, 1, 1]
    fillGaps = True
    NB = True

    result = upsample(image, scale, sigma=sigma, iso=iso, spacing=spacing, fillGaps=fillGaps, NB=NB)
    np.testing.assert_array_equal(result, expected)
