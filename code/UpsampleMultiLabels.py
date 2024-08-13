import numpy as np
from code.RigorousPreprocess import MeshPreprocessor
from code.Extractor import IsosurfaceExtractor
from code.Voxelizer import MeshVoxelizer
from code.VoxelizerNumba import MeshVoxelizerNumba
from code.LabelSeparater import LabelSeparation
from code.FillGaps import FillGaps
"""
Perform upsampling for a labelled image

Parameters:
- multiLabelMatrix: 3D numpy array of floating numbers
- sigma: floating number >= 0
- targetVolume: floating number
- scale: list of 3 floating numbers
- spacing: list of 3 floating numbers
- iso: floating number from 0 to 1
- fillGaps: boolean
- NB: boolean

"""
def validateInputs(multiLabelMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB):

    if not (isinstance(multiLabelMatrix, np.ndarray) and multiLabelMatrix.ndim == 3 and multiLabelMatrix.dtype in [np.float32, np.float64]):
        raise ValueError("multiLabelMatrix should be a 3D numpy array of floating numbers")
    if not (isinstance(sigma, (float, int)) and sigma >= 0):
        raise ValueError("sigma should be a floating number >= 0")
    if not isinstance(targetVolume, (float, int)):
        raise ValueError("targetVolume should be a floating number")
    if not (len(scale) == 3 and all(isinstance(x, (float, int)) for x in scale)):
        raise ValueError("scale should be a list of 3 floating numbers")
    if not (len(spacing) == 3 and all(isinstance(x, (float, int)) for x in spacing)):
        raise ValueError("spacing should be a list of 3 floating numbers")
    if not (isinstance(iso, (float, int)) and 0 <= iso <= 1):
        raise ValueError("iso should be a floating number from 0 to 1")
    if not isinstance(fillGaps, bool):
        raise ValueError("fillGaps should be a boolean value")
    if not isinstance(NB, bool):
        raise ValueError("NB should be a boolean value")
    return True

def upsample(multiLabelMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB):
    validateInputs(multiLabelMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)

    # Initialize background matrix for voxelization
    gx, gy, gz = np.shape(multiLabelMatrix)
    dx = [scale[0] / spacing[0], scale[1] / spacing[1], scale[2] / spacing[2]]
    background = np.zeros((int(gx / dx[0]), int(gy / dx[1]), int(gz / dx[2])), dtype=np.uint8)
    smoothedList = []

    # Initialize LabelSeparation instance and separate labels
    labelSeparationInstance = LabelSeparation(multiLabelMatrix)
    labelSeparationInstance.separateLabels()
    separateMatrices, labelVolume, labels = labelSeparationInstance.getResults()

    # Loop through each label, preprocess, extract isosurface, and voxelize
    for i in range(len(separateMatrices)):
        singleLabelMatrix = separateMatrices[i]
        label = labels[i]

        # Preprocess the individual label matrix
        preprocessor = MeshPreprocessor(singleLabelMatrix, sigma, targetVolume)
        smoothedMatrix, isovalue, croppedMatrix, bounds = preprocessor.meshPreprocessing()
        smoothedList.append(smoothedMatrix)
        croppedMatrix = np.ascontiguousarray(croppedMatrix)

        if targetVolume:
            iso = isovalue

        # Extract isosurface
        isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso)
        faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

        x, y, z = np.shape(croppedMatrix)

        # Voxelize the isosurface
        if NB:
            voxelizer = MeshVoxelizerNumba(polyData, smoothedMatrix, x, y, z, scale, spacing, background, bounds, label)
        else:
            voxelizer = MeshVoxelizer(polyData, smoothedMatrix, x, y, z, scale, spacing, background, bounds, label)
        background = voxelizer.voxeliseMesh()

    # Resulting voxelized matrix
    newMatrix = background

    if fillGaps:
        GapFiller = FillGaps(newMatrix, smoothedList, dx, isovalue)
        newMatrix = GapFiller.fillZeros()

    return newMatrix

if __name__ == "__main__":
    
    newMatrix = upsample(multiLabelMatrix, sigma, targetVolume, scale, spacing, iso, fillGaps, NB)
    np.save('multilabelTestShape.npy', multiLabelMatrix)
