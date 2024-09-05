%% INVESTIGATE UPSAMPLING METHODS FOR 3D SHAPES
% This script compares two different method for upsampling complex test object 
% 3D shapes: Mesh-based, trilinear interpolation, and nearest-neighbor. 
% It evaluates the performance of each method based on Degree of Complexity (DoC) 
% and volume grade as a function of upsampling grid spacing (dx).

% AUTHOR:
%     Liangpu Liu, Rui Xu, Bradley Treeby
% DATE:
%     4th September 2024
% LAST UPDATE:
%     4th September 2024
%
% This script is part of the k-Wave Toolbox (http://www.k-wave.org).
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
codeDirect = folderPath + "/code";
dataDirect = folderPath + "/data";
addpath(codeDirect)

%% CREATE INITIAL 3D SHAPE DATA
% Low-resolution grid parameters.
N = 60;                      % Grid size
radius = round(N / 3);        % Radius of the shape
shapes = makeShapes("Complex", [radius], [N, N, N], [0, 0, 0]);

% Use the first shape as the original matrix.
originalMatrix = shapes{1};

%% UPSAMPLING PARAMETERS
sigma = 0.68;                 % Gaussian smoothing parameter
Volume = 0;                   % Target volume (not applied in this case)
isovalue = 0.513;             % Isovalue threshold for surface extraction
dx = [0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95];  % Grid spacing for upsampling

% Initialize Python environment.
pyenv;

%% INITIALIZE ARRAYS FOR STORING GRADES
AllDoCgrade = [];             % Array to store DoC grades.
AllVolumegrade = [];          % Array to store volume grades.
AllDoCdxgrade = [];           % Array to store DoC grades scaled by dx.

%% DEGREE OF COMPLEXITY CALCULATION FOR ORIGINAL SHAPE
DoC = DegreeOfComplexity(originalMatrix);

%% UPSAMPLE AND EVALUATE METHODS
% Loop through each upsampling method: 
% 1 = Mesh-based, 2 = Trilinear interpolation, 3 = Nearest-neighbor.
for s = 1:3
    % Initialize arrays for current method grades.
    DoCgrade = [];
    Volumegrade = [];
    DoCdxgrade = [];

    % Loop through each grid spacing (dx) value.
    for ii = dx
        % Create reference data.
        Nref = floor(double(N / ii));
        radiusRef = floor(radius / ii);
        referenceMatrix = makeShapes("Complex", [radiusRef], [Nref, Nref, Nref], [0, 0, 0]);

        % Perform upsampling based on the method.
        switch(s)
            case 1  % Mesh-based method using Python script.
                newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                                      "newMatrix", ...
                                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                                      sigma = sigma, ...
                                      targetVolume = Volume, ...
                                      scale = [ii, ii, ii], ...
                                      spacing = [1 1 1], ...
                                      iso = isovalue, ...
                                      fillGaps = false, ...
                                      NB = true);
                newMatrix = single(newMatrix);
            case 2  % Trilinear interpolation method.
                newMatrix = trinterp(originalMatrix, ii);
                newMatrix = single(newMatrix > 0);
            case 3  % Nearest-neighbor interpolation method.
                newMatrix = nearestn(originalMatrix, ii);
                newMatrix = single(newMatrix > 0);
        end

        % Compute the differences between the upsampled and reference matrices.
        DifferenceMatrix = referenceMatrix ~= newMatrix;
        Diff = sum(DifferenceMatrix, "all");

        % Calculate grades based on volume differences and DoC.
        Volumegrade(end+1) = Diff / sum(referenceMatrix > 0, "all");
        DoCgrade(end+1) = Diff * DoC^3;
        DoCdxgrade(end+1) = Diff * (DoC * ii)^3;
    end

    % Store grades for the current method.
    AllDoCgrade = [AllDoCgrade; DoCgrade];
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% PLOTTING RESULTS
figure;

% Plot Degree of Complexity (DoC) grades as a function of dx.
subplot(1, 2, 1);
hold on;
plot(dx, AllDoCdxgrade, 'LineWidth', 2);
hold off;
set(gca, "FontSize", 14);
title("Grade by Degree of Complexity", 'FontSize', 20);
xlim([0.2, 0.95]);
xlabel("dx", 'FontSize', 20);
ylabel("Grade", 'FontSize', 20);
legend("Mesh-Based", "Trinterp", "NearestN", 'FontSize', 18);

% Plot volume grades as a function of dx.
subplot(1, 2, 2);
hold on;
plot(dx, AllVolumegrade, 'LineWidth', 2);
hold off;
set(gca, "FontSize", 14);
title("Grade by Volume", 'FontSize', 20);
xlim([0.2, 0.95]);
xlabel("dx", 'FontSize', 20);
ylabel("Grade", 'FontSize', 20);
legend("Mesh-Based", "Trinterp", "NearestN", 'FontSize', 18);
