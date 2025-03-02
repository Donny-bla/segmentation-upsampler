
import numpy as np

class FillGaps:
    """
FILLGAPS Post-processing of upsampled segmentation to resolve interstitial voids.

DESCRIPTION:
    Operates on SegmentedImage container to fill unassigned voxels between 
    labeled regions. Uses:
    - Smoothed guidance maps from preprocessing
    - Neighborhood majority voting
    - Mesh inclusion validation

USAGE:
    # As part of segmentation pipeline:
    gap_filler = FillGaps(segImg)
    gap_filler.fillZeros()
    gap_filler.updateImg()

ATTRIBUTES:
    segImg      : ImageBase.SegmentedImage
        Container with voxel grid and processing parameters
    newMatrix   : numpy.ndarray
        Reference to segImg's output grid (modified in-place)
    dx          : tuple
        Grid spacing from SegmentedImage
    isovalue    : float
        Threshold for mesh inclusion checks

ABOUT:
    author      : Liangpu Liu, Rui Xu, Bradley Treeby
    date        : 25th Aug 2024
    last update :  1st Mar 2025

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

    def __init__(self, segImg):
        """
        INIT Prepare gap filling for SegmentedImage output.

        DESCRIPTION:
            Initializes gap filler with references to processing data
            from SegmentedImage container.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Container with upsampled grid and binary image data
        """
        self.segImg = segImg
        self.newMatrix = self.segImg.newImg
        self.dx = self.segImg.dx
        self.isovalue = self.segImg.iso
    
    def findSurroundings(self, x, y, z):
        """
        FINDSURROUNDINGS Identify neighboring labels for void voxel.

        DESCRIPTION:
            Examines 26-connected neighborhood to collect adjacent labels.
            Handles grid boundary conditions.

        PARAMETERS:
            x, y, z     : int
                Grid coordinates of target void voxel

        RETURNS:
            list[int]   : Non-zero labels in 3x3x3 neighborhood
        """
        surroundings = []
        xx, yy, zz = self.newMatrix.shape
        for i in range(max(0, x-1), min(x+2, xx-1)):
            for j in range(max(0, y-1), min(y+2, yy-1)):
                for k in range(max(0, z-1), min(z+2, zz-1)):
                    if (i, j, k) != (x, y, z) and self.newMatrix[i, j, k] != 0:
                        surroundings.append(self.newMatrix[i, j, k])
        return surroundings

    def fillZeros(self):
        """
        FILLZEROS Resolve interstitial voids in upsampled grid.

        PROCESS:
            1. Identify unassigned (zero) voxels
            2. Validate against original meshes using smoothed fields
            3. For valid voids, apply majority label from neighborhood
        """
        zeros = np.argwhere(self.newMatrix == 0)
        binImgList = [self.segImg.binaryImgList[i] for i in range(self.segImg.getLabelNumber())]
        for x, y, z in zeros:
            inMesh = 0

            for binImg in binImgList:
                smoothedMatrix = binImg.smoothedImg
                if smoothedMatrix[int(x*self.dx[0]), int(y*self.dx[1]), 
                                  int(z*self.dx[2])] > self.isovalue:
                    inMesh = 1
                    continue

            if inMesh:
                surroundings = self.findSurroundings(x, y, z)
                
                if surroundings:
                    mostFrequent = np.bincount(surroundings).argmax()
                    self.newMatrix[x, y, z] = mostFrequent

    def updateImg(self):
        """Finalize changes in SegmentedImage container."""
        self.segImg.setUpdatedImg(self.newMatrix)
        print("Zeros filled")
        