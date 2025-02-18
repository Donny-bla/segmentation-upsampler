import numpy as np
from scipy.signal import convolve
from scipy.ndimage import gaussian_filter
from SegmentationUpsampler import ImageBase

class ImagePreprocess:

    def __init__(self, segImg, i, isotropoic = True):

        self.binaryImg = segImg.binaryImgList[i]
        self.segImg = segImg
        self.array = np.int32(self.binaryImg.binImg)
        self.originalImg = self.binaryImg.binImg
        
        self.sigma = 0
        self.sigmaAnI = 0
        self.isotropic = isotropoic
        self.iso = 0

        self.smoothMatrix = None
        self.nonZeroShape = None
        self.croppedMatrix = None

    def getVolume(self):
        return np.sum(np.concatenate(self.array))
    
    def getSurfaceArea(self):
        surfaceAreaKernel = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                    [[0,-1,0],[-1,6,-1],[0,-1,0]],
                                    [[0,0,0],[0,-1,0],[0,0,0]]])
        surface = convolve(self.array, surfaceAreaKernel, mode="same")
        surfaceArea = np.sum(np.abs(np.concatenate(surface)))/2
        return surfaceArea
    
    def getAxialSurfaceArea(self):
        surfaceAreaKernel_X = np.array([[[0,0,0],[0,0,0],[0,0,0]],
                                            [[0,-1,0],[-1,4,-1],[0,-1,0]],
                                            [[0,0,0],[0,0,0],[0,0,0]]])
        surfaceAreaKernel_Y = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                            [[0,0,0],[-1,4,-1],[0,0,0]],
                                            [[0,0,0],[0,-1,0],[0,0,0]]])
        surfaceAreaKernel_Z = np.array([[[0,0,0],[0,-1,0],[0,0,0]],
                                            [[0,-1,0],[0,4,0],[0,-1,0]],
                                            [[0,0,0],[0,-1,0],[0,0,0]]])
        surface_X = convolve(self.array, surfaceAreaKernel_X, mode="same")
        surface_Y = convolve(self.array, surfaceAreaKernel_Y, mode="same")
        surface_Z = convolve(self.array, surfaceAreaKernel_Z, mode="same")
        
        Ax = np.sum(np.abs(np.concatenate(surface_X)))/2
        Ay = np.sum(np.abs(np.concatenate(surface_Y)))/2
        Az = np.sum(np.abs(np.concatenate(surface_Z)))/2

        return Ax, Ay, Az
    
    def grossParameterAV(self):
        A = self.getSurfaceArea()
        V = self.getVolume()

        return (A**(1/2))/(V**(1/3))
    
    def axialParameter(self):
        Ax, Ay, Az = self.getAxialSurfaceArea()
        A = self.getSurfaceArea()
        return Ax/A, Ay/A, Az/A
    
    def computeSigma(self):
        AV = self.grossParameterAV()
        if AV<2.6:
            self.sigma = 0.4
        elif 2.6<=AV<2.9:
            self.sigma = 0.4 + (AV-2.6)/((2.9-2.6)/(0.5-0.4))
        elif 2.9<=AV<4.5:
            self.sigma = 0.5 + (AV-2.9)/((4.5-2.9)/(0.75-0.5))
        elif 4.5<=AV<5:
            self.sigma = 0.75 + (AV-4.5)/((5-4.5)/(1-0.75))
        elif AV>=5:
            self.sigma = 1

    def computeAnIsotropicSigma(self):
        Ax, Ay, Az = self.axialParameter()
        M = max(Ax, Ay, Az)
        self.computeSigma()
        self.sigmaAnI = [self.sigma*Ax/M, self.sigma*Ay/M, self.sigma*Az/M]
        
    def computeIso(self):
        originalAV = self.grossParameterAV()
        
        isovalue = 0
        minDiff = 9999        
        stepsize = 0.001

        while isovalue < 0.6:
            isovalue = isovalue + stepsize
            self.array = np.int32(self.croppedMatrix >= isovalue)
            thisAV = self.grossParameterAV()
            diff = abs(thisAV - originalAV)

            if diff < minDiff:
                minDiff = diff
                self.iso = isovalue
                #print(minDiff, self.iso)

    def setSigma(self):
        if self.segImg.sigma == -1:
            if self.isotropic:
                self.computeSigma()
                self.binaryImg.setSigma(self.sigma)
            else:
                self.computeAnIsotropicSigma()
                self.binaryImg.setSigma(self.sigmaAnI)
        else:
            self.binaryImg.setSigma(self.segImg.sigma)

    def setIsovalue(self):
        if self.segImg.iso == -1:
            self.computeIso()
            self.binaryImg.setIsovalue(self.iso)
        else:
            self.binaryImg.setIsovalue(self.segImg.iso)

    def applyGaussianFilter(self, image):
        filteredImage = gaussian_filter(image, sigma=self.binaryImg.sigma)
        return filteredImage
    
    def cropLabels(self, image):
        nonZeroLabels = np.nonzero(image)
        lowerBound = np.min(nonZeroLabels, axis=1)
        upperBound = np.max(nonZeroLabels, axis=1) + 1
        croppedMatrix = self.smoothMatrix[lowerBound[0]:upperBound[0], 
                                          lowerBound[1]:upperBound[1], 
                                          lowerBound[2]:upperBound[2]]
        nonZeroShape = (lowerBound, upperBound)
        return croppedMatrix, nonZeroShape

    def meshPreprocessing(self):
        self.setSigma()
        self.smoothMatrix = self.applyGaussianFilter(self.originalImg)

        self.croppedMatrix, self.nonZeroShape = self.cropLabels(self.smoothMatrix)
        self.croppedMatrix =  np.ascontiguousarray(self.croppedMatrix)

        self.setIsovalue()

    def updateImg(self):
        self.binaryImg.setPreprocessedImg(self.smoothMatrix, self.croppedMatrix, self.nonZeroShape)
