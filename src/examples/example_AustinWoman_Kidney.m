%% GENERATE AND PROCESS 3D MEDICAL IMAGE WITHOUT EVALUATING RESULTS
% This script upsamples a 3D medical image obtained from the AustinWoman 
% dataset. The script demonstrates the steps involved in preparing and 
% processing 3D medical image data without evaluating the results.
%
% CITATION:
% J. W. Massey and A. E. Yilmaz, "AustinMan and AustinWoman: 
% High-fidelity, anatomical voxel models developed from the VHP color 
% images," in Proc. 38th Annual International Conference of the IEEE 
% Engineering in Medicine and Biology Society (IEEE EMBC), Orlando, 
% FL, Aug. 2016.
% URL: https://web.corral.tacc.utexas.edu/AustinManEMVoxels/AustinWoman/index.html
%
% AUTHOR:
%     Liangpu Liu, Rui Xu, Bradley Treeby
% DATE:
%     26th August 2024
% LAST UPDATE:
%     11th November 2024
%
% This script is part of the pySegmentationUpsampler 
% Copyright (C) 2024 Liangpu Liu, Rui Xu, Bradley Treeby
%
% This script is distributed under the terms of the GNU Lesser General 
% Public License as published by the Free Software Foundation, either 
% version 3 of the License, or (at your option) any later version.
% See <http://www.gnu.org/licenses/>.

%% SETUP FILE PATHS AND ADD DEPENDENCIES
% Define the paths to the required code and data directories.
folderPath = pwd;
codeDirect = folderPath + "/TestSupportingFunction";
pythonFunction = folderPath + "/runPythonFunction.py";
dataDirect = fileparts(folderPath) + "/data";
addpath(codeDirect)

%% IMPORTANT VARIABLES
% Define key variables used in the upsampling process.
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (ignored if Volume is 0)
% Volume: Target volume for upsampling (0 to ignore)

dx = 0.8;                     
sigma = 0.4;                  
isovalue = 0.4;               
Volume = 0;                   

%% LOAD AND PREPARE DATA
% Load the initial 3D shape matrix with multiple labels from a file.
load(dataDirect + "/padded_liver.mat")
originalMatrix = paddMatrix;

%% UPSAMPLE THE ORIGINAL MATRIX
% Use a Python script to upsample the original matrix. The upsampling is 
% performed by invoking a Python script that applies a series of 
% transformations to the 3D data.
pyenv;
newMatrix = pyrunfile(pythonFunction, ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      sigma = sigma, ...
                      targetVolume = Volume, ...
                      scale = [dx, dx, dx], ...
                      spacing = [1 1 1], ...
                      iso = isovalue, ...
                      fillGaps = true, ...
                      NB = true);

newMatrix = double(newMatrix);

%% PLOT RESULTS
% Visualize the original and upsampled 3D matrices.
figure;
subplot(1, 2, 1);
imagesc(originalMatrix(:, :, 17));
axis image; 
title(sprintf('Input Image')); 
set(gca, "Fontsize", 20);

subplot(1, 2, 2);
imagesc(newMatrix(:, :, 20));
axis image; 
title(sprintf('Output Image, Gap filling applied')); 
set(gca, "Fontsize", 20);
