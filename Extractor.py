import vtk
import numpy as np

class IsosurfaceExtractor:
    def __init__(self, array, threshold):
        """
        Initialize the IsosurfaceExtractor.

        Parameters:
        - array: numpy.ndarray
          3D array from which the isosurface is extracted.
        - threshold: float
          Threshold value for isosurface extraction.
        """
        self.array = array
        self.threshold = threshold
        self.faces = None
        self.nodes = None
        self.polyData = None

    def extractIsosurface(self):
        """
        Extracts the isosurface from the 3D array and saves the results.

        Returns:
        - faces: numpy.ndarray
          Array representing the faces of the extracted isosurface.
        - nodes: numpy.ndarray
          Array representing the nodes of the extracted isosurface.
        - polyData: vtk.vtkPolyData
          The vtkPolyData object representing the isosurface.
        """
        data = vtk.vtkImageData()
        data.SetDimensions(self.array.shape)
        data.SetSpacing(1, 1, 1)
        data.SetOrigin(0, 0, 0)

        vtkDataArray = vtk.vtkFloatArray()
        vtkDataArray.SetNumberOfComponents(1)
        vtkDataArray.SetArray(self.array.ravel(), len(self.array.ravel()), 1)

        data.GetPointData().SetScalars(vtkDataArray)

        # Extract isosurface
        surface = vtk.vtkFlyingEdges3D()
        surface.SetInputData(data)
        surface.SetValue(0, self.threshold)
        surface.Update()

        # Get faces and nodes of the isosurface
        polyData = surface.GetOutput()

        # Extract faces
        self.faces = []
        cells = polyData.GetPolys()
        cells.InitTraversal()
        idList = vtk.vtkIdList()
        while cells.GetNextCell(idList):
            self.faces.append([idList.GetId(0), idList.GetId(1), idList.GetId(2)])

        # Extract nodes
        self.nodes = []
        points = polyData.GetPoints()
        for i in range(points.GetNumberOfPoints()):
            self.nodes.append(points.GetPoint(i))

        self.polyData = polyData

        return np.array(self.faces), np.array(self.nodes), self.polyData


