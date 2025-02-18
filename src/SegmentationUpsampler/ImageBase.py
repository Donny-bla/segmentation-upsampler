import vtk
import numpy as np

class BinaryImage:
    def __init__(self, binImg, label):
        #self.segImg = segImg
        self.binImg = binImg
        self.label = label

        self.iso = None
        self.sigma = None
        self.smoothedImg = None
        self.croppedImg = None
        self.bounds = None

        self.polyData = None
        self.faces = None
        self.nodes = None
    
    def setPreprocessedImg(self, smoothMatrix, croppedMatrix, nonZeroShape):
        self.smoothedImg = smoothMatrix
        self.croppedImg = croppedMatrix
        self.bounds = nonZeroShape
    
    def setIsovalue(self, iso):
        self.iso = iso
        print("label:", self.label, "mesh extracted with iso: ", self.iso)

    def setSigma(self, sigma):
        self.sigma = sigma
        print("label: ", self.label, "smoothed with sigma: ", self.sigma)

    def setSurfaceMesh(self, polyData, faces, nodes):
        self.polyData = polyData
        self.faces = faces
        self.nodes = nodes

class SegmentedImage:
    """

ABOUT:
    author         : Liangpu Liu, Rui Xu, and Bradley Treeby.
    date           : 26th Jan 2025
    last update    :  2nd Feb 2025

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

    def __init__(self, multiLabelMatrix, sigma, scale, spacing, iso, targetVolume):
        """

        """
        self.multiLabelMatrix = multiLabelMatrix
        self.sigma = sigma
        self.iso = iso
        self.targetVolume = targetVolume
        
        self.gx, self.gy, self.gz = np.shape(multiLabelMatrix)
        self.dx = [scale[0] / spacing[0], scale[1] / spacing[1], 
            scale[2] / spacing[2]]
        self.newImg = np.zeros((int(self.gx / self.dx[0]), int(self.gy / self.dx[1]), 
                            int(self.gz / self.dx[2])), dtype=np.uint8)
        self.smoothedList = []

    def generateBinaryImgList(self):
        self.binaryImgList = []
        for i in range(self.getLabelNumber()):
            img, label = self.getLabel(i)
            binImg = BinaryImage(img, label)
            self.binaryImgList.append(binImg)
    
    def setSeparateLabels(self, separateMatrix, labelVolume, labels):
        self.separateMatrix = np.float32(separateMatrix)
        self.labelVolume = labelVolume
        self.labels = labels
        self.generateBinaryImgList()

    def setUpdatedImg(self, newImg):
        self.newImg = newImg

    def getAllLabels(self):
        return self.separateMatrix, self.labelVolume, self.labels
    
    def getLabelNumber(self):
        return len(self.separateMatrix)
    
    def getLabel(self, i):
        return self.separateMatrix[i], self.labels[i]
    
    