# Import necessary classes
#from Preprocess import MeshPreprocessor  # If using the MeshPreprocessor from a different file
from RigorousPreprocess import MeshPreprocessor  # Assuming MeshPreprocessor is defined in RigorousPreprocess
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
import numpy as np

# Create a MeshPreprocessor instance and perform preprocessing
preprocessor = MeshPreprocessor(originalMatrix, sigma, targetVolume)
smoothedMatrix, isovalue, croppedMatrix, bounds = preprocessor.meshPreprocessing() 

# Manually set isovalue and ensure the matrix is contiguous in memory
if targetVolume:
    iso = isovalue
print("isovalue is:", iso)
croppedMatrix = np.ascontiguousarray(croppedMatrix)

# Print shape and bounds of the cropped matrix
print(croppedMatrix.shape)
print(bounds)

# Extract isosurface using IsosurfaceExtractor
isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, iso)
faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

# Initialize background matrix for voxelization
gx, gy, gz = np.shape(originalMatrix)
background = np.zeros((int(gx / scale), int(gy / scale), int(gz / scale)), dtype=np.uint8)
label = 1

# Voxelize the mesh using MeshVoxelizer
x, y, z = np.shape(croppedMatrix)
voxelizer = MeshVoxelizer(polyData, x, y, z, scale, background, bounds, label)
newMatrix = voxelizer.voxeliseMesh()

# Print shape of the voxelized matrix
print(newMatrix.shape)
