%% EVALUATING UPSAMPLEING USING DIFFERENT NORMALIZATION METHOD
% This script compares different method of evaluating upsampling quality
% voxelization. It computes Degree of Complexity (DoC) and volume grades 
% for each shape across multiple upsampling scales (dx).

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
folderPath = pwd;
codeDirect = fileparts(folderPath) + "/SegmentationUpsampler";
dataDirect = fileparts(folderPath) + "/data";
addpath(codeDirect)

%% CREATE INITIAL 3D SHAPES
shapes = cell(1, 4);
shapes{1} = makeShapes("BallHole", [10, round(10/3)], [30, 30, 30], ...
                       [0, 0, 0]);
shapes{2} = makeShapes("Bowl", [18, round(18/2)], [40, 40, 40], ...
                       [0, 0, 0]);
shapes{3} = makeShapes("Cylinder", [15, 30], [35, 35, 35], ...
                       [0, 0, 0]);
shapes{4} = makeShapes("Ball", [20], [45, 45, 45], [0, 0, 0]);

referenceShapes = cell(1, 4);

%% SET UPSAMPLING PARAMETERS
Volume = 0;                  
sigma = 0.6;                 
isovalue = 0.44;             
dx = 0.2:0.2:1;
% dx = 0.2:0.1:1; scale set for denser plot

pyenv;
%% INITIALIZE ARRAYS FOR STORING RESULTS
AllVolumegrade = [];         
AllDoCdxgrade = [];          

%% UPSAMPLE AND EVALUATE SHAPES
for s = 1:4
    originalMatrix = shapes{s};
    DoC = DegreeOfComplexity(originalMatrix);
    
    Volumegrade = [];
    DoCdxgrade = [];
    
    for ii = dx
        referenceShapes{1} = makeShapes("BallHole", [floor(10/ii), ...
                             floor(10/3/ii)], [floor(30/ii), ...
                             floor(30/ii), floor(30/ii)], [0, 0, 0]);
        referenceShapes{2} = makeShapes("Bowl", [floor(18/ii), ...
                             floor(18/2/ii)], [floor(40/ii), ...
                             floor(40/ii), floor(40/ii)], [0, 0, 0]);
        referenceShapes{3} = makeShapes("Cylinder", [floor(15/ii), ...
                             floor(30/ii)], [floor(35/ii), ...
                             floor(35/ii), floor(35/ii)], [0, 0, 0]);
        referenceShapes{4} = makeShapes("Ball", [floor(20/ii)], ...
                             [floor(45/ii), floor(45/ii), ...
                              floor(45/ii)], [0, 0, 0]);
        referenceMatrix = referenceShapes{s};
        
        disp("processing scale = " + string(ii))
        
        newMatrix = pyrunfile(codeDirect + "/UpsampleMultiLabels.py", ...
                              "newMatrix", ...
                              multiLabelMatrix = py.numpy.array( ...
                              originalMatrix), sigma = sigma, ...
                              targetVolume = Volume, scale = [ii, ii, ...
                              ii], spacing = [1 1 1], iso = isovalue, ...
                              fillGaps = false, NB = true);
        
        newMatrix = double(newMatrix);  % Convert to double
        
        DifferenceMatrix = abs(referenceMatrix - single(newMatrix > 0));
        Diff = sum(DifferenceMatrix, "all");
        
        Volumegrade(end+1) = Diff / sum(referenceMatrix, "all");
        DoCdxgrade(end+1) = Diff * (DoC * ii) ^ 3;
    end
    
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% PLOTTING RESULTS
figure;

% Plot Degree of Complexity (DoC) grades by shape
subplot(1, 2, 1);
hold on;
plot(dx(1:end-1), AllDoCdxgrade(:,1:end-1), 'LineWidth', 2);
hold off;
set(gca, 'FontSize', 20);
title("Grade by Shape", 'FontSize', 24);
xlabel("Scale of Upsampling", 'FontSize', 20);
ylabel("Grade", 'FontSize', 20);
xlim([0.2, 0.9]);
legend("BallHole", "Bowl", "Cylinder", "Ball", 'FontSize', 16);

% Plot volume grades by shape
subplot(1, 2, 2);
hold on;
plot(dx(1:end-1), AllVolumegrade(:,1:end-1), 'LineWidth', 2);
hold off;
set(gca, 'FontSize', 20);
title("Grade by Volume", 'FontSize', 24);
xlabel("Scale of Upsampling", 'FontSize', 20);
ylabel("Grade", 'FontSize', 20);
xlim([0.2, 0.9]);
legend("BallHole", "Bowl", "Cylinder", "Ball", 'FontSize', 16);
