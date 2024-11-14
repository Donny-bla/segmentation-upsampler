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
%     3rd October 2024
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

%% CREATE INITIAL 3D SHAPE DATA
% Low-resolution grid parameters.
N = 60;                      % Grid size
radius = round(N / 3);        % Radius of the shape
originalMatrix = makeShapes("Complex", [radius], [N, N, N], [0, 0, 0]);

%% UPSAMPLING PARAMETERS
sigma = 0.68;                 % Gaussian smoothing parameter
Volume = 0;                   % Target volume (not applied in this case)
isovalue = 0.513;             % Isovalue threshold for surface extraction
dx = [0.3 0.5 0.7 0.9];           % Grid spacing for upsampling

%dx = 0.2:0.05:0.95;           % scale applied in thesis plotting

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
        disp("processing scale = " + string(ii))
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

%% Plotting Results

figure('Position', [300 300 600 400])
subplot(1,2,1)
hold on
plot(dx, AllDoCdxgrade(1,:), 'k+-');
plot(dx, AllDoCdxgrade(2,:), ':s', 'color', (1/255) * [80 7 120]);
plot(dx, AllDoCdxgrade(3,:), '--*', 'color', (1/255) * [52 198 198]);
xlim([0.2 0.95])
xlabel("Upscaling Factor [dx]"); 
ylabel("Grade by Degree of Complexity"); 
legend("MeshBased","Trinterp", "NearestN", 'location', 'southeast'); 
box on; grid on;

subplot(1,2,2)
hold on
plot(dx, AllVolumegrade(1,:), 'k+-');
plot(dx, AllVolumegrade(2,:), ':s', 'color', (1/255) * [80 7 120]);
plot(dx, AllVolumegrade(3,:), '--*', 'color', (1/255) * [52 198 198]);
xlim([0.2 0.95])
xlabel("Upsampling Factor [dx]")
ylabel('Grade by Volume')
legend("MeshBased","Trinterp", "NearestN", 'location', 'southeast')
box on; grid on;
