#from Preprocess import MeshPreprocessor
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
import numpy as np

padWidth = 5
paddedMatrix = np.pad(originalMatrix, pad_width = padWidth, mode='constant', constant_values=0)

preprocessor = MeshPreprocessor(paddedMatrix, sigma, targetVolume)
smoothedMatrix, isovalue, croppedMatrix, bounds  = preprocessor.meshPreprocessing() #
croppedMatrix = np.ascontiguousarray(croppedMatrix)
print(croppedMatrix.shape)
print(bounds)
isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, isovalue)
faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()


gx, gy, gz = np.shape(paddedMatrix)
background = np.zeros((int(gx / scale),
                        int(gy / scale),
                        int(gz / scale)), dtype=np.uint8)
label = 1
x, y, z = np.shape(croppedMatrix)
voxelizer = MeshVoxelizer(polyData, x, y, z, scale, background, bounds, label)
paddedNewMatrix = voxelizer.voxeliseMesh()

unpad = int(padWidth/scale)
newMatrix = paddedNewMatrix[unpad:-unpad, unpad:-unpad, unpad:-unpad]
newMatrix = np.ascontiguousarray(newMatrix)
print(newMatrix.shape)

