import vtk
import numpy as np

class BinaryImage:
    """
BINARYIMAGE Container for label-specific segmentation processing data.

DESCRIPTION:
    Stores intermediate data and parameters for individual labels during
    segmentation processing pipeline. Maintains:
    - Smoothed/cropped image data
    - Mesh extraction parameters
    - Surface geometry representations

ATTRIBUTES:
    binImg       : numpy.ndarray 
        Original binary mask for label
    label        : int
        Label identifier value
    iso          : float
        Isovalue used for mesh extraction
    sigma        : float
        Gaussian smoothing parameter
    smoothedImg  : numpy.ndarray
        Smoothed binary mask
    croppedImg   : numpy.ndarray
        Region-of-interest cropped image
    bounds       : tuple
        (min, max) bounds of non-zero region
    polyData     : vtk.vtkPolyData
        Extracted surface mesh
    faces        : numpy.ndarray
        Mesh face connectivity (Nx3)
    nodes        : numpy.ndarray 
        Mesh vertex coordinates (Mx3)
    """

    def __init__(self, binImg, label):
        """
        INIT Initialize label processing container.

        INPUTS:
            binImg      : numpy.ndarray
                Binary mask for target label
            label       : int
                Label identifier value
        """
        self.binImg = binImg
        self.label = label

        # Processing parameters
        self.iso = None
        self.sigma = None
        
        # Image data containers
        self.smoothedImg = None
        self.croppedImg = None
        self.bounds = None
        
        # Geometry data
        self.polyData = None
        self.faces = None
        self.nodes = None
    
    def setPreprocessedImg(self, smoothMatrix, croppedMatrix, nonZeroShape):
        """
        STOREPREPROCESSED Store smoothed and cropped image data.

        INPUTS:
            smoothMatrix   : numpy.ndarray
                Gaussian-smoothed binary mask
            croppedMatrix  : numpy.ndarray
                ROI-cropped image data
            nonZeroShape   : tuple
                Bounding box of non-zero region (xmin, xmax, ymin, ymax, zmin, zmax)
        """
        self.smoothedImg = smoothMatrix
        self.croppedImg = croppedMatrix
        self.bounds = nonZeroShape
    
    def setIsovalue(self, iso):
        """
        SETISOVALUE Configure mesh extraction threshold.

        INPUTS:
            iso       : float
                Isovalue for surface extraction
        """
        self.iso = iso
        print(f"Label {self.label}: Mesh extracted with iso={self.iso:.3f}")

    def setSigma(self, sigma):
        """
        SETSIGMA Record smoothing parameter.

        INPUTS:
            sigma     : float
                Gaussian kernel standard deviation
        """
        self.sigma = sigma
        print(f"Label {self.label}: Smoothed with σ={sigma:.2f}")

    def setSurfaceMesh(self, polyData, faces, nodes):
        """
        SETSURFACEMESH Store extracted surface geometry.

        INPUTS:
            polyData  : vtk.vtkPolyData
                Surface mesh structure
            faces     : numpy.ndarray
                Triangular face connectivity
            nodes     : numpy.ndarray
                Mesh vertex coordinates
        """
        self.polyData = polyData
        self.faces = faces
        self.nodes = nodes


class SegmentedImage:
    """
SEGMENTEDIMAGE Main container for multi-label segmentation processing.

DESCRIPTION:
    Central data structure for segmentation upsampling pipeline. Manages:
    - Original multi-label volume
    - Processing parameters (scaling, spacing, smoothing)
    - Label-specific binary image containers
    - Output upsampled volume

ATTRIBUTES:
    multiLabelMatrix : numpy.ndarray
        Original 3D segmented image (HxWxD)
    sigma           : float
        Global Gaussian smoothing parameter
    iso             : float
        Default isovalue for mesh extraction
    gx, gy, gz     : int
        Original grid dimensions
    dx              : (float, float, float)
        Scaling factors (output/original) per axis
    newImg          : numpy.ndarray
        Upsampled output volume (XxYxZ)
    binaryImgList   : list[BinaryImage]
        Per-label processing containers
    separateMatrix  : numpy.ndarray
        Separated 4D label array (LxHxWxD)
    labelVolume     : numpy.ndarray
        Voxel counts per label (L,)
    labels          : numpy.ndarray
        Unique label identifiers (L,)

ABOUT:
    author         : Liangpu Liu, Rui Xu, Bradley Treeby
    date           : 26th Jan 2025
    last update    :  1st Mar 2025

LICENSE:
    This file is part of the pySegmentationUpsampler.
    Copyright (C) 2024  Liangpu Liu, Rui Xu, and Bradley Treeby.
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

    def __init__(self, multiLabelMatrix, sigma, scale, spacing, iso):
        """
        INIT Initialize segmentation processing container.

        INPUTS:
            multiLabelMatrix : numpy.ndarray
                3D array of integer labels
            sigma           : float
                Gaussian smoothing parameter
            scale          : (float, float, float)
                Output scaling factors (sx, sy, sz)
            spacing         : (float, float, float)
                Original voxel spacing (dx, dy, dz)
            iso             : float
                Default isovalue for surface extraction
        """
        self.multiLabelMatrix = multiLabelMatrix
        self.sigma = sigma
        self.iso = iso
        
        # Original grid dimensions
        self.gx, self.gy, self.gz = np.shape(multiLabelMatrix)
        
        # Calculate scaling factors
        self.dx = [scale[0]/spacing[0],
                   scale[1]/spacing[1],
                   scale[2]/spacing[2]]
        
        # Initialize output grid
        self.newImg = np.zeros(
            (int(self.gx/self.dx[0]),
             int(self.gy/self.dx[1]),
             int(self.gz/self.dx[2])),
            dtype=np.uint8
        )
        
        self.smoothedList = []  # Legacy attribute for compatibility

    def generateBinaryImgList(self):
        """Create BinaryImage instances for each separated label."""
        self.binaryImgList = []
        for i in range(self.getLabelNumber()):
            img, label = self.getLabel(i)
            self.binaryImgList.append(BinaryImage(img, label))

    def setSeparateLabels(self, separateMatrix, labelVolume, labels):
        """
        STORESEPARATEDLABELS Register label separation results.

        INPUTS:
            separateMatrix : numpy.ndarray
                4D array of separated labels (LxHxWxD)
            labelVolume    : numpy.ndarray
                Voxel counts per label (L,)
            labels         : numpy.ndarray
                Unique label identifiers (L,)
        """
        self.separateMatrix = np.float32(separateMatrix)
        self.labelVolume = labelVolume
        self.labels = labels
        self.generateBinaryImgList()

    def setUpdatedImg(self, newImg):
        """
        UPDATEOUTPUTGRID Register modified upsampled volume.

        INPUTS:
            newImg      : numpy.ndarray
                Updated segmentation grid
        """
        self.newImg = newImg

    def getAllLabels(self):
        """
        GETLABELDATA Retrieve separated label information.

        RETURNS:
            tuple: (separateMatrix, labelVolume, labels)
        """
        return self.separateMatrix, self.labelVolume, self.labels
    
    def getLabelNumber(self):
        """GETLABELCOUNT Return number of unique labels."""
        return len(self.separateMatrix)
    
    def getLabel(self, i):
        """
        GETLABELBYINDEX Retrieve specific label data.

        INPUTS:
            i           : int
                Label index in separateMatrix

        RETURNS:
            tuple: (binary_mask, label_value)
        """
        return self.separateMatrix[i], self.labels[i]