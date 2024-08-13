import numpy as np
from scipy.ndimage import gaussian_filter

class MeshPreprocessor:
    """
    A class for preprocessing a 3D mesh using Gaussian filtering and binary search for isovalue.

    Attributes:
    ----------
    originalMatrix : numpy.ndarray
        3D array representing the original mesh.
    sigma : float
        Standard deviation for the Gaussian filter.
    targetVolume : float
        Target volume for binary search of isovalue.
    smoothMatrix : numpy.ndarray
        3D array representing the smoothed mesh.
    isovalue : float
        Optimal isovalue for the smoothed mesh.
    nonZeroShape : tuple
        Bounds of the cropped matrix after removing zero labels.
    croppedMatrix : numpy.ndarray
        3D array representing the cropped matrix after removing zero labels.
    """

    def __init__(self, originalMatrix, sigma, targetVolume):
        """
        Initialize the MeshPreprocessor.

        Parameters:
        ----------
        originalMatrix : numpy.ndarray
            3D array representing the original mesh.
        sigma : float
            Standard deviation for the Gaussian filter.
        targetVolume : float
            Target volume for binary search of isovalue.
        """
        self.originalMatrix = originalMatrix
        self.sigma = sigma
        self.targetVolume = targetVolume
        self.smoothMatrix = None
        self.isovalue = None
        self.nonZeroShape = None
        self.croppedMatrix = None

    def applyGaussianFilter(self, image):
        """
        Apply Gaussian filter to a 3D image.

        Parameters:
        ----------
        image : numpy.ndarray
            The 3D array representing the image.

        Returns:
        -------
        numpy.ndarray
            The filtered 3D image.
        """
        if self.sigma == 0:
            return image
        filteredImage = gaussian_filter(image, sigma=self.sigma)
        return filteredImage

    def cropLabels(self):
        """
        Crop zero labels to speed up the following process.

        Returns:
        -------
        numpy.ndarray
            Cropped matrix after removing zero labels.
        tuple
            Bounds of the cropped matrix.
        """
        nonZeroLabels = np.nonzero(self.smoothMatrix)
        lowerBound = np.min(nonZeroLabels, axis=1)
        upperBound = np.max(nonZeroLabels, axis=1) + 1
        croppedMatrix = self.smoothMatrix[lowerBound[0]:upperBound[0], 
                                           lowerBound[1]:upperBound[1], 
                                           lowerBound[2]:upperBound[2]]
        nonZeroShape = (lowerBound, upperBound)
        return croppedMatrix, nonZeroShape

    def meshPreprocessing(self):
        """
        Perform preprocessing on a 3D mesh.

        Returns:
        -------
        numpy.ndarray
            3D array representing the smoothed mesh.
        float
            Optimal isovalue for the smoothed mesh.
        numpy.ndarray
            3D array representing the cropped matrix after removing zero labels.
        tuple
            Bounds of the cropped matrix.
        """
        # Gaussian smoothing
        self.smoothMatrix = self.applyGaussianFilter(self.originalMatrix)

        # Compute original and smoothed volumes
        originalVolume = np.sum(self.originalMatrix == 1)

        # Binary search for isovalue
        upper = np.max(self.smoothMatrix)
        lower = np.min(self.smoothMatrix)
        self.isovalue = (upper + lower) / 2
        smoothedVolume = np.sum(self.smoothMatrix > self.isovalue)  # Initialize isovalue at 0.5

        volumeDiff = -1
        if smoothedVolume < originalVolume: 
            volumeDiff = 1
        v = volumeDiff / (np.log(np.abs(smoothedVolume - originalVolume) / originalVolume))

        ii = 0
        while ((v >= (self.targetVolume + 0.005) or v <= (self.targetVolume - 0.005)) and ii < 1000):
            ii += 1
            if v < self.targetVolume:
                lower = self.isovalue
            else:
                upper = self.isovalue
            self.isovalue = (upper + lower) / 2
            smoothedVolume = np.sum(self.smoothMatrix > self.isovalue)

            volumeDiff = -1
            if smoothedVolume < originalVolume: 
                volumeDiff = 1
            v = -1 / (np.log(np.abs(smoothedVolume - originalVolume) / originalVolume)) * volumeDiff

        self.croppedMatrix, self.nonZeroShape = self.cropLabels()

        return self.smoothMatrix, self.isovalue, self.croppedMatrix, self.nonZeroShape
