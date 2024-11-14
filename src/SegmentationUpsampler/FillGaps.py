import numpy as np

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

    def __init__(self, newMatrix, smoothedMatrixList, dx, isovalue):
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
        self.newMatrix = newMatrix
        self.smoothedMatrixList = smoothedMatrixList
        self.dx = dx
        self.isovalue = isovalue
    
    def findSurroundings(self, x, y, z):
        """
        FINDSURROUNDINGS Find the surrounding non-zero voxels.

        DESCRIPTION:
            FINDSURROUNDINGS checks the 3x3x3 neighborhood around a 
            voxel to find surrounding non-zero voxels.

        INPUTS:
            x : int
                The x-coordinate of the voxel.
            y : int
                The y-coordinate of the voxel.
            z : int
                The z-coordinate of the voxel.

        OUTPUTS:
            surroundings : list of int
                A list of labels from the surrounding non-zero voxels.
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
        
        for x, y, z in zeros:
            inMesh = 0

            for smoothedMatrix in self.smoothedMatrixList:
                if smoothedMatrix[int(x*self.dx[0]), int(y*self.dx[1]), 
                                  int(z*self.dx[2])] > self.isovalue:
                    inMesh = 1
                    continue

            if inMesh:
                surroundings = self.findSurroundings(x, y, z)
                
                if surroundings:
                    mostFrequent = np.bincount(surroundings).argmax()
                    self.newMatrix[x, y, z] = mostFrequent

        print("Zeros filled")
        return self.newMatrix
