import numpy as np
import Extractor
import FillGaps
import LabelSeparater
import Voxelizer
import VoxelizerNumba
import ImageBase
import FillGapsNumba
import Preprocess
#from SegmentationUpsampler import Extractor
#from SegmentationUpsampler import FillGaps
#from SegmentationUpsampler import LabelSeparater
#from SegmentationUpsampler import Voxelizer
#from SegmentationUpsampler import VoxelizerNumba
#from SegmentationUpsampler import ImageBase
#from SegmentationUpsampler import FillGapsNumba
#from SegmentationUpsampler import Preprocess

"""
Upsamples a labelled image

DESCRIPTION:
    UpsampleMultiLabels upsamples a segmented image using a mesh based
    method.

    This function utilized Python vtk library for mesh processing.

USAGE:
    call from this function:
    newMatrix = upsample(
        multiLabelMatrix, sigma, 
        scale, spacing, iso, fillGaps, NB
    )
    call from Matlab:
    newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                          "newMatrix", ...
                          multiLabelMatrix = py.numpy.array(Matrix), ...
                          sigma = sigma, ...
                          scale = [dx, dx, dx], ...
                          spacing = [1 1 1], ...
                          iso = isovalue, ...
                          fillGaps = true, ...
                          NB = true);

INPUTS:
    multiLabelMatrix 
            - 3D numpy array of segmented image
    spacing - list of 3 floating numbers, spacing of input image
    scale   - list of 3 floating numbers, scale of upsampling
    
    sigma   - floating number >= 0, Gaussian smoothing parameter 
    iso     - floating number from 0 to 1, isovalue to extract surface 
              mesh
    
    fillGaps 
            - boolean, optional post processing to fill gaps between 
              connecting object
    NB      - boolean, optional cpu boosting used in mesh voxelization
    
    OUTPUTS:
    newMatrix
            - upsampled segmented matrix

ABOUT:
    author - Liangpu Liu, Rui Xu, Bradley Treeby
    date - 25th Aug 2024
    last update - 4th Feb 2025
    
LICENSE:
    This function is part of the pySegmentationUpsampler.
    Copyright (C) 2024  Liangpu Liu, Rui Xu, and Bradley Treeby.

This file is part of pySegmentationUpsampler, pySegmentationUpsampler
is free software: you can redistribute it and/or modify it under the 
terms of the GNU Lesser General Public License as published by the 
Free Software Foundation, either version 3 of the License, or (at 
your option) any later version.

pySegmentationUpsampler is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public 
License along with pySegmentationUpsampler. If not, see 
<http://www.gnu.org/licenses/>.

"""
def ValidateInputs(multiLabelMatrix, sigma, scale, spacing, iso, fillGaps, NB):

    if not (isinstance(multiLabelMatrix, np.ndarray) and 
            multiLabelMatrix.ndim == 3 and 
            multiLabelMatrix.dtype in [np.float32, np.float64]):
        raise ValueError("MultiLabelMatrix should be a 3D numpy array of " +
                         "floating numbers.")
    
    if not (isinstance(sigma, (float, int)) and (sigma >= 0 or sigma == -1)):
        raise ValueError("Sigma should be a floating number >= 0, set to -1 to generate sigma automatically.")
    
    if not (len(scale) == 3 and 
            all(isinstance(x, (float, int)) for x in scale)):
        raise ValueError("Scale should be a list of 3 floating numbers.")
    
    if not (len(spacing) == 3 and 
            all(isinstance(x, (float, int)) for x in spacing)):
        raise ValueError("Spacing should be a list of 3 floating numbers.")
    
    if not (isinstance(iso, (float, int)) and (0 <= iso <= 1 or iso == -1)):
        raise ValueError("Iso should be a floating number from 0 to 1, set to -1 to generate isovalue automatically.")
    
    if not isinstance(fillGaps, bool):
        raise ValueError("FillGaps should be a boolean value.")
    
    if not isinstance(NB, bool):
        raise ValueError("NB should be a boolean value.")
    
    return True


def upsample(multiLabelMatrix, scale, sigma = -1, iso = -1, spacing = [1, 1, 1], fillGaps = False, NB = True):
    
    ValidateInputs(multiLabelMatrix, sigma, scale, spacing, iso, fillGaps, NB)

    segImg = ImageBase.SegmentedImage(multiLabelMatrix, sigma, scale, spacing, iso)

    labelSeparationInstance = LabelSeparater.LabelSeparation(segImg)
    labelSeparationInstance.separateLabels()
    labelSeparationInstance.updateImg()

    for i in range(segImg.getLabelNumber()):
        preprocesser = Preprocess.ImagePreprocess(segImg, i, False)
        preprocesser.meshPreprocessing()
        preprocesser.updateImg()


        isosurfaceExtractor = Extractor.IsosurfaceExtractor(segImg, i)
        isosurfaceExtractor.extractIsosurface()
        isosurfaceExtractor.updateImg()

        if NB:
            voxelizer = VoxelizerNumba.MeshVoxelizerNumba(segImg, i)
        else:
            voxelizer = Voxelizer.MeshVoxelizer(segImg, i)

        voxelizer.voxeliseMesh()
        voxelizer.updateImg()

    if fillGaps:
        if NB:
            gapFiller = FillGapsNumba.FillGaps(segImg)
        else:
            gapFiller = FillGaps.FillGaps(segImg)
        gapFiller.fillZeros()
        gapFiller.updateImg()

    newMatrix = segImg.newImg

    return newMatrix

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

newMatrix = upsample(multiLabelMatrix, scale, sigma=s, iso=i, spacing=space, fillGaps=f, NB=nb)
