import vtk
import numpy as np

class MeshVoxelizer:
    def __init__(self, mesh, x, y, z, scale, background, bounds, label):
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
        self.gx = x
        self.gy = y
        self.gz = z
        self.scale = scale
        self.lower = np.array(bounds[0])
        self.background = background
        self.label = label
        self.voxelValues = None

    def voxeliseMesh(self):

        transform = vtk.vtkTransform()
        transform.Scale(1 / self.scale, 1 / self.scale, 1 / self.scale)
        
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.mesh)
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        scaledMesh = transformFilter.GetOutput()

        distanceFilter = vtk.vtkImplicitPolyDataDistance()
        distanceFilter.SetInput(scaledMesh)

        # self.voxelValues = np.zeros((int(self.gx / self.scale), int(self.gy / self.scale),
        #                              int(self.gz / self.scale)), dtype=np.uint8)
        
        lowerBound = np.uint8(self.lower/self.scale)
        for k in range(int(self.gx / self.scale)):
            for j in range(int(self.gy / self.scale)):
                for i in range(int(self.gz / self.scale)):
                    point = np.array([i, j, k], dtype=float)
                    distance = distanceFilter.EvaluateFunction(point)

                    if distance < 0.0:
                        # Swapped x-axis and z-axis in the output
                        self.background[k + lowerBound[0], j + lowerBound[1], i + lowerBound[2]] = self.label
                        #self.voxelValues[k, j, i] = self.label
                        
        return self.background
