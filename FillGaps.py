import numpy as np

class FillGaps:

    def __init__(self, newMatrix, smoothedMatrixList, dx, isovalue):
        self.newMatrix = newMatrix
        self.smoothedMatrixList = smoothedMatrixList
        self.dx = dx
        self.isovalue = isovalue
    
    def findSurroundings(self,x,y,z):
        surroundings = []
        xx, yy, zz = self.newMatrix.shape
        for i in range(max(0, x-1), min(x+2, xx-1)):
            for j in range(max(0, y-1), min(y+2, yy-1)):
                for k in range(max(0, z-1), min(z+2, zz-1)):
                    if (i, j, k) != (x, y, z) and self.newMatrix[i ,j, k] != 0:
                        surroundings.append(self.newMatrix[i, j, k])
        return surroundings

    def fillZeros(self):
        zeros = np.argwhere(self.newMatrix == 0)
        
        for x, y, z in zeros:
            inMesh = 0

            for smoothedMatrix in self.smoothedMatrixList:
                if smoothedMatrix[int(x*self.dx[0]),int(y*self.dx[1]),int(z*self.dx[2])] > self.isovalue:
                    inMesh = 1
                    continue

            if inMesh:
                surroundings = self.findSurroundings(x,y,z)
                
                if surroundings:
                    mostFrequent = np.bincount(surroundings).argmax()
                    self.newMatrix[x, y, z] = mostFrequent
                    

        print("zeros filled")
        return self.newMatrix
