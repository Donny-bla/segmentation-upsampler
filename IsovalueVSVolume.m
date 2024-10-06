%% INVESTIGATE THE EFFECT OF VOLUME RATIO IN SELECTING ISOVALUE
% This script investigates how the volume ratio changes with different 
% isovalues and Gaussian smoothing parameters (sigma) for a complex 3D 
% shape. The volume ratio is calculated for smoothed shapes using various 
% isovalues.

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

% 
%% SETUP FILE PATHS AND ADD DEPENDENCIES
% Define the paths to the required code directory.
folderPath = pwd;
codeDirect = folderPath + "/code";
dataDirect = folderPath + "/data";
addpath(codeDirect)

%% GENERATE ORIGINAL 3D SHAPE MATRIX
% Create a complex 3D shape matrix.
originalMatrix = makeShapes("Complex", [20], [60,60,60], [0,0,0]);

% Calculate the volume of the original shape (non-zero voxels).
originalVolume = sum(originalMatrix > 0, "all");

%% APPLY GAUSSIAN SMOOTHING
% Apply Gaussian smoothing with sigma values 0.7 and 1.5.
smoothMatrix0p7 = imgaussfilt3(originalMatrix, 0.7);
smoothMatrix1p5 = imgaussfilt3(originalMatrix, 1.5);

%% INITIALIZE VARIABLES FOR VOLUME RATIOS
% Define arrays to store volume ratios and range of isovalues.
v_0p7 = [];  % Volume ratios for sigma = 0.7
v_1p5 = [];  % Volume ratios for sigma = 1.5
iso = 0:0.0001:1;  % Range of isovalues to investigate

%% CALCULATE VOLUME RATIOS
% Loop through each isovalue and calculate volume ratios for both sigma values.
for ii = iso
    % Calculate the volume of smoothed shapes above the current isovalue.
    smoothedVolume0p7 = sum(smoothMatrix0p7 > ii, "all");
    smoothedVolume1p5 = sum(smoothMatrix1p5 > ii, "all");
    
    % Compute the volume ratio for sigma = 0.7.
    t = -1;
    if smoothedVolume0p7 < originalVolume
        t = 1;
    end
    v_0p7(end+1) = t / log(abs(smoothedVolume0p7 - originalVolume) / originalVolume);

    % Compute the volume ratio for sigma = 1.5.
    t = -1;
    if smoothedVolume1p5 < originalVolume
        t = 1;
    end
    v_1p5(end+1) = t / log(abs(smoothedVolume1p5 - originalVolume) / originalVolume);
end

%% PLOT RESULTS
% Plot the volume ratio as a function of isovalue for both sigma values.
figure;
hold on;

% Plot volume ratios for sigma = 0.7 and 1.5.
plot(iso, v_0p7, 'LineWidth', 2);  % Volume ratios for sigma = 0.7
plot(iso, v_1p5, 'LineWidth', 2);  % Volume ratios for sigma = 1.5

% Set plot limits, labels, and grid.
ylim([-2 2]);
xlim([0 1]);
grid on;
ylabel("Volume Ratio");
xlabel("Isovalue");
legend("sigma = 0.7", "sigma = 1.5");
set(gca, "FontSize", 20);

hold off;
