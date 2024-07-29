# Import necessary classes and functions
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
from VoxelizerNumba import MeshVoxelizerNumba
from LabelSeparater import LabelSeparation
from FillGaps import FillGaps
from scipy.ndimage import gaussian_filter
import numpy as np

# Initialize background matrix for voxelization
gx, gy, gz = np.shape(multiLabelMatrix)
dx = [scale[0] / spacing[0], scale[1] / spacing[1], scale[2] / spacing[2]]
background = np.zeros((int(gx / dx[0]), int(gy / dx[1]), int(gz / dx[2])), dtype=np.uint8)
smoothedList = []

# Initialize LabelSeparation instance and separate labels
labelSeparationInstance = LabelSeparation(multiLabelMatrix)
labelSeparationInstance.separateLabels()
separateMatrices, labelVolume, labels = labelSeparationInstance.getResults()
#print(len(separateMatrices))

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
    #print("isovalue for label",i, "is:", iso)

    # Extract isosurface
    isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso)
    faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

    x, y, z = np.shape(croppedMatrix)
    #print(bounds, x, y, z)

    # Voxelize the isosurface
    if NB:
        voxelizer = MeshVoxelizerNumba(polyData, smoothedMatrix, x, y, z, scale, spacing, background, bounds, label)
        background = voxelizer.voxeliseMesh()

    else:
        voxelizer = MeshVoxelizer(polyData, smoothedMatrix, x, y, z, scale, spacing, background, bounds, label)
        background = voxelizer.voxeliseMesh()

# Resulting voxelized matrix
newMatrix = background

if fillGaps:
    GapFiller = FillGaps(newMatrix, smoothedList, dx, isovalue)
    newMatrix = GapFiller.fillZeros()
