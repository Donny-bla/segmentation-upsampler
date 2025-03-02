import numpy as np
import numba as nb

class FillGaps:
    """
FILLGAPSNUMBA Numba-accelerated post-processing for interstitial void filling.

DESCRIPTION:
    Optimized version of FillGaps that uses Numba for performance-critical 
    operations. Part of segmentation upsampling pipeline. Features:
    - Numba-accelerated neighborhood analysis
    - Mesh existence validation using precomputed smooth fields
    - Majority voting from 26-connected neighborhood

USAGE:
    # As part of segmentation processing pipeline:
    gap_filler = FillGaps(segImg)
    gap_filler.fillZeros()
    gap_filler.updateImg()

ATTRIBUTES:
    segImg      : ImageBase.SegmentedImage
        Container with upsampled grid and processing parameters
    newMatrix   : numpy.ndarray
        Reference to segImg's output grid (modified in-place)
    dx          : tuple
        Grid spacing from original to upsampled space
    isovalue    : float
        Threshold for mesh inclusion validation

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
        INIT Prepare gap filler with SegmentedImage data.

        DESCRIPTION:
            Initializes with references to processing data from 
            SegmentedImage container.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Container with upsampled grid and binary image data
        """
        self.segImg = segImg
        self.newMatrix = self.segImg.newImg
        self.dx = self.segImg.dx
        self.isovalue = self.segImg.iso

    def fillZeros(self):
        """
        FILLZEROS Execute Numba-accelerated void filling.

        PROCESS:
            1. Identify remaining zeros in upsampled grid
            2. Collect smoothed guidance fields from all labels
            3. Delegate to Numba-optimized processing:
               - Coordinate scaling
               - Mesh inclusion checks
               - Neighborhood analysis
        """
        zeros = np.argwhere(self.newMatrix == 0)
        smoothedList = []
        for i in range(self.segImg.getLabelNumber()):
            binImg = self.segImg.binaryImgList[i]
            smoothedList.append(binImg.smoothedImg)

        self.newMatrix = pointWiseProcess(zeros, smoothedList, self.dx, self.isovalue, self.newMatrix)
    
    def updateImg(self):
        """Finalize changes in SegmentedImage container."""
        self.segImg.setUpdatedImg(self.newMatrix)
        print("Zeros filled")
        
@nb.njit
def pointWiseProcess(zeros, smoothed_list, dx, isovalue, new_matrix):
    """
    NUMBA-ACCELERATED VOID PROCESSING CORE

    PARAMETERS:
        zeros         : array[int, int, int]
            Array of (x,y,z) coordinates for void voxels
        smoothed_list : list[array[float]]
            List of smoothed guidance fields per label
        dx            : (float, float, float)
            Scaling factors between grid spaces
        isovalue      : float
            Threshold for mesh inclusion
        new_matrix    : array[int]
            Output grid to modify (in-place)

    RETURNS:
        array[int]    : Modified output grid with filled voids
    """
    for x, y, z in zeros:
        # Convert to original scale coordinates
        orig_x = int(x * dx[0])
        orig_y = int(y * dx[1])
        orig_z = int(z * dx[2])
        
        # Check against all label guidance fields
        in_mesh = False
        for smoothed in smoothed_list:
            if smoothed[orig_x, orig_y, orig_z] > isovalue:
                in_mesh = True
                break

        if in_mesh:
            # Analyze 26-connected neighborhood
            surroundings = []
            xx, yy, zz = new_matrix.shape
            for i in range(max(0, x-1), min(x+2, xx)):
                for j in range(max(0, y-1), min(y+2, yy)):
                    for k in range(max(0, z-1), min(z+2, zz)):
                        if (i, j, k) != (x, y, z) and new_matrix[i, j, k] != 0:
                            surroundings.append(new_matrix[i, j, k])
            
            if surroundings:
                # Apply majority label
                new_matrix[x, y, z] = np.bincount(np.array(surroundings)).argmax()
    
    return new_matrix