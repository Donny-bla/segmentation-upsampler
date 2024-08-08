import vtk
import numpy as np

class IsosurfaceExtractor:
    """
    A class to extract isosurfaces from a 3D array using a specified threshold.

    Attributes:
    -----------
    array : numpy.ndarray
        The 3D array from which the isosurface is extracted.
    threshold : float
        The threshold value for isosurface extraction.
    faces : numpy.ndarray, optional
        Array representing the faces of the extracted isosurface.
    nodes : numpy.ndarray, optional
        Array representing the nodes of the extracted isosurface.
    polyData : vtk.vtkPolyData, optional
        The vtkPolyData object representing the isosurface.
    """

    def __init__(self, array, threshold):
        """
        Initialize the IsosurfaceExtractor.

        Parameters:
        ----------
        array : numpy.ndarray
            3D array from which the isosurface is extracted.
        threshold : float
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
        -------
        faces : numpy.ndarray
            Array representing the faces of the extracted isosurface.
        nodes : numpy.ndarray
            Array representing the nodes of the extracted isosurface.
        polyData : vtk.vtkPolyData
            The vtkPolyData object representing the isosurface.
        """
        # Convert the numpy array to a VTK image data
        data = vtk.vtkImageData()
        x, y, z = self.array.shape
        data.SetDimensions(z, y, x)
        data.SetSpacing(1, 1, 1)
        data.SetOrigin(0, 0, 0)

        vtkDataArray = vtk.vtkFloatArray()
        vtkDataArray.SetNumberOfComponents(1)
        vtkDataArray.SetArray(self.array.ravel(), len(self.array.ravel()), 1)

        data.GetPointData().SetScalars(vtkDataArray)

        # Extract the isosurface using the FlyingEdges3D algorithm
        surface = vtk.vtkFlyingEdges3D()
        surface.SetInputData(data)
        surface.SetValue(0, self.threshold)
        surface.Update()

        # Fill holes in the mesh
        fill = vtk.vtkFillHolesFilter()
        fill.SetInputConnection(surface.GetOutputPort())
        fill.SetHoleSize(5)
        fill.Update()
    
        # Remove any duplicate points
        cleanFilter = vtk.vtkCleanPolyData()
        cleanFilter.SetInputConnection(fill.GetOutputPort())
        cleanFilter.Update()

        # Get the cleaned isosurface
        polyData = cleanFilter.GetOutput()

        # Extract faces from the isosurface
        self.faces = []
        cells = polyData.GetPolys()
        cells.InitTraversal()
        idList = vtk.vtkIdList()
        while cells.GetNextCell(idList):
            self.faces.append([idList.GetId(0), idList.GetId(1), idList.GetId(2)])

        # Extract nodes from the isosurface
        self.nodes = []
        points = polyData.GetPoints()
        for i in range(points.GetNumberOfPoints()):
            self.nodes.append(points.GetPoint(i))

        self.polyData = polyData

        return np.array(self.faces), np.array(self.nodes), self.polyData
