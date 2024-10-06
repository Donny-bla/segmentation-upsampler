%% CONDUCTING GRID SEARCH OF SIGMA AND ISOVALUE IN UPSAMPLING
% This script scans various sigma (smoothing factor) and isovalue 
% (threshold) settings to evaluate their effects on 3D upsampled shapes. 
% It computes the differences between the upsampled and reference shapes 
% and evaluates the number of gaps and volume differences.

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

%% SETUP FILE PATHS AND ADD DEPENDENCIES
% Define the paths to the required code directory.
folderPath = pwd;
codeDirect = folderPath + "/code";
dataDirect = folderPath + "/data";
addpath(codeDirect)

%% CREATE ORIGINAL DATA (LOW-RESOLUTION 3D SHAPE)
% Low-resolution grid parameters
N = 60;                      % Grid size in X and Y directions
radius = round(N / 3);        % Radius of the shape

% Generate a complex multi-label 3D shape matrix
originalMatrix = makeShapes("MultiLabel", [radius], [N, N, 80], [0, 0, 0]);

%% UPSAMPLE SETTINGS
dx = 0.3;                     % Grid spacing for upsampling

% Define ranges for sigma (smoothing factor) and isovalue (threshold)
sigma = 0.6:0.025:1.1;        % Range of sigma values
isovalue = 0.44:0.0035:0.51;  % Range of isovalue values

%% CREATE REFERENCE DATA
% Parameters for generating reference shapes
Nref = floor(N / dx);          % Grid size for reference data in X and Y
radiusRef = radius / dx;       % Scaled radius for reference shape

% Generate the reference and full shapes
referenceMatrix = makeShapes("MultiLabel", [radiusRef], ...
                             [Nref, Nref, floor(80 / dx)], [0, 0, 0]);
fullMatrix = makeShapes("Ball", [radiusRef - 2], ...
                        [Nref, Nref, floor(80 / dx)], [0, 0, 0]);

%% INITIALIZE ARRAYS TO STORE RESULTS
AllDiff = [];  % To store volume differences
AllGaps = [];  % To store gaps in the full matrix

%% SCAN THROUGH SIGMA AND ISOVALUE COMBINATIONS
for s = sigma    
    Volumegrade = [];  % Initialize for each sigma
    Gapsgrade = [];    % Initialize for each sigma
    
    for iso = isovalue
        disp(['Processing Sigma: ', num2str(s), ', Isovalue: ', num2str(iso)]); 

        % Initialize Python environment
        pyenv;
        
        % Upsample the original matrix using the specified sigma and isovalue
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
        DifferenceMatrix = referenceMatrix ~= newMatrix;
        Diff = sum(DifferenceMatrix, "all");  % Sum of differences
    
        % Compute grades based on volume differences and gaps
        Volumegrade(end+1) = Diff / sum(referenceMatrix > 0, "all");
        Gapsgrade(end+1) = sum(newMatrix(fullMatrix == 1) == 0);
    end

    % Store grades for the current sigma value
    AllGaps = [AllGaps; Gapsgrade];
    AllDiff = [AllDiff; Volumegrade];
end

%% PLOT RESULTS
figure;

% Plot gaps with respect to sigma and isovalue
subplot(1, 2, 1);
colormap(subplot(1, 2, 1), 'hot');  % Set colormap
cb = colorbar();                     % Add colorbar
cb.Label.String = 'Number of Gaps';  % Set colorbar label
cb.FontSize = 14;                    % Set font size
hold on;
imagesc(isovalue, sigma, AllGaps);   % Display gap data
contour(isovalue, sigma, AllGaps, [0 500], 'LineWidth', 2, ...
        'Color', 'green', 'LineStyle', '--');  % Contour for 500 gaps
contour(isovalue, sigma, AllDiff, [0 0.04], 'LineWidth', 2, ...
        'Color', 'blue', 'LineStyle', '--');   % Contour for volume grade 0.04
hold off;
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20);
xlabel("Isovalue", 'FontSize', 20);
ylabel("Sigma", 'FontSize', 20);
legend("500 Gaps", "Volume Grade 0.04", 'FontSize', 14);

% Plot volume grades with respect to sigma and isovalue
subplot(1, 2, 2);
colormap(subplot(1, 2, 2), 'hot');  % Set colormap
cb = colorbar();                     % Add colorbar
cb.Label.String = 'Grade by Volume'; % Set colorbar label
cb.FontSize = 14;                    % Set font size
hold on;
imagesc(isovalue, sigma, AllDiff);   % Display volume grade data
contour(isovalue, sigma, AllDiff, [0 0.04], 'LineWidth', 2, ...
        'Color', 'blue', 'LineStyle', '--');  % Contour for volume grade 0.04
hold off;
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20);
xlabel("Isovalue", 'FontSize', 20);
ylabel("Sigma", 'FontSize', 20);
legend("0.04", 'FontSize', 14);
