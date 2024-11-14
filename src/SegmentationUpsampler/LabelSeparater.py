import numpy as np

class LabelSeparation:
    """
LABELSEPARATION Separate labels in a matrix and analyze label volumes.

DESCRIPTION:
    LABELSEPARATION is a class designed to separate labels in a 
    multi-label matrix and calculate the volume (number of elements) 
    for each label. The separated labels are stored in a 4D array 
    where each slice along the first axis corresponds to a binary 
    matrix for a specific label.

USAGE:
    separator = LabelSeparation(multiLabelMatrix)
    separator.separateLabels()
    separatedMatrices, labelVolumes, labels = separator.getResults()

INPUTS:
    multiLabelMatrix : numpy.ndarray
        Matrix with integer labels.

OUTPUTS:
    separatedMatrices : numpy.ndarray
        4D array where each slice along the first axis contains a 
        binary matrix for each label.
    labelVolumes      : numpy.ndarray
        Array containing the volume (number of elements) for each label.
    labels            : numpy.ndarray
        Array of unique labels in the matrix.

ABOUT:
    author            : Liangpu Liu, Rui Xu, and Bradley Treeby.
    date              : 25th Aug 2024
    last update       : 25th Aug 2024

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

    def __init__(self, multiLabelMatrix):
        """
        INIT Initialize the LabelSeparation instance.

        DESCRIPTION:
            INIT initializes the LabelSeparation class with the 
            multi-label matrix. The matrix is analyzed to extract unique 
            labels and prepare the storage for the separated matrices 
            and their volumes.

        INPUTS:
            multiLabelMatrix : numpy.ndarray
                Matrix with integer labels.
        """
        self.multiLabelMatrix = multiLabelMatrix
        self.x, self.y, self.z = multiLabelMatrix.shape
        self.labels = np.unique(self.multiLabelMatrix)
        if self.labels[0] == 0:
            self.labels = self.labels[1:]
        self.separateMatrix = np.zeros((len(self.labels), self.x, self.y, 
                                        self.z), dtype=int)
        self.labelVolume = np.zeros(len(self.labels), dtype=int)

    def separateLabels(self):
        """
        SEPARATELABELS Separate labels in the matrix and calculate volumes.

        DESCRIPTION:
            SEPARATELABELS processes the multi-label matrix by separating 
            each label into a binary matrix. It also calculates the volume 
            for each label by summing the elements in the binary matrix. 
            The labels and corresponding matrices are then sorted by 
            volume in descending order.
        """
        for i, label in enumerate(self.labels):
            # Create a binary matrix where 1 corresponds to the current label
            self.separateMatrix[i] = (self.multiLabelMatrix == label).astype(float)

            # Calculate the sum of the binary matrix to get the label volume
            self.labelVolume[i] = np.sum(self.separateMatrix[i])

        # Sort labels by volume in descending order
        sortedLabels = np.argsort(self.labelVolume)[::-1]

        # Use the sorted indices to rearrange attributes
        self.separateMatrix = self.separateMatrix[sortedLabels]
        self.labelVolume = self.labelVolume[sortedLabels]
        self.labels = self.labels[sortedLabels]

    def getResults(self):
        """
        GETRESULTS Retrieve separated matrices, label volumes, and labels.

        DESCRIPTION:
            GETRESULTS returns the separated binary matrices, the label 
            volumes, and the unique labels in the matrix.

        OUTPUTS:
            separatedMatrices : numpy.ndarray
                4D array where each slice along the first axis contains a 
                binary matrix for each label.
            labelVolumes      : numpy.ndarray
                Array containing the volume (number of elements) for each label.
            labels            : numpy.ndarray
                Array of unique labels in the matrix.
        """
        return np.float32(self.separateMatrix), self.labelVolume, self.labels
