%% GENERATE AND PROCESS 3D MEDICAL IMAGE WITHOUT EVALUATING RESULTS
% This script upsamples a 3D segmented vertebra obtained from a public 
% dataset. The script demonstrates the steps involved in preparing and 
% processing 3D medical image data without evaluating the results.
%
% CITATION:
%     Liebl, H., Schinz, D., Sekuboyina, A., Malagutti, L., Löffler, 
%     M. T., Bayat, A., ... & Kirschke, J. S. (2021). A computed 
%     tomography vertebral segmentation dataset with anatomical 
%     variations and multi-vendor scanner data. Scientific data, 
%     8(1), 284.
%     URL: https://osf.io/t98fz/
%
% AUTHOR:
%     Liangpu Liu, Rui Xu, Bradley Treeby
% DATE:
%     26th August 2024
% LAST UPDATE:
%     19th February 2025
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
pythonFunction = fileparts(folderPath) + "/SegmentationUpsampler/UpsampleMultiLabels.py";
dataDirect = fileparts(folderPath) + "/data";
addpath(codeDirect)
addpath(fileparts(pythonFunction))
%% IMPORTANT VARIABLES
% Define key variables used in the upsampling process.
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (ignored if Volume is 0)
% Volume: Target volume for upsampling (0 to ignore)

dx = 0.8;        
sigma = 0.7;      
isovalue = 0.4;    
Volume = 0;        

%% LOAD AND PREPARE DATA
% Load the initial 3D segmented vertebra matrix from a NIfTI file.
Mask = niftiread(dataDirect + "/sub-gl003_dir-ax_seg-vert_msk.nii.gz");
info = niftiinfo(dataDirect + "/sub-gl003_dir-ax_seg-vert_msk.nii.gz");
originalMatrix = double(Mask);
spacing  = info.PixelDimensions;  % Extract pixel spacing information

%% UPSAMPLE THE ORIGINAL MATRIX
% Use a Python script to upsample the original matrix. The upsampling is 
% performed by invoking a Python script that applies a series of 
% transformations to the 3D data.
%% I haven't make this update packaged, just move to the SegmentationUpsampler folder while running this part
pyenv;
newMatrix = pyrunfile(pythonFunction, ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      scale = [dx, dx, dx], ...
                      spacing = spacing);

newMatrix = double(newMatrix);  % Convert the new matrix to double precision

%% PLOT RESULTS
% Visualize the original and upsampled 3D matrices with and without defined 
% spacing.
figure;

% Plot the original matrix without defined spacing
subplot(1, 3, 1);
crossSection = squeeze(originalMatrix(end/2, :, :));
crossSection = imrotate(crossSection, 90);
imagesc(crossSection);
axis image; 
title(sprintf('Input Image\n(Spacing Undefined)')); 
set(gca, "Fontsize", 20);

% Plot the original matrix with defined spacing
subplot(1, 3, 2);
crossSection = squeeze(originalMatrix(end/2, :, :));
crossSection = imrotate(crossSection, 90);
imagesc([0:0.2910:512*0.2910],[0:1.25:214*1.25], crossSection);
axis image; 
title(sprintf('Input Image\n(Spacing Defined)')); 
set(gca, "Fontsize", 20);

% Plot the upsampled matrix with defined spacing
subplot(1, 3, 3);
crossSection = squeeze(newMatrix(end/2-1, :, :));
crossSection = imrotate(crossSection, 90);
imagesc(crossSection);
axis image; 
title(sprintf('Output Image\n(Spacing Defined)')); 
set(gca, "Fontsize", 20);
