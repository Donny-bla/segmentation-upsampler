import numpy as np
from src.SegmentationUpsampler.RigorousPreprocess import MeshPreprocessor
from src.SegmentationUpsampler.Extractor import IsosurfaceExtractor
from src.SegmentationUpsampler.Voxelizer import MeshVoxelizer
from src.SegmentationUpsampler.VoxelizerNumba import MeshVoxelizerNumba
from src.SegmentationUpsampler.LabelSeparater import LabelSeparation
from src.SegmentationUpsampler.FillGaps import FillGaps
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
def validateInputs(multiLabelMatrix, sigma, targetVolume, scale, spacing, 
                   iso, fillGaps, NB):
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


def upsample(multiLabelMatrix, sigma, targetVolume, scale, spacing, iso, 
             fillGaps, NB):
    validateInputs(multiLabelMatrix, sigma, targetVolume, scale, spacing, 
                   iso, fillGaps, NB)

    gx, gy, gz = np.shape(multiLabelMatrix)
    dx = [scale[0] / spacing[0], scale[1] / spacing[1], 
          scale[2] / spacing[2]]
    background = np.zeros((int(gx / dx[0]), int(gy / dx[1]), 
                           int(gz / dx[2])), dtype=np.uint8)
    smoothedList = []

    labelSeparationInstance = LabelSeparation(multiLabelMatrix)
    labelSeparationInstance.separateLabels()
    separateMatrices, _, labels = labelSeparationInstance.getResults()

    for i in range(len(separateMatrices)):
        singleLabelMatrix = separateMatrices[i]
        label = labels[i]

        preprocessor = MeshPreprocessor(singleLabelMatrix, sigma, 
                                        targetVolume)
        smoothedMatrix, isovalue, croppedMatrix, bounds = (
            preprocessor.meshPreprocessing())
        smoothedList.append(smoothedMatrix)
        croppedMatrix = np.ascontiguousarray(croppedMatrix)

        if targetVolume:
            iso = isovalue

        isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso)
        faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

        x, y, z = np.shape(croppedMatrix)

        if NB:
            voxelizer = MeshVoxelizerNumba(polyData, smoothedMatrix, x, y, 
                                           z, scale, spacing, background, 
                                           bounds, label)
        else:
            voxelizer = MeshVoxelizer(polyData, smoothedMatrix, x, y, z, 
                                      scale, spacing, background, bounds, 
                                      label)
        background = voxelizer.voxeliseMesh()

    newMatrix = background

    if fillGaps:
        gapFiller = FillGaps(newMatrix, smoothedList, dx, isovalue)
        newMatrix = gapFiller.fillZeros()

    return newMatrix


if __name__ == "__main__":
    newMatrix = upsample(multiLabelMatrix, sigma, targetVolume, scale, 
                         spacing, iso, fillGaps, NB)
    np.save('multilabelTestShape.npy', multiLabelMatrix)
