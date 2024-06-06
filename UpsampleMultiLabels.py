# Import necessary classes and functions
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
from LabelSeparater import LabelSeparation
from scipy.ndimage import gaussian_filter
import numpy as np

# Initialize background matrix for voxelization
gx, gy, gz = np.shape(multiLabelMatrix)
background = np.zeros((int(gx / scale), int(gy / scale), int(gz / scale)), dtype=np.uint8)

# Initialize LabelSeparation instance and separate labels
labelSeparationInstance = LabelSeparation(multiLabelMatrix)
labelSeparationInstance.separateLabels()
separateMatrices, labelVolume, labels = labelSeparationInstance.getResults()
print(len(separateMatrices))
# Loop through each label, preprocess, extract isosurface, and voxelize
for i in range(len(separateMatrices)):
    singleLabelMatrix = separateMatrices[i]
    label = labels[i]

    # Preprocess the individual label matrix
    preprocessor = MeshPreprocessor(singleLabelMatrix, sigma, targetVolume)
    smoothedMatrix, isovalue, croppedMatrix, bounds = preprocessor.meshPreprocessing()
    croppedMatrix = np.ascontiguousarray(croppedMatrix)
    
    if targetVolume:
        iso = isovalue
    print("isovalue for label",i, "is:", iso)

    # Extract isosurface
    isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso)
    faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

    # Voxelize the isosurface
    x, y, z = np.shape(croppedMatrix)
    voxelizer = MeshVoxelizer(polyData, x, y, z, scale, background, bounds, label)
    background = voxelizer.voxeliseMesh()

    
# Resulting voxelized matrix
newMatrix = background
