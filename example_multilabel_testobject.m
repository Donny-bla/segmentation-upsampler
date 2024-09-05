%% GENERATE AND PROCESS 3D SHAPES WITH DIFFERENT CONFIGURATIONS AND EVALUATE RESULTS
% This script creates 3D shapes in a low-resolution grid, upsamples them, 
% creates reference data, visualizes the results, and evaluates the 
% differences using various metrics.
%
% AUTHOR:
%     Liangpu Liu, Rui Xu, Bradley Treeby
% DATE:
%     26th August 2024
% LAST UPDATE:
%     26th August 2024
%
% This script is part of the k-Wave Toolbox (http://www.k-wave.org).
% Copyright (C) 2024 Liangpu Liu, Rui Xu, Bradley Treeby
%
% This script is distributed under the terms of the GNU Lesser General 
% Public License as published by the Free Software Foundation, either 
% version 3 of the License, or (at your option) any later version.
% See <http://www.gnu.org/licenses/>.

%% SETUP FILE PATHS AND ADD DEPENDENCIES
% Define the paths to the required code and data directories.
folderPath = pwd;
codeDirect = folderPath + "/code";
dataDirect = folderPath + "/data";
addpath(codeDirect)


%% IMPORTANT VARIABLES
% Define key variables used in the 3D shape creation and upsampling process.
% N: Grid size for the low-resolution grid
% radius: Radius of the shape
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (ignored if Volume is 0)
% Volume: Target volume for upsampling (0 to ignore)
% Nref: Grid size for the reference data
% radiusRef: Radius for the reference shape

N = 60;                       
radius = round(N/3);          
dx = [0.5, 0.5, 0.5];         
spacing = [1.0, 1.0, 1.0];    
sigma = 0.6;                  
isovalue = 0.4;               
Volume = 0;                   
Nref = floor(N / (dx(1) * spacing(1)));  
fac = 1 / (dx(1) * spacing(1));          
radiusRef = radius / (dx(1) * spacing(1));

%% CREATE INITIAL 3D SHAPE
% Generate an initial 3D shape matrix with multiple labels.
originalMatrix = makeShapes("MultiLabel", [radius], [N, N, 80], [0, 0, 0]);

%% UPSAMPLE THE ORIGINAL MATRIX
% Use a Python script to upsample the original matrix.
pyenv;
newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      sigma = sigma, ...
                      targetVolume = Volume, ...
                      scale = dx, ...
                      spacing = spacing, ...
                      iso = isovalue, ...
                      fillGaps = false, ...
                      NB = true);

%% CREATE REFERENCE DATA
% Generate a high-resolution reference matrix with the same shape parameters.
referenceMatrix = makeShapes("MultiLabel", [radiusRef], ...
                             [Nref, Nref, floor(80/0.5)], [0, 0, 0]);

%% PLOT RESULTS
% Visualize the original, upsampled, and reference matrices, and evaluate 
% the differences.
newMatrix = double(newMatrix);

figure;
subplot(2, 3, 1);
imagesc(originalMatrix(:, :, end/2));
axis image; 
title('Input Image'); 
set(gca, "Fontsize", 20);

subplot(2, 3, 2);
imagesc(newMatrix(:, :, end/2));
axis image; 
title('Output Image'); 
set(gca, "Fontsize", 20);

subplot(2, 3, 3);
imagesc(referenceMatrix(:, :, end/2));
axis image; 
title('Reference Image'); 
set(gca, "Fontsize", 20);

subplot(2, 3, 4);
imagesc(newMatrix(:, :, end/2) - referenceMatrix(:, :, end/2));
axis image; 
title('Difference Image - Z-axis'); 
set(gca, "Fontsize", 20);

subplot(2, 3, 5);
imagesc(squeeze(newMatrix(end/2, :, :) - referenceMatrix(end/2, :, :)));
axis image; 
title('Difference Image - X-axis'); 
set(gca, "Fontsize", 20);

subplot(2, 3, 6);
imagesc(squeeze(newMatrix(:, end/2, :) - referenceMatrix(:, end/2, :)));
axis image; 
title('Difference Image - Y-axis'); 
set(gca, "Fontsize", 20);

%% EVALUATE THE RESULT
% Calculate the degree of complexity and differences between the matrices.
DoC = DegreeOfComplexity(originalMatrix);
DifferenceMatrix = abs(referenceMatrix - single(newMatrix > 0));

% Compute and display the grades based on complexity and volume.
Diff = sum(DifferenceMatrix, "all");
DoCgrade = Diff * DoC ^ 3;
fprintf('Grade by Degree of Complexity: %d\n', DoCgrade);

Volumegrade = Diff / sum(referenceMatrix, "all");
fprintf('Grade by Volume: %d\n', Volumegrade);
