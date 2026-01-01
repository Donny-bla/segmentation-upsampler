import numpy as np
from scipy.signal import convolve
from scipy.ndimage import gaussian_filter

class ImagePreprocess:
    """
IMAGEPREPROCESS Geometric analysis and preprocessing for binary segmentation masks.

DESCRIPTION:
    Performs label-specific preprocessing including:
    - Surface area/volume ratio calculations
    - Adaptive Gaussian smoothing parameter computation
    - Isovalue determination for mesh extraction
    - Image cropping and filtering

METHODS:
    meshPreprocessing: Main preprocessing pipeline
    
ABOUT:
    author - Liangpu Liu, Rui Xu, Bradley Treeby
    date - 25th Aug 2024
    last update - 1st Mar 2025
    
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

    def __init__(self, segImg, i, isotropoic = True):
        """
        INIT Initialize preprocessing for specific label.

        INPUTS:
            segImg      : SegmentedImage
                Parent segmentation container
            i           : int
                Index in binaryImgList
            isotropoic  : bool
                Smoothing mode flag (True=isotropic)
        """
        self.binaryImg = segImg.binaryImgList[i]
        self.segImg = segImg
        self.array = np.int32(self.binaryImg.binImg)
        self.originalImg = self.binaryImg.binImg
        
        # Processing parameters
        self.sigma = 0        # Isotropic smoothing factor
        self.sigmaAnI = 0      # Anisotropic smoothing factors [x,y,z]
        self.isotropic = isotropoic  # Smoothing mode
        self.iso = 0          # Surface extraction threshold

        # Image data containers
        self.smoothMatrix = None   # Smoothed intensity field
        self.nonZeroShape = None   # Bounding box of non-zero region
        self.croppedMatrix = None  # Cropped region-of-interest

    def getVolume(self):
        """Calculate binary mask volume (voxel count)."""
        return np.sum(np.concatenate(self.array))
    
    def getSurfaceArea(self):
        """Calculate surface area using 26-neighborhood kernel."""
        surfaceAreaKernel = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                    [[0,-1,0],[-1,6,-1],[0,-1,0]],
                                    [[0,0,0],[0,-1,0],[0,0,0]]])
        surface = convolve(self.array, surfaceAreaKernel, mode="same")
        return np.sum(np.abs(np.concatenate(surface)))/2
    
    def getAxialSurfaceArea(self):
        """Calculate axis-aligned surface areas (X,Y,Z directions)."""
        # X-axis kernel
        surfaceAreaKernel_X = np.array([[[0,0,0],[0,0,0],[0,0,0]],
                                      [[0,-1,0],[-1,4,-1],[0,-1,0]],
                                      [[0,0,0],[0,0,0],[0,0,0]]])
        # Y-axis kernel                                    
        surfaceAreaKernel_Y = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                      [[0,0,0],[-1,4,-1],[0,0,0]],
                                      [[0,0,0],[0,-1,0],[0,0,0]]])
        # Z-axis kernel
        surfaceAreaKernel_Z = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                      [[0,-1,0],[0,4,0],[0,-1,0]],
                                      [[0,0,0],[0,-1,0],[0,0,0]]])
        
        # Calculate directional surface areas
        surface_X = convolve(self.array, surfaceAreaKernel_X, mode="same")
        surface_Y = convolve(self.array, surfaceAreaKernel_Y, mode="same")
        surface_Z = convolve(self.array, surfaceAreaKernel_Z, mode="same")
        
        return (np.sum(np.abs(np.concatenate(surface_X)))/2,
                np.sum(np.abs(np.concatenate(surface_Y)))/2,
                np.sum(np.abs(np.concatenate(surface_Z)))/2)
    
    def grossParameterAV(self):
        """Compute surface-to-volume ratio metric (A√/V∛)."""
        return (self.getSurfaceArea()**(1/2))/(self.getVolume()**(1/3))
    
    def axialParameter(self):
        """Get normalized axial surface area ratios."""
        Ax, Ay, Az = self.getAxialSurfaceArea()
        A = self.getSurfaceArea()
        return Ax/A, Ay/A, Az/A
    
    def computeSigma(self):
        """Determine isotropic sigma based on AV ratio thresholds."""
        AV = self.grossParameterAV()
        # Piecewise linear mapping from AV ratio to sigma
        if AV<2.6:
            self.sigma = 0.4
        elif 2.6<=AV<2.9:
            self.sigma = 0.4 + (AV-2.6)/((2.9-2.6)/(0.5-0.4))
        elif 2.9<=AV<4.5:
            self.sigma = 0.5 + (AV-2.9)/((4.5-2.9)/(0.75-0.5))
        elif 4.5<=AV<5:
            self.sigma = 0.75 + (AV-4.5)/((5-4.5)/(1-0.75))
        elif AV>=5:
            self.sigma = 1

    def computeAnIsotropicSigma(self):
        """Compute directional sigmas based on surface anisotropy."""
        Ax, Ay, Az = self.axialParameter()
        M = max(Ax, Ay, Az)
        self.computeSigma()
        # Scale sigmas by axial ratios
        self.sigmaAnI = [self.sigma*Ax/M, self.sigma*Ay/M, self.sigma*Az/M]
        
    def computeIso(self):
        """Iterative isovalue search for AV ratio preservation."""
        originalAV = self.grossParameterAV()
        minDiff = 9999        
        stepsize = 0.001

        # Linear search through isovalues
        isovalue = 0
        while isovalue < 0.6:
            isovalue += stepsize
            self.array = np.int32(self.croppedMatrix >= isovalue)
            thisAV = self.grossParameterAV()
            if abs(thisAV - originalAV) < minDiff:
                minDiff = abs(thisAV - originalAV)
                self.iso = isovalue

    def setSigma(self):
        """Apply computed or predefined sigma to BinaryImage."""
        if self.segImg.sigma == -1:  # Auto-compute mode
            if self.isotropic:
                self.computeSigma()
                self.binaryImg.setSigma(self.sigma)
            else:
                self.computeAnIsotropicSigma()
                self.binaryImg.setSigma(self.sigmaAnI)
        else:  # Use predefined sigma
            self.binaryImg.setSigma(self.segImg.sigma)

    def setIsovalue(self):
        """Apply computed or predefined iso to BinaryImage."""
        if self.segImg.iso == -1:  # Auto-compute mode
            self.computeIso()
            self.binaryImg.setIsovalue(self.iso)
        else:  # Use predefined iso
            self.binaryImg.setIsovalue(self.segImg.iso)

    def applyGaussianFilter(self, image):
        """Apply Gaussian smoothing with current sigma parameters."""
        return gaussian_filter(image, sigma=self.binaryImg.sigma)
    
    def cropLabels(self, image):
        """Crop image to minimal non-zero bounding box.
        
        RETURNS:
            tuple: (croppedMatrix, nonZeroShape)
        """
        nonZeroLabels = np.nonzero(image)
        lowerBound = np.min(nonZeroLabels, axis=1)
        upperBound = np.max(nonZeroLabels, axis=1) + 1
        return (image[lowerBound[0]:upperBound[0], 
                     lowerBound[1]:upperBound[1], 
                     lowerBound[2]:upperBound[2]],
                (lowerBound, upperBound))

    def meshPreprocessing(self):
        """Full preprocessing pipeline:
        1. Sigma computation
        2. Gaussian smoothing
        3. ROI cropping
        4. Isovalue determination
        """
        self.setSigma()
        self.smoothMatrix = self.applyGaussianFilter(self.originalImg)
        self.croppedMatrix, self.nonZeroShape = self.cropLabels(self.smoothMatrix)
        self.croppedMatrix =  np.ascontiguousarray(self.croppedMatrix)
        self.setIsovalue()

    def updateImg(self):
        """Store processed data in BinaryImage container."""
        self.binaryImg.setPreprocessedImg(self.smoothMatrix, 
                                        self.croppedMatrix, 
                                        self.nonZeroShape)