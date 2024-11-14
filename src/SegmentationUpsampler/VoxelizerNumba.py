import vtk
import numpy as np
import numba as nb

class MeshVoxelizerNumba:
    """
MESHVOXELIZERNUMBA Voxelize a 3D mesh into a grid.

DESCRIPTION:
    MESHVOXELIZERNUMBA is a class designed to voxelize a 3D mesh 
    into a grid using the Numba library for accelerated processing. 
    The class takes in a 3D mesh and generates a voxelized 
    representation on a specified background grid.

USAGE:
    voxelizer = MeshVoxelizerNumba(mesh, smoothedMatrix, x, y, z, 
                                   scale, spacing, background, 
                                   bounds, label)
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
    author        : Liangpu Liu, Rui Xu, Bradley Treeby
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
        INIT Initialize the MeshVoxelizerNumba.

        DESCRIPTION:
            INIT initializes the MeshVoxelizerNumba class with the input 
            mesh, smoothed matrix, grid dimensions, scale, spacing, 
            background grid, bounds, and label for voxelization.

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
            VOXELISEMESH creates a voxelized representation of the input 
            mesh on the background grid by evaluating the implicit 
            function for each grid point.

        OUTPUTS:
            updatedGrid   : numpy.ndarray
                The updated background grid with the voxelized mesh.
        """
        # Create an implicit function of the scaled mesh
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(self.mesh)

        dx = [self.scale[0] / self.spacing[0], self.scale[1] / self.spacing[1], 
              self.scale[2] / self.spacing[2]]
        self.background, points = pointWiseProcess(self.gx, self.gy, self.gz, 
                                                   dx, self.lower, 
                                                   self.smoothedMatrix, 
                                                   self.label, 
                                                   self.background)
        for p in points:
            distance = distanceFilter.EvaluateFunction(p)
            # Update background grid with label if point is inside the mesh
            if distance < 0:
                px = round(p[2] / dx[0]) + int(self.lower[0] / dx[0])
                py = round(p[1] / dx[1]) + int(self.lower[1] / dx[1])
                pz = round(p[0] / dx[2]) + int(self.lower[2] / dx[2])
                self.background[px, py, pz] = self.label

        return self.background

@nb.njit
def pointWiseProcess(gx, gy, gz, dx, lower, smoothedMatrix, label, 
                     background):
    """
    POINTWISEPROCESS Voxelize the mesh by processing each grid point.

    DESCRIPTION:
        POINTWISEPROCESS iterates through each grid point, checks the 
        corresponding value in the smoothed matrix, and updates the 
        background grid with the voxelized mesh.

    INPUTS:
        gx             : int
            Number of grid points along the X-axis.
        gy             : int
            Number of grid points along the Y-axis.
        gz             : int
            Number of grid points along the Z-axis.
        dx             : list of float
            Spacing between the grid points after scaling.
        lower          : numpy.ndarray
            Lower bounds of the grid after scaling.
        smoothedMatrix : numpy.ndarray
            Matrix that determines which points are ignored during 
            voxelization.
        label          : int
            The label to assign to voxels inside the mesh.
        background     : numpy.ndarray
            The background grid to which the voxelized mesh will be added.

    OUTPUTS:
        background     : numpy.ndarray
            The updated background grid with the voxelized mesh.
        ApplyDistanceFilter : list of list of float
            Points that need to be evaluated for distance filtering.
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
