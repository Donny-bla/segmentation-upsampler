import vtk
import numpy as np

class MeshVoxelizer:
    """
MESHVOXELIZER Integrates mesh data into SegmentedImage voxel grid.

DESCRIPTION:
    Operates as part of segmentation upsampling pipeline to convert 
    processed meshes back into volumetric representation. Uses VTK's 
    implicit distance functions for inside/outside testing.

USAGE:
    # As part of segmentation processing pipeline:
    voxelizer = MeshVoxelizer(segImg, label_index)
    voxelizer.voxeliseMesh()
    voxelizer.updateImg()

ATTRIBUTES:
    segImg         : ImageBase.SegmentedImage
        Main container for segmentation data
    binImg         : ImageBase.BinaryImage
        Label-specific processing data
    smoothedMatrix : numpy.ndarray 
        Pre-processed mask guiding voxelization
    mesh           : vtk.vtkPolyData
        Surface mesh for current label
    background     : numpy.ndarray
        Reference to output voxel grid (segImg.newImg)
    label          : int
        Current label value being processed
    gx, gy, gz     : int
        Dimensions of cropped processing area
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
        INIT Prepare voxelization for label-specific mesh.

        DESCRIPTION:
            Initializes voxelization parameters from SegmentedImage 
            container and specified label index.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Main processing container with spatial parameters
            i           : int
                Index of label to process in binaryImgList
        """
        self.segImg = segImg
        self.binImg = segImg.binaryImgList[i]

        # Inherit processing parameters from container
        self.smoothedMatrix = self.binImg.smoothedImg
        self.mesh = self.binImg.polyData
        self.background = self.segImg.newImg  # Direct reference to output grid
        self.label = self.binImg.label

        # Get spatial parameters for voxelization
        self.gx, self.gy, self.gz = np.shape(self.binImg.croppedImg)
        self.lower = self.binImg.bounds[0]

    def voxeliseMesh(self):
        """
        VOXELISEMESH Convert mesh to volumetric representation.

        DESCRIPTION:
            Performs grid-space conversion using:
            1. VTK implicit distance function for inside/outside testing
            2. Smoothed matrix guidance for selective processing
            3. Direct modification of background grid in SegmentedImage

        PROCESS:
            - Iterates through cropped processing region
            - Uses pre-computed smoothed matrix to skip processed areas
            - Applies mesh distance function for boundary resolution
            - Updates segmentation grid in-place
        """
        # VTK distance calculator for mesh inclusion testing
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(self.mesh)

        # Get grid spacing from parent container
        dx = self.segImg.dx

        # Process voxels in cropped region
        for k in np.arange(self.lower[0], self.gx + self.lower[0], dx[0]):
            for j in np.arange(self.lower[1], self.gy + self.lower[1], dx[1]):
                for i in np.arange(self.lower[2], self.gz + self.lower[2], dx[2]):
                    # Convert to output grid coordinates
                    px = round((k - self.lower[0])/dx[0]) + int(self.lower[0]/dx[0])
                    py = round((j - self.lower[1])/dx[1]) + int(self.lower[1]/dx[1])
                    pz = round((i - self.lower[2])/dx[2]) + int(self.lower[2]/dx[2])

                    # Apply pre-computed guidance matrix
                    sm_val = self.smoothedMatrix[int(k), int(j), int(i)]
                    if sm_val == 1:
                        self.background[px, py, pz] = self.label
                    elif sm_val == 0:
                        continue  # Skip fully processed areas
                    else:
                        # Resolve boundary regions with mesh testing
                        point = np.array([i-self.lower[2], 
                                        j-self.lower[1], 
                                        k-self.lower[0]], dtype=float)
                        if distanceFilter.EvaluateFunction(point) < 0:
                            self.background[px, py, pz] = self.label
                        
    def updateImg(self):
        """Propagate changes to SegmentedImage container."""
        self.segImg.setUpdatedImg(self.background)
