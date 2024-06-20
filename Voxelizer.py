import vtk
import numpy as np

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

    def __init__(self, mesh, smoothedMatrix, x, y, z, scale, spacing, background, bounds, label):
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
        self.spacing = spacing
        self.lower = bounds[0]
        self.background = background
        self.label = label
        self.smoothedMatrix = smoothedMatrix

    def voxeliseMesh(self):
        """
        Voxelizes the input mesh and updates the background grid.

        Returns:
        -------
        np.ndarray
            The updated background grid with the voxelized mesh.
        """

        # Create an implicit function of the scaled mesh
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(self.mesh)

        dx = [self.scale[0] * self.spacing[0], self.scale[1] * self.spacing[1], self.scale[2] * self.spacing[2]]
        # Voxelize the mesh by evaluating the implicit function at each grid point
        for k in np.arange(self.lower[0], self.gx + self.lower[0], dx[0]):
            for j in np.arange(self.lower[1], self.gy + self.lower[1], dx[1]):
                for i in np.arange(self.lower[2], self.gz + self.lower[2], dx[2]):

                    # A point is ignored if its corresponding point on the smoothed matrix is 1 or 0
                    if self.smoothedMatrix[int(k), int(j), int(i)] == 1:
                        self.background[round(k/dx[0]), round(j/dx[1]), round(i/dx[2])] = self.label
                    elif self.smoothedMatrix[int(k), int(j), int(i)] == 0:
                        continue 

                    else:
                        point = np.array([i - self.lower[2], j - self.lower[1], k - self.lower[0]], dtype=float)
                        distance = distanceFilter.EvaluateFunction(point)
    
                        # Update background grid with label if point is inside the mesh
                        if distance < 0.0:
                            self.background[round(k/dx[0]), round(j/dx[1]), round(i/dx[2])] = self.label
                        
        return self.background
