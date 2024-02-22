#from Preprocess import MeshPreprocessor
from RigorousPreprocess import MeshPreprocessor
from Extractor import IsosurfaceExtractor
from Voxelizer import MeshVoxelizer
from LabelSeparater import LabelSeparation
from scipy.ndimage import gaussian_filter
import numpy as np

gx, gy, gz = np.shape(multiLabelMatrix)
background = np.zeros((int(gx / scale),
                        int(gy / scale),
                        int(gz / scale)), dtype=np.uint8)

labelSeparationInstance = LabelSeparation(multiLabelMatrix)
labelSeparationInstance.separateLabels()
separateMatrices, labelVolume, labels = labelSeparationInstance.getResults()
print(labels)
#singleLabelMatrix = separateMatrices[0]
#preprocessor = MeshPreprocessor(singleLabelMatrix, sigma, targetVolume)
#smoothedMatrix, isovalue, croppedMatrix, bounds = preprocessor.meshPreprocessing()
#
for i in range(len(separateMatrices)):
    singleLabelMatrix = separateMatrices[i]
    label = labels[i]
    print(singleLabelMatrix.shape, label)

    preprocessor = MeshPreprocessor(singleLabelMatrix, sigma, targetVolume)
    smoothedMatrix, isovalue, croppedMatrix, bounds  = preprocessor.meshPreprocessing() #
    croppedMatrix = np.ascontiguousarray(croppedMatrix)
    print(croppedMatrix.shape)

    isosurfaceExtractor = IsosurfaceExtractor(croppedMatrix, isovalue)
    faces, nodes, polyData = isosurfaceExtractor.extractIsosurface()
    
    x, y, z = np.shape(croppedMatrix)
    voxelizer = MeshVoxelizer(polyData, x, y, z, scale, background, bounds, label)
    background = voxelizer.voxeliseMesh()

newMatrix = background
