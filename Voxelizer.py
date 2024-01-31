import vtk
import numpy as np

class MeshVoxelizer:
    def __init__(self, mesh, gx, gy, gz, scale):
        """
        Initialize the MeshVoxelizer.

        Parameters:
        - mesh: vtk.vtkPolyData
          The input mesh to be voxelized.
        - gx: float
          The number of grid points along the X-axis.
        - gy: float
          The number of grid points along the Y-axis.
        - gz: float
          The number of grid points along the Z-axis.
        - scale: float
          The scale factor to adjust the size of the grid.
        """
        self.mesh = mesh
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.scale = scale
        self.voxelValues = None

    def voxeliseMesh(self):
        """
        Voxelizes the input mesh and stores the result in voxelValues.

        Returns:
        - voxelValues: numpy.ndarray
          A binary representation of the mesh on the grid.
        """
        # Create a grid
        grid = vtk.vtkImageData()
        grid.SetDimensions(int(self.gx), int(self.gy), int(self.gz))
        grid.SetSpacing(self.scale, self.scale, self.scale)

        # Scale the mesh to fit within the grid
        transform = vtk.vtkTransform()
        transform.Scale(1 / self.scale, 1 / self.scale, 1 / self.scale)

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.mesh)
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        scaledMesh = transformFilter.GetOutput()

        # Set the origin of the grid
        grid.SetOrigin(0, 0, 0)

        # Create vtkImplicitPolyDataDistance
        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(scaledMesh)

        # Create a NumPy array to store voxel values
        self.voxelValues = np.zeros((int(self.gx / self.scale), int(self.gy / self.scale),
                                     int(self.gz / self.scale)), dtype=np.uint8)

        # Iterate over all grid points and determine if they are inside the mesh
        for i in range(int(self.gx / self.scale)):
            for j in range(int(self.gy / self.scale)):
                for k in range(int(self.gz / self.scale)):
                    point = np.array([i, j, k], dtype=float)
                    distance = distanceFilter.EvaluateFunction(point)

                    # If the distance is negative, the point is inside the mesh
                    if distance < 0.0:
                        self.voxelValues[i, j, k] = 1

        return self.voxelValues
