%% CONDUCT GRID SEARCH OF SIGMA AND ISOVALUE ON UPSAMPLING SINGLELABEL
% This script scans various sigma (smoothing factor) and isovalue (threshold)
% settings to evaluate their effects on upsampling a complex 3D shape.
% It computes volume and Degree of Complexity (DoC) differences between the 
% upsampled and reference shapes.

% AUTHOR:
%     Liangpu Liu, Rui Xu, Bradley Treeby
% DATE:
%     4th September 2024
% LAST UPDATE:
%     4th September 2024
%
% This script is part of the pySegmentationUpsampler 
% Copyright (C) 2024 Liangpu Liu, Rui Xu, Bradley Treeby
%
% This script is distributed under the terms of the GNU Lesser General 
% Public License as published by the Free Software Foundation, either 
% version 3 of the License, or (at your option) any later version.
% See <http://www.gnu.org/licenses/>.

clear all;

%% SETUP FILE PATHS AND ADD DEPENDENCIES
% Define the paths to the required code directory.
folderPath = pwd;
codeDirect = fileparts(folderPath) + "/SegmentationUpsampler";
dataDirect = fileparts(folderPath) + "/data";
addpath(codeDirect)

%% CREATE ORIGINAL 3D SHAPE MATRIX
% Low-resolution grid parameters
N = 60;                      % Grid size
radius = round(N / 3);        % Radius of the shape

% Generate a complex multi-label 3D shape matrix
originalMatrix = makeShapes("Complex", [radius], [N, N, N], [0, 0, 0]);

%% SET UPSAMPLE SETTINGS
dx = 0.25;                    % Grid spacing for upsampling

% Define ranges for sigma (smoothing factor) and isovalue (threshold)
sigma = 0:0.5:2;              % Range of sigma values
isovalue = 0.3:0.1:0.7;      % Range of isovalue values

% Paramter set for sparse gird scan
% sigma = 0:0.2:2;              % Range of sigma values
% isovalue = 0.4:0.02:0.6;      % Range of isovalue values
%% CREATE REFERENCE DATA
% Define parameters for reference data rasterization
Nref = floor(N / dx);         % Grid size for reference data
fac = 1 / dx;                 % Upscaling factor
radiusRef = radius / dx;      % Scaled radius for the reference shape

% Generate the reference shape using the makeShapes function
referenceMatrix = makeShapes("Complex", [radiusRef], [Nref, Nref, Nref], [0, 0, 0]);

%% CALCULATE DEGREE OF COMPLEXITY FOR ORIGINAL SHAPE
DoC = DegreeOfComplexity(originalMatrix);

%% INITIALIZE ARRAYS TO STORE RESULTS
AllVolumegrade = [];  % Array to store volume grades
AllDoCdxgrade = [];   % Array to store DoC grades

%% SCAN THROUGH SIGMA AND ISOVALUE COMBINATIONS
% Loop through each sigma value
for s = sigma    
    Volumegrade = []; % Initialize array for volume grades
    DoCdxgrade = [];  % Initialize array for DoC grades
    
    % Loop through each isovalue
    for iso = isovalue
        disp(['Sigma: ', num2str(s), ', Isovalue: ', num2str(iso)])  % Display current settings

        % Upsample the original shape using the Python script
        newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                              "newMatrix", ...
                              multiLabelMatrix = py.numpy.array(originalMatrix), ...
                              sigma = s, ...
                              targetVolume = 0, ...
                              scale = [dx, dx, dx], ...
                              spacing = [1 1 1], ...
                              iso = iso, ...
                              fillGaps = false, ...
                              NB = true);
        newMatrix = double(newMatrix);  % Convert Python result to double

        % Calculate the difference between new and reference matrices
        DifferenceMatrix = newMatrix - referenceMatrix;
        Diff = sum(abs(DifferenceMatrix), "all");  % Sum of absolute differences
    
        % Compute grades based on volume differences and DoC
        Volumegrade(end+1) = Diff / sum(referenceMatrix, "all");
        DoCdxgrade(end+1) = Diff * (DoC * dx)^3;
    end

    % Store grades for the current sigma value
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% PLOT RESULTS
figure;

% Plot grades by Degree of Complexity (DoC)
subplot(1, 2, 1)
colormap(subplot(1, 2, 1), 'hot');  % Set colormap to 'hot'
cb = colorbar();
cb.Label.String = 'Grade by Degree of Complexity';
cb.FontSize = 14;
hold on
imagesc(isovalue, sigma, AllDoCdxgrade)  % Display DoC grades as an image
hold off
set(gca, 'FontSize', 14);
title("Multi-label Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)

% Plot grades by volume
subplot(1, 2, 2)
colormap(subplot(1, 2, 2), 'hot');  % Set colormap to 'hot'
cb = colorbar();
cb.Label.String = 'Grade by Volume';
cb.FontSize = 14;
hold on
imagesc(isovalue, sigma, AllVolumegrade)  % Display volume grades as an image
contour(isovalue, sigma, AllVolumegrade, [0 0.04], 'LineWidth', 2, ...
        'Color', 'blue', 'LineStyle', '--');  % Contour for volume grade 0.04
hold off
set(gca, 'FontSize', 14);
title("Multi-label Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)
legend("0.04", "FontSize", 14)
