import numpy as np
from SegmentationUpsampler.UpsampleMultiLabels import upsample

def test_upsample_dimensions():
    image = np.zeros((10, 10, 10), dtype=float)  # Should be float per validation!
    image[2:5, 2:5, 2:5] = 1
    spacing = [1.0, 1.0, 1.0]
    scale = [0.5, 0.5, 0.5]  # Example: upsampling by 2x

    upsampled = upsample(image, scale, spacing=spacing)
    assert upsampled.shape[0] > image.shape[0]
    assert upsampled.shape[1] > image.shape[1]
    assert upsampled.shape[2] > image.shape[2]
    assert upsampled.dtype == image.dtype