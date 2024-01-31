import numpy as np
from scipy.ndimage import gaussian_filter

class MeshPreprocessor:
    def __init__(self, originalMatrix, sigma, targetVolume):
        """
        Initialize the MeshPreprocessor.

        Parameters:
        - originalMatrix: numpy.ndarray
          3D array representing the original mesh.
        - sigma: float
          Standard deviation for the Gaussian filter.
        - targetVolume: float
          Target volume for binary search of isovalue.
        """
        self.originalMatrix = originalMatrix
        self.sigma = sigma
        self.targetVolume = targetVolume
        self.smoothMatrix = None
        self.isovalue = None

    def applyGaussianFilter(self, image):
        """
        Apply Gaussian filter to a 3D image.

        Parameters:
        - image: numpy.ndarray
          The 3D array representing the image.

        Returns:
        - numpy.ndarray
          The filtered 3D image.
        """
        if self.sigma == 0:
            return image
        filteredImage = gaussian_filter(image, sigma=self.sigma)
        return filteredImage

    def meshPreprocessing(self):
        """
        Perform preprocessing on a 3D mesh.

        Returns:
        - smoothMatrix: numpy.ndarray
          3D array representing the smoothed mesh.
        - isovalue: float
          Optimal isovalue for the smoothed mesh.
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
        if smoothedVolume<originalVolume: volumeDiff = 1
        v = -1/(np.log(np.abs(smoothedVolume - originalVolume) / originalVolume)) * volumeDiff

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
            if smoothedVolume<originalVolume: volumeDiff = 1
            v = -1/(np.log(np.abs(smoothedVolume - originalVolume) / originalVolume)) * volumeDiff

        return self.smoothMatrix, self.isovalue
