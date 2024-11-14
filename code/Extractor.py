import vtk
import numpy as np

class IsosurfaceExtractor:
    """
ISOSURFACEEXTRACTOR Extract isosurfaces from a 3D array.

DESCRIPTION:
    ISOSURFACEEXTRACTOR is a class designed to extract isosurfaces 
    from a 3D array using a specified threshold. The extracted 
    isosurface is represented as faces, nodes, and a vtkPolyData 
    object.

USAGE:
    extractor = IsosurfaceExtractor(array, threshold)
    faces, nodes, polyData = extractor.extractIsosurface()

INPUTS:
    array          : numpy.ndarray
        The 3D array from which the isosurface is extracted.
    threshold      : float
        The threshold value for isosurface extraction.

OUTPUTS:
    faces          : numpy.ndarray
        Array representing the faces of the extracted isosurface.
    nodes          : numpy.ndarray
        Array representing the nodes of the extracted isosurface.
    polyData       : vtk.vtkPolyData
        The vtkPolyData object representing the isosurface.

ABOUT:
    author         : Liangpu Liu, Rui Xu, and Bradley Treeby.
    date           : 25th Aug 2024
    last update    : 25th Aug 2024

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

    def __init__(self, array, threshold):
        """
        INIT Initialize the IsosurfaceExtractor.

        DESCRIPTION:
            INIT initializes the IsosurfaceExtractor class with the 3D 
            array and threshold value for isosurface extraction.

        INPUTS:
            array      : numpy.ndarray
                3D array from which the isosurface is extracted.
            threshold  : float
                Threshold value for isosurface extraction.
        """
        self.array = array
        self.threshold = threshold
        self.faces = None
        self.nodes = None
        self.polyData = None

    def extractIsosurface(self):
        """
        EXTRACTISOSURFACE Extract the isosurface from the 3D array.

        DESCRIPTION:
            EXTRACTISOSURFACE extracts the isosurface from the 3D array 
            using the specified threshold. The method converts the 3D 
            array to a vtkImageData object, applies the FlyingEdges3D 
            algorithm, fills holes, removes duplicate points, and 
            retrieves the resulting faces, nodes, and vtkPolyData object.

        OUTPUTS:
            faces      : numpy.ndarray
                Array representing the faces of the extracted isosurface.
            nodes      : numpy.ndarray
                Array representing the nodes of the extracted isosurface.
            polyData   : vtk.vtkPolyData
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
            self.faces.append([idList.GetId(0), idList.GetId(1), 
                               idList.GetId(2)])

        # Extract nodes from the isosurface
        self.nodes = []
        points = polyData.GetPoints()
        for i in range(points.GetNumberOfPoints()):
            self.nodes.append(points.GetPoint(i))

        self.polyData = polyData

        return np.array(self.faces), np.array(self.nodes), self.polyData
