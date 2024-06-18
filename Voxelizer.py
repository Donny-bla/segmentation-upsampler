import vtk
import numpy as np
import numba as nb

class MeshVoxelizer:
    """
    A class to voxelize a 3D mesh into a grid.

    Attributes:
    -----------
    mesh : vtk.vtkPolyData
        The input mesh to be voxelized.
    gx : int
        Number of grid points along the X-axis.
    gy : int
        Number of grid points along the Y-axis.
    gz : int
        Number of grid points along the Z-axis.
    scale : float
        The scale factor to adjust the size of the grid.
    lower : np.ndarray
        Lower bounds of the grid after scaling.
    background : np.ndarray
        The background grid to which the voxelized mesh will be added.
    label : int
        The label to assign to voxels inside the mesh.
    voxelValues : np.ndarray, optional
        Array to hold the voxel values (initialized as None).
    """

    def __init__(self, mesh, smoothedMatrix, x, y, z, scale, background, bounds, label):
        """
        Initialize the MeshVoxelizer.

        Parameters:
        ----------
        mesh : vtk.vtkPolyData
            The input mesh to be voxelized.
        x : int
            Number of grid points along the X-axis.
        y : int
            Number of grid points along the Y-axis.
        z : int
            Number of grid points along the Z-axis.
        scale : float
            Scale factor to adjust the size of the grid.
        background : np.ndarray
            The background grid to which the voxelized mesh will be added.
        bounds : list of tuples
            The bounds of the grid [(x_min, x_max), (y_min, y_max), (z_min, z_max)].
        label : int
            The label to assign to voxels inside the mesh.
        """
        self.mesh = mesh
        self.gx = x
        self.gy = y
        self.gz = z
        self.scale = scale
        self.lower = np.array(bounds[0])
        self.background = background
        self.label = label
        self.voxelValues = None
        self.smoothedMatrix = smoothedMatrix

    def voxeliseMesh(self):
        """
        Voxelizes the input mesh and updates the background grid.

        Returns:
        -------
        np.ndarray
            The updated background grid with the voxelized mesh.
        """
        
        # Scale the mesh
        transform = vtk.vtkTransform()
        # Consider nonisotropic properties
        # dx = [self.scale[0]*self.spacing[0], self.scale[1]*self.spacing[1], self.scale[2]*self.spacing[2]]
        transform.Scale(1 / self.scale, 1 / self.scale, 1 / self.scale)
        
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.mesh)
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        scaledMesh = transformFilter.GetOutput()

        # Create an implicit function of the scaled mesh
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(scaledMesh)

        # Lower bound coordinates adjusted by scaling
        lowerBound = np.uint32([self.lower[0] / self.scale, self.lower[1] / self.scale, self.lower[2] / self.scale])
        self.background, points = pointWiseProcess(self.gx, self.gy, self.gz, self.scale, lowerBound, self.smoothedMatrix, self.label, self.background)
        for p in points:
            distance = distanceFilter.EvaluateFunction(p)
        
            # Update background grid with label if point is inside the mesh
            if distance < 0.0:
                self.background[p[2] + lowerBound[0], p[1] + lowerBound[1], p[0] + lowerBound[2]] = self.label

        return self.background

@nb.njit
def pointWiseProcess(gx, gy, gz, scale, lowerBound, smoothedMatrix, label, background):
    ApplyDistanceFilter = []
    # Voxelize the mesh by evaluating the implicit function at each grid point
    for k in range(int(gx / scale)):
        for j in range(int(gy / scale)):
            for i in range(int(gz / scale)):
                positionX = int((k + lowerBound[0]) * scale)
                positionY = int((j + lowerBound[1]) * scale)
                positionZ = int((i + lowerBound[2]) * scale)
                if smoothedMatrix[positionX, positionY, positionZ] == 1:
                    background[k + lowerBound[0], j + lowerBound[1], i + lowerBound[2]] = label
                elif smoothedMatrix[positionX, positionY, positionZ] == 0:
                    continue
                else:
                    ApplyDistanceFilter.append([i,j,k])

    return background, ApplyDistanceFilter
