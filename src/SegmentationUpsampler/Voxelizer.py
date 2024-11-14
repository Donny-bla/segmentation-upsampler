import vtk
import numpy as np

class MeshVoxelizer:
    """
MESHVOXELIZER Voxelize a 3D mesh into a grid.

DESCRIPTION:
    MESHVOXELIZER is a class designed to voxelize a 3D mesh into 
    a grid. The class processes each point in the grid, evaluating 
    whether the point lies inside the mesh, and labels the point 
    accordingly on a background grid.

USAGE:
    voxelizer = MeshVoxelizer(mesh, smoothedMatrix, x, y, z, scale, 
                              spacing, background, bounds, label)
    updatedGrid = voxelizer.voxeliseMesh()

INPUTS:
    mesh          : vtk.vtkPolyData
        The input mesh to be voxelized.
    smoothedMatrix: numpy.ndarray
        Matrix that determines which points are ignored during 
        voxelization.
    x             : int
        Number of grid points along the X-axis.
    y             : int
        Number of grid points along the Y-axis.
    z             : int
        Number of grid points along the Z-axis.
    scale         : float
        Scale factor to adjust the size of the grid.
    spacing       : tuple
        The spacing between the grid points along each axis.
    background    : numpy.ndarray
        The background grid to which the voxelized mesh will be added.
    bounds        : list of tuples
        The bounds of the grid [(x_min, x_max), (y_min, y_max), 
        (z_min, z_max)].
    label         : int
        The label to assign to voxels inside the mesh.

OUTPUTS:
    updatedGrid   : numpy.ndarray
        The updated background grid with the voxelized mesh.

ABOUT:
    author        : Liangpu Liu, Rui Xu, and Bradley Treeby
    date          : 25th Aug 2024
    last update   : 25th Aug 2024

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

    def __init__(self, mesh, smoothedMatrix, x, y, z, scale, spacing, 
                 background, bounds, label):
        """
        INIT Initialize the MeshVoxelizer.

        DESCRIPTION:
            INIT initializes the MeshVoxelizer class with the input mesh, 
            smoothed matrix, grid dimensions, scale, spacing, background 
            grid, bounds, and label for voxelization.

        INPUTS:
            mesh          : vtk.vtkPolyData
                The input mesh to be voxelized.
            smoothedMatrix: numpy.ndarray
                Matrix that determines which points are ignored during 
                voxelization.
            x             : int
                Number of grid points along the X-axis.
            y             : int
                Number of grid points along the Y-axis.
            z             : int
                Number of grid points along the Z-axis.
            scale         : float
                Scale factor to adjust the size of the grid.
            spacing       : tuple
                The spacing between the grid points along each axis.
            background    : numpy.ndarray
                The background grid to which the voxelized mesh will be 
                added.
            bounds        : list of tuples
                The bounds of the grid [(x_min, x_max), (y_min, y_max), 
                (z_min, z_max)].
            label         : int
                The label to assign to voxels inside the mesh.
        """
        self.mesh = mesh
        self.gx = x
        self.gy = y
        self.gz = z
        self.scale = scale
        self.spacing = spacing
        self.lower = bounds[0]
        self.background = background
        self.label = label
        self.smoothedMatrix = smoothedMatrix

    def voxeliseMesh(self):
        """
        VOXELISEMESH Voxelizes the input mesh and updates the background grid.

        DESCRIPTION:
            VOXELISEMESH processes each point in the grid to determine if 
            it lies within the mesh. If a point is inside the mesh, it is 
            labeled accordingly on the background grid.

        OUTPUTS:
            updatedGrid   : numpy.ndarray
                The updated background grid with the voxelized mesh.
        """
        # Create an implicit function of the scaled mesh
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(self.mesh)

        dx = [self.scale[0] / self.spacing[0],
              self.scale[1] / self.spacing[1], 
              self.scale[2] / self.spacing[2]]

        for k in np.arange(self.lower[0], self.gx + self.lower[0], dx[0]):
            for j in np.arange(self.lower[1], self.gy + self.lower[1], dx[1]):
                for i in np.arange(self.lower[2], self.gz + self.lower[2], dx[2]):
                    px = round((k - self.lower[0]) / dx[0]) + int(self.lower[0] / dx[0])
                    py = round((j - self.lower[1]) / dx[1]) + int(self.lower[1] / dx[1])
                    pz = round((i - self.lower[2]) / dx[2]) + int(self.lower[2] / dx[2])

                    if self.smoothedMatrix[int(k), int(j), int(i)] == 1:
                        self.background[px, py, pz] = self.label
                    elif self.smoothedMatrix[int(k), int(j), int(i)] == 0:
                        continue 
                    else:
                        point = np.array([i - self.lower[2], j - self.lower[1], 
                                          k - self.lower[0]], dtype=float)
                        distance = distanceFilter.EvaluateFunction(point)

                        if distance < 0.0:
                            self.background[px, py, pz] = self.label
                        
        return self.background
