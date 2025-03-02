import vtk
import numpy as np

class IsosurfaceExtractor:
    """
ISOSURFACEEXTRACTOR Extract isosurfaces from segmented image data.

DESCRIPTION:
    ISOSURFACEEXTRACTOR is a class designed to extract isosurfaces 
    from a segmented image component using VTK's mesh processing 
    pipeline. Handles label-specific surface extraction including 
    hole filling and mesh cleaning.

USAGE:
    # As part of segmentation upsampling pipeline:
    extractor = IsosurfaceExtractor(segImg, label_index)
    extractor.extractIsosurface()

INPUTS:
    segImg       : ImageBase.SegmentedImage
        Container class with processed segmentation data
    i           : int
        Index of the label to process in segImg.binaryImgList

ATTRIBUTES:
    binaryImg    : ImageBase.BinaryImage
        Label-specific image data
    array        : numpy.ndarray
        3D array slice for the specified label
    threshold    : float
        Calculated isovalue for surface extraction
    faces        : numpy.ndarray
        Triangular faces from extracted mesh (Nx3)
    nodes        : numpy.ndarray
        Mesh vertices in physical coordinates (Mx3)
    polyData     : vtk.vtkPolyData
        Processed surface mesh with topology

ABOUT:
    author         : Liangpu Liu, Rui Xu, and Bradley Treeby.
    date           : 25th Aug 2024
    last update    :  1st Mar 2025

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

    def __init__(self, segImg, i):
        """
        INIT Initialize label-specific surface extractor.

        DESCRIPTION:
            Configures extraction parameters from SegmentedImage 
            container and specified label index.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Main container with preprocessed segmentation data
            i           : int  
                Index of label to process in binaryImgList
        """
        self.binaryImg = segImg.binaryImgList[i]
        self.array = self.binaryImg.croppedImg
        self.threshold = self.binaryImg.iso

        self.faces = None
        self.nodes = None
        self.polyData = None

    def extractIsosurface(self):
        """
        INIT Initialize label-specific surface extractor.

        DESCRIPTION:
            Configures extraction parameters from SegmentedImage 
            container and specified label index.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Main container with preprocessed segmentation data
            i           : int  
                Index of label to process in binaryImgList
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

    def updateImg(self):
        """Update parent image with extracted surface data."""
        self.binaryImg.setSurfaceMesh(self.polyData, 
                                    np.array(self.faces), 
                                    np.array(self.nodes))