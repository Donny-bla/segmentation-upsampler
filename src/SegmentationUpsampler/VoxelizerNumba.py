import vtk
import numpy as np
import numba as nb

class MeshVoxelizerNumba:
    """
MESHVOXELIZERNUMBA Accelerated mesh voxelization using Numba-VTK hybrid processing.

DESCRIPTION:
    Optimized version of MeshVoxelizer that combines Numba-accelerated grid 
    processing with VTK's mesh operations. Part of segmentation upsampling 
    pipeline. Features:
    - Numba-optimized grid traversal
    - VTK-based mesh inclusion testing
    - Selective processing using guidance matrix

USAGE:
    # As part of segmentation processing pipeline:
    voxelizer = MeshVoxelizerNumba(segImg, label_index)
    voxelizer.voxeliseMesh()
    voxelizer.updateImg()

ATTRIBUTES:
    segImg         : ImageBase.SegmentedImage
        Main container for segmentation data
    binImg         : ImageBase.BinaryImage
        Label-specific processing data
    smoothedMatrix : numpy.ndarray 
        Pre-computed guidance matrix (1=set, 0=ignore, other=test)
    mesh           : vtk.vtkPolyData
        Target surface mesh for voxelization
    background     : numpy.ndarray
        Reference to output grid in SegmentedImage
    label          : int
        Current label identifier
    gx, gy, gz     : int
        Dimensions of cropped processing region
    lower          : tuple
        Minimum bounds of cropped region

ABOUT:
    author        : Liangpu Liu, Rui Xu, Bradley Treeby
    date          : 25th Aug 2024
    last update   :  1st Mar 2025


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

    def __init__(self, segImg, i):
        """
        INIT Prepare Numba-accelerated voxelizer for label processing.

        DESCRIPTION:
            Initializes from SegmentedImage container and label index.
            Inherits spatial parameters and processing masks.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Main processing container
            i           : int
                Index in binaryImgList for target label
        """
        self.segImg = segImg
        self.binImg = segImg.binaryImgList[i]

        self.smoothedMatrix = self.binImg.smoothedImg
        self.mesh = self.binImg.polyData
        self.background = self.segImg.newImg
        self.label = self.binImg.label

        self.gx, self.gy, self.gz = np.shape(self.binImg.croppedImg)
        self.lower = self.binImg.bounds[0]

    def voxeliseMesh(self):
        """
        VOXELISEMESH Execute hybrid Numba/VTK voxelization pipeline.

        DESCRIPTION:
            1. Uses Numba-accelerated pre-processing to:
               - Apply guidance matrix rules
               - Collect boundary points needing mesh testing
            2. Applies VTK distance filter to boundary points
            3. Updates output grid in SegmentedImage
        """
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(self.mesh)

        dx = self.segImg.dx
        self.background, points = pointWiseProcess(self.gx, self.gy, self.gz, 
                                                   dx, self.lower, 
                                                   self.smoothedMatrix, 
                                                   self.label, 
                                                   self.background)
        for p in points:
            distance = distanceFilter.EvaluateFunction(p)
            if distance < 0:
                px = round(p[2] / dx[0]) + int(self.lower[0] / dx[0])
                py = round(p[1] / dx[1]) + int(self.lower[1] / dx[1])
                pz = round(p[0] / dx[2]) + int(self.lower[2] / dx[2])
                self.background[px, py, pz] = self.label
    
    def updateImg(self):
        """Propagate grid changes to SegmentedImage container."""
        self.segImg.setUpdatedImg(self.background)

@nb.njit
def pointWiseProcess(gx, gy, gz, dx, lower, smoothedMatrix, label, 
                     background):
    """
    NUMBA-ACCELERATED GRID PROCESSING

    DESCRIPTION:
        First-stage processing that handles:
        - Grid coordinate calculations
        - Guidance matrix application
        - Boundary point collection

    PARAMETERS:
        gx, gy, gz   : int
            Cropped region dimensions
        dx           : (float, float, float)
            Grid spacing from SegmentedImage
        lower        : (int, int, int)
            Minimum bounds of cropped region
        smoothedMatrix : array[float]
            3D guidance matrix
        label        : int
            Target label value
        background   : array[int]
            Output grid reference

    RETURNS:
        background   : array[int]
            Updated output grid reference
        test_points  : list[array[float]]
            Collected points needing mesh testing
    """
    ApplyDistanceFilter = []

    for k in np.arange(lower[0], gx + lower[0], dx[0]):
        for j in np.arange(lower[1], gy + lower[1], dx[1]):
            for i in np.arange(lower[2], gz + lower[2], dx[2]):
                px = round((k - lower[0]) / dx[0]) + int(lower[0] / dx[0])
                py = round((j - lower[1]) / dx[1]) + int(lower[1] / dx[1])
                pz = round((i - lower[2]) / dx[2]) + int(lower[2] / dx[2])

                # A point is ignored if its corresponding point on the 
                # smoothed matrix is 1 or 0
                if smoothedMatrix[int(k), int(j), int(i)] == 1:
                    background[px, py, pz] = label
                elif smoothedMatrix[int(k), int(j), int(i)] == 0:
                    continue 
                else:
                    ApplyDistanceFilter.append(
                        [i - lower[2], j - lower[1], k - lower[0]])

    return background, ApplyDistanceFilter
