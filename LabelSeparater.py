import numpy as np

class LabelSeparation:
    """
    A class for separating labels in a matrix and analyzing label volumes.
    """

    def __init__(self, multiLabelMatrix):
        """
        Initialize the LabelSeparation instance.

        Parameters:
        - multiLabelMatrix (numpy.ndarray): Matrix with integer labels.
        """
        self.multiLabelMatrix = multiLabelMatrix
        self.x, self.y, self.z = multiLabelMatrix.shape
        self.labels = np.unique(self.multiLabelMatrix)
        if self.labels[0] == 0:
            self.labels = self.labels[1:]
        self.separateMatrix = np.zeros((len(self.labels), self.x, self.y, self.z), dtype=int)
        self.labelVolume = np.zeros(len(self.labels), dtype=int)

    def separateLabels(self):
        """
        Separate the labels in the matrix and calculate label volumes.
        """
        for i, label in enumerate(self.labels):
            # Create a binary matrix where 1 corresponds to the current label
            self.separateMatrix[i] = (self.multiLabelMatrix == label).astype(float)

            # Calculate the sum of the binary matrix to get the label volume
            self.labelVolume[i] = np.sum(self.separateMatrix[i])

        sortedLabels = np.argsort(self.labelVolume)[::-1]

        # Use the sorted indices to rearrange attributes
        self.separateMatrix = self.separateMatrix[sortedLabels]
        self.labelVolume = self.labelVolume[sortedLabels]
        self.labels = self.labels[sortedLabels]

    def getResults(self):
        """
        Get the separated matrices, label volumes, and labels.

        Returns:
        - tuple: A tuple containing the separated matrices, label volumes, and labels.
        """
        return np.float32(self.separateMatrix), self.labelVolume, self.labels
