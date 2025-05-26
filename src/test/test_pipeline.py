
import numpy as np
from SegmentationUpsampler.UpsampleMultiLabels import upsample_multilabel

def test_upsample_multilabel_dimensions():
    image = np.zeros((10, 10, 10), dtype=int)
    image[2:5, 2:5, 2:5] = 1
    spacing = [1.0, 1.0, 1.0]
    upsampled, new_spacing = upsample_multilabel(image, spacing, dx=0.5)
    assert upsampled.shape[0] > image.shape[0]
    assert upsampled.shape[1] > image.shape[1]
    assert upsampled.shape[2] > image.shape[2]
    assert all(ns < os for ns, os in zip(new_spacing, spacing))
    assert upsampled.dtype == image.dtype
