import numpy as np
from SegmentationUpsampler import RigorousPreprocess
from SegmentationUpsampler import Extractor
from SegmentationUpsampler import FillGaps
from SegmentationUpsampler import LabelSeparater
from SegmentationUpsampler import Voxelizer
from SegmentationUpsampler import VoxelizerNumba
from SegmentationUpsampler import ImageBase

"""
Upsamples a labelled image

DESCRIPTION:
    UpsampleMultiLabels upsamples a segmented image using a mesh based
    method.

    This function utilized Python vtk library for mesh processing.

USAGE:
    call from this function:
    newMatrix = upsample(
        multiLabelMatrix, sigma, targetVolume, 
        scale, spacing, iso, fillGaps, NB
    )
    call from Matlab:
    newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                          "newMatrix", ...
                          multiLabelMatrix = py.numpy.array(Matrix), ...
                          sigma = sigma, ...
                          targetVolume = Volume, ...
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
    targetVolume 
            - floating number, use to generate isovalue automatically, 
              not used unless iso is 0
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
    last update - 25th Aug 2024
    
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
def ValidateInputs(multiLabelMatrix, sigma, scale, spacing, iso, targetVolume, fillGaps, NB):

    if not (isinstance(multiLabelMatrix, np.ndarray) and 
            multiLabelMatrix.ndim == 3 and 
            multiLabelMatrix.dtype in [np.float32, np.float64]):
        raise ValueError("MultiLabelMatrix should be a 3D numpy array of " +
                         "floating numbers.")
    
    if not (isinstance(sigma, (float, int)) and sigma >= 0):
        raise ValueError("Sigma should be a floating number >= 0.")
    
    if not isinstance(targetVolume, (float, int)):
        raise ValueError("TargetVolume should be a floating number.")
    
    if not (len(scale) == 3 and 
            all(isinstance(x, (float, int)) for x in scale)):
        raise ValueError("Scale should be a list of 3 floating numbers.")
    
    if not (len(spacing) == 3 and 
            all(isinstance(x, (float, int)) for x in spacing)):
        raise ValueError("Spacing should be a list of 3 floating numbers.")
    
    if not (isinstance(iso, (float, int)) and 0 <= iso <= 1):
        raise ValueError("Iso should be a floating number from 0 to 1.")
    
    if not isinstance(fillGaps, bool):
        raise ValueError("FillGaps should be a boolean value.")
    
    if not isinstance(NB, bool):
        raise ValueError("NB should be a boolean value.")
    
    return True


def upsample(multiLabelMatrix, sigma, scale, spacing, iso, targetVolume = 0, fillGaps = True, NB = False):
    ValidateInputs(multiLabelMatrix, sigma, scale, spacing, iso, targetVolume, fillGaps, NB)

    segImg = ImageBase.SegmentedImage(multiLabelMatrix, sigma, scale, spacing, iso, targetVolume)
    
    #gx, gy, gz = np.shape(multiLabelMatrix)
    #dx = [scale[0] / spacing[0], scale[1] / spacing[1], 
    #      scale[2] / spacing[2]]
    #background = np.zeros((int(gx / dx[0]), int(gy / dx[1]), 
    #                       int(gz / dx[2])), dtype=np.uint8)
    smoothedList = []

    labelSeparationInstance = LabelSeparater.LabelSeparation(segImg)
    labelSeparationInstance.separateLabels()
    labelSeparationInstance.updateImg()

    #separateMatrices, _, labels = segImg.getAllLabels()

    for i in range(segImg.getLabelNumber()):
        #singleLabelMatrix = separateMatrix[i]
        #label = labels[i]

        preprocessor = RigorousPreprocess.MeshPreprocessor(segImg, i)
        preprocessor.meshPreprocessing()
        preprocessor.updateImg()
        
        binImg = segImg.binaryImgList[i]
        isosurfaceExtractor = Extractor.IsosurfaceExtractor(segImg, i)
        isosurfaceExtractor.extractIsosurface()
        isosurfaceExtractor.updateImg()

        binImg = segImg.binaryImgList[i]
        print(np.shape(binImg.faces))

        #x, y, z = np.shape(croppedMatrix)
        if NB:
            voxelizer = VoxelizerNumba.MeshVoxelizerNumba(segImg, i)
        else:
            voxelizer = Voxelizer.MeshVoxelizer(segImg, i)

        voxelizer.voxeliseMesh()
        voxelizer.updateImg()

    if fillGaps:
        gapFiller = FillGaps.FillGaps(segImg)
        gapFiller.fillZeros()
        gapFiller.updateImg()

    newMatrix = segImg.background
    return newMatrix

newMatrix = upsample(multiLabelMatrix, sigma, scale, spacing, iso)