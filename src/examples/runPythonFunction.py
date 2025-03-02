from SegmentationUpsampler import UpsampleMultiLabels
import numpy as np

try: s = sigma
except: s = -1
try: i = iso
except: i = -1
try: space = spacing
except: space = [1, 1, 1]
try: f = fillGaps
except: f = False
try: nb = Numba
except: nb = True

newMatrix = UpsampleMultiLabels.upsample(multiLabelMatrix, scale, sigma=s, iso=i, spacing=space, fillGaps=f, NB=nb)
#np.save('multilabelTestShape.npy', multiLabelMatrix)
