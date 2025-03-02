import numpy as np

class LabelSeparation:
    """
LABELSEPARATION Separate labels in SegmentedImage container and analyze volumes.

DESCRIPTION:
    LABELSEPARATION processes a SegmentedImage instance to isolate individual 
    labels, calculate their volumes, and store results in the parent container. 
    Operates as part of segmentation upsampling pipeline.

USAGE:
    # As part of segmentation processing pipeline:
    separator = LabelSeparation(segImg)
    separator.separateLabels()
    separator.updateImg()

ATTRIBUTES:
    segImg         : ImageBase.SegmentedImage
        Main container with original segmentation data
    labels         : numpy.ndarray
        Unique non-zero labels from input matrix
    separateMatrix : numpy.ndarray 
        4D array (label_count x X x Y x Z) of binary masks
    labelVolume    : numpy.ndarray
        Voxel counts for each label (sorted descending)

ABOUT:
    author         : Liangpu Liu, Rui Xu, Bradley Treeby
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

    def __init__(self, segImg):
        """
        INIT Prepare label separation for SegmentedImage instance.

        DESCRIPTION:
            Initializes label processing from SegmentedImage container.
            Identifies unique non-zero labels and preallocates storage.

        INPUTS:
            segImg      : ImageBase.SegmentedImage
                Container with multi-label matrix and spatial parameters
        """
        self.segImg = segImg
        
        self.labels = np.unique(self.segImg.multiLabelMatrix)
        if self.labels[0] == 0:
            self.labels = self.labels[1:]

        self.separateMatrix = np.zeros((len(self.labels), self.segImg.gx, self.segImg.gy, 
                                        self.segImg.gz), dtype=int)
        self.labelVolume = np.zeros(len(self.labels), dtype=int)

    def separateLabels(self):
        """
        SEPARATELABELS Isolate labels and calculate volumetric properties.

        DESCRIPTION:
            Processes multi-label matrix to:
            1. Create binary masks for each unique label
            2. Calculate voxel counts for each label
            3. Sort labels by descending volume
        """
        for i, label in enumerate(self.labels):
            # Create a binary matrix where 1 corresponds to the current label
            self.separateMatrix[i] = (self.segImg.multiLabelMatrix == label).astype(float)

            # Calculate the sum of the binary matrix to get the label volume
            self.labelVolume[i] = np.sum(self.separateMatrix[i])

        # Sort labels by volume in descending order
        sortedLabels = np.argsort(self.labelVolume)[::-1]

        # Use the sorted indices to rearrange attributes
        self.separateMatrix = self.separateMatrix[sortedLabels]
        self.labelVolume = self.labelVolume[sortedLabels]
        self.labels = self.labels[sortedLabels]

    def updateImg(self):
        """
        UPDATEIMG Store results in SegmentedImage container.

        DESCRIPTION:
            Transfers processed label data back to parent SegmentedImage
            instance for subsequent pipeline steps.
        """
        self.segImg.setSeparateLabels(self.separateMatrix, 
                                    self.labelVolume, 
                                    self.labels)
        #return np.float32(self.separateMatrix), self.labelVolume, self.labels
