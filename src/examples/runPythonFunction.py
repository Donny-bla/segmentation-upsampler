from SegmentationUpsampler import UpsampleMultiLabels
import numpy as np

newMatrix = UpsampleMultiLabels.upsample(multiLabelMatrix, sigma, 
                                         targetVolume, scale, spacing, 
                                         iso, fillGaps, NB)
#np.save('multilabelTestShape.npy', multiLabelMatrix)
