import numpy as np
from scipy.ndimage import gaussian_filter

class MeshPreprocessor:
    """
MESH PREPROCESSOR Preprocess a 3D mesh using Gaussian filtering.

DESCRIPTION:
    MESH PREPROCESSOR is a class designed for preprocessing a 3D mesh 
    using Gaussian filtering and binary search for an optimal isovalue. 
    The class helps in smoothing the mesh, cropping out zero labels, 
    and determining the isovalue that approximates a target volume.

USAGE:
    preprocessor = MeshPreprocessor(originalMatrix, sigma, targetVolume)
    smoothMatrix, isovalue, croppedMatrix, nonZeroShape = \
        preprocessor.meshPreprocessing()

INPUTS:
    originalMatrix : numpy.ndarray
        3D array representing the original mesh.
    sigma          : float
        Standard deviation for the Gaussian filter.
    targetVolume   : float
        Target volume for binary search of isovalue.

OUTPUTS:
    smoothMatrix   : numpy.ndarray
        3D array representing the smoothed mesh.
    isovalue       : float
        Optimal isovalue for the smoothed mesh.
    croppedMatrix  : numpy.ndarray
        3D array representing the cropped matrix after removing 
        zero labels.
    nonZeroShape   : tuple
        Bounds of the cropped matrix after removing zero labels.

ABOUT:
    author         : Liangpu Liu, Rui Xu, and Bradley Treeby
    date           : 25th Aug 2024
    last update    : 25th Aug 2024

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

    def __init__(self, originalMatrix, sigma, targetVolume):
        """
        INIT Initialize the MeshPreprocessor.

        DESCRIPTION:
            INIT initializes the MeshPreprocessor class with the original 
            3D matrix, the Gaussian filter's standard deviation, and the 
            target volume for determining the optimal isovalue.

        INPUTS:
            originalMatrix : numpy.ndarray
                3D array representing the original mesh.
            sigma          : float
                Standard deviation for the Gaussian filter.
            targetVolume   : float
                Target volume for binary search of isovalue.
        """
        self.originalMatrix = originalMatrix
        self.sigma = sigma
        self.targetVolume = targetVolume
        self.smoothMatrix = None
        self.isovalue = None
        self.nonZeroShape = None
        self.croppedMatrix = None

    def applyGaussianFilter(self, image):
        """
        APPLYGAUSSIANFILTER Apply Gaussian filter to a 3D image.

        DESCRIPTION:
            APPLYGAUSSIANFILTER smooths the input 3D image using a Gaussian 
            filter with a specified standard deviation.

        INPUTS:
            image : numpy.ndarray
                The 3D array representing the image.

        OUTPUTS:
            filteredImage : numpy.ndarray
                The filtered 3D image.
        """
        if self.sigma == 0:
            return image
        filteredImage = gaussian_filter(image, sigma=self.sigma)
        return filteredImage

    def cropLabels(self):
        """
        CROPLABELS Crop zero labels to speed up the following process.

        DESCRIPTION:
            CROPLABELS identifies the non-zero regions in the smoothed 
            matrix and crops out the zero labels, returning the cropped 
            matrix and its bounds.

        OUTPUTS:
            croppedMatrix : numpy.ndarray
                Cropped matrix after removing zero labels.
            nonZeroShape  : tuple
                Bounds of the cropped matrix.
        """
        nonZeroLabels = np.nonzero(self.smoothMatrix)
        lowerBound = np.min(nonZeroLabels, axis=1)
        upperBound = np.max(nonZeroLabels, axis=1) + 1
        croppedMatrix = self.smoothMatrix[lowerBound[0]:upperBound[0], 
                                          lowerBound[1]:upperBound[1], 
                                          lowerBound[2]:upperBound[2]]
        nonZeroShape = (lowerBound, upperBound)
        return croppedMatrix, nonZeroShape

    def meshPreprocessing(self):
        """
        MESHPREPROCESSING Perform preprocessing on a 3D mesh.

        DESCRIPTION:
            MESHPREPROCESSING performs the full preprocessing pipeline 
            on a 3D mesh, including Gaussian smoothing, binary search 
            for optimal isovalue, and cropping zero labels.

        OUTPUTS:
            smoothMatrix  : numpy.ndarray
                3D array representing the smoothed mesh.
            isovalue      : float
                Optimal isovalue for the smoothed mesh.
            croppedMatrix : numpy.ndarray
                3D array representing the cropped matrix after removing 
                zero labels.
            nonZeroShape  : tuple
                Bounds of the cropped matrix.
        """
        # Gaussian smoothing
        self.smoothMatrix = self.applyGaussianFilter(self.originalMatrix)

        # Compute original and smoothed volumes
        originalVolume = np.sum(self.originalMatrix == 1)

        # Binary search for isovalue
        upper = np.max(self.smoothMatrix)
        lower = np.min(self.smoothMatrix)
        self.isovalue = (upper + lower) / 2
        smoothedVolume = np.sum(self.smoothMatrix > self.isovalue)

        volumeDiff = -1
        if smoothedVolume < originalVolume:
            volumeDiff = 1

        v = volumeDiff / (np.log(np.abs(smoothedVolume - originalVolume) / 
                                 originalVolume))

        ii = 0
        while ((v >= (self.targetVolume + 0.005) or 
                v <= (self.targetVolume - 0.005)) and ii < 1000):
            ii += 1
            if v < self.targetVolume:
                lower = self.isovalue
            else:
                upper = self.isovalue

            self.isovalue = (upper + lower) / 2
            smoothedVolume = np.sum(self.smoothMatrix > self.isovalue)

            volumeDiff = -1
            if smoothedVolume < originalVolume:
                volumeDiff = 1

            v = (-1 / (np.log(np.abs(smoothedVolume - originalVolume) / 
                              originalVolume))) * volumeDiff

        self.croppedMatrix, self.nonZeroShape = self.cropLabels()

        return self.smoothMatrix, self.isovalue, self.croppedMatrix, \
               self.nonZeroShape
