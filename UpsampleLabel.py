#from Preprocess import MeshPreprocessor
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
import numpy as np

preprocessor = MeshPreprocessor(originalMatrix, sigma, targetVolume)
smoothedMatrix, isovalue = preprocessor.meshPreprocessing()
print(isovalue)
isosurfaceExtractor = IsosurfaceExtractor(smoothedMatrix, isovalue)
faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()

gx, gy, gz = np.shape(originalMatrix)
voxelizer = MeshVoxelizer(polyData, gx, gy, gz, scale)
newMatrix = voxelizer.voxeliseMesh()
