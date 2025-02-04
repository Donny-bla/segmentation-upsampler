import numpy as np
import numba as nb

class FillGaps:
    """
FILLGAPS Fill gaps in a voxelized matrix.

DESCRIPTION:
    FILLGAPS is a class designed to fill gaps in a voxelized matrix 
    by evaluating the surrounding voxels and assigning the most 
    frequent label to the gaps.

USAGE:
    gapFiller = FillGaps(newMatrix, smoothedMatrixList, dx, isovalue)
    filledMatrix = gapFiller.fillZeros()

INPUTS:
    newMatrix       : numpy.ndarray
        The voxelized matrix with gaps to be filled.
    smoothedMatrixList : list of numpy.ndarray
        A list of smoothed matrices used to check if a voxel belongs 
        to a mesh.
    dx              : list of float
        The scale factors along each axis.
    isovalue        : float
        The isovalue threshold for determining if a voxel belongs 
        to a mesh.

OUTPUTS:
    filledMatrix    : numpy.ndarray
        The voxelized matrix with gaps filled.

ABOUT:
    author          : Liangpu Liu, Rui Xu, and Bradley Treeby.
    date            : 25th Aug 2024
    last update     : 25th Aug 2024

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
    #(self, newMatrix, smoothedMatrixList, dx, isovalue):
        """
        INIT Initialize the FillGaps class.

        DESCRIPTION:
            INIT initializes the FillGaps class with the voxelized 
            matrix, a list of smoothed matrices, scale factors, and the 
            isovalue threshold.

        INPUTS:
            newMatrix       : numpy.ndarray
                The voxelized matrix with gaps to be filled.
            smoothedMatrixList : list of numpy.ndarray
                A list of smoothed matrices used to check if a voxel 
                belongs to a mesh.
            dx              : list of float
                The scale factors along each axis.
            isovalue        : float
                The isovalue threshold for determining if a voxel belongs 
                to a mesh.
        """
        self.segImg = segImg
        self.newMatrix = self.segImg.newImg
        self.dx = self.segImg.dx
        self.isovalue = self.segImg.iso

    def fillZeros(self):
        """
        FILLZEROS Fill gaps in the voxelized matrix.

        DESCRIPTION:
            FILLZEROS finds all zero-valued voxels in the matrix and 
            attempts to fill them by evaluating the surrounding voxels 
            and using the most frequent label.

        OUTPUTS:
            filledMatrix : numpy.ndarray
                The voxelized matrix with gaps filled.
        """
        zeros = np.argwhere(self.newMatrix == 0)
        smoothedList = []
        for i in range(self.segImg.getLabelNumber()):
            binImg = self.segImg.binaryImgList[i]
            smoothedList.append(binImg.smoothedImg)

        self.newMatrix = pointWiseProcess(zeros, smoothedList, self.dx, self.isovalue, self.newMatrix)
    
    def updateImg(self):
        self.segImg.setUpdatedImg(self.newMatrix)
        print("Zeros filled")
        
@nb.njit
def pointWiseProcess(zeros, smoothedList, dx, isovalue, newMatrix):

    for x, y, z in zeros:
        inMesh = 0
        for smoothedMatrix in smoothedList:

            if smoothedMatrix[int(x*dx[0]), int(y*dx[1]), int(z*dx[2])] > isovalue:
                inMesh = 1
                continue

        if inMesh:
            surroundings = []
            xx, yy, zz = np.shape(newMatrix)
            for i in range(max(0, x-1), min(x+2, xx-1)):
                for j in range(max(0, y-1), min(y+2, yy-1)):
                    for k in range(max(0, z-1), min(z+2, zz-1)):
                        if (i, j, k) != (x, y, z) and newMatrix[i, j, k] != 0:
                            surroundings.append(newMatrix[i, j, k])
            if surroundings:
                mostFrequent = np.bincount(surroundings).argmax()
                newMatrix[x, y, z] = mostFrequent
    
    return newMatrix
