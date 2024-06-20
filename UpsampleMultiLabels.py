# Import necessary classes and functions
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
from VoxelizerNumba import MeshVoxelizerNumba
from LabelSeparater import LabelSeparation
from scipy.ndimage import gaussian_filter
import numpy as np

# Initialize background matrix for voxelization
gx, gy, gz = np.shape(multiLabelMatrix)
# background = np.zeros((int(gx / (scale[0] * spacing[0])), int(gy / (scale[1] * spacing[1])), int(gz / (scale[2] * spacing[2]))), dtype=np.uint8)
background = np.zeros((int(gx / scale), int(gy / scale), int(gz / scale)), dtype=np.uint8)

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
    croppedMatrix = np.ascontiguousarray(croppedMatrix)
    
    if targetVolume:
        iso = isovalue
    #print("isovalue for label",i, "is:", iso)

    # Extract isosurface
    isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso, spacing)
    faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()
    #print(faces.shape, nodes.shape)
    

    x, y, z = np.shape(croppedMatrix)
    # Voxelize the isosurface
    if NB:
        voxelizer = MeshVoxelizerNumba(polyData, smoothedMatrix, x, y, z, scale, background, bounds, label)
        background = voxelizer.voxeliseMesh()
    else:
        voxelizer = MeshVoxelizer(polyData, smoothedMatrix, x, y, z, scale, background, bounds, label)
        background = voxelizer.voxeliseMesh()
    
# Resulting voxelized matrix
newMatrix = background
