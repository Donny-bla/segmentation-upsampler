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

    def __init__(self, mesh, x, y, z, scale, background, bounds, label):
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
        lowerBound = np.uint8(self.lower / self.scale)

        # Voxelize the mesh by evaluating the implicit function at each grid point
        for k in range(int(self.gx / self.scale)):
            for j in range(int(self.gy / self.scale)):
                for i in range(int(self.gz / self.scale)):
                    point = np.array([i, j, k], dtype=float)
                    distance = distanceFilter.EvaluateFunction(point)

                    # Update background grid with label if point is inside the mesh
                    if distance < 0.0:
                        self.background[k + lowerBound[0], j + lowerBound[1], i + lowerBound[2]] = self.label

        return self.background
