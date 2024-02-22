
%% Create some data
clear all;

% Low resolution.
N = 60;
radius = round(N/3);
%originalMatrix = makeShapes("Complex", [radius], [N,N,80], [0, 0, 0]);
originalMatrix = makeShapes("MultiLabel", [radius], [N,N,80], [0, 0, 0]);
%originalMatrix = makeShapes("BallHole",[radius, floor(radius/3)], [N,N,N],[0,0,0]);
%%
% Set grid spacing.
dx = 0.29;
sigma = 0.68; Volume = 0;
%sigma = 0.8; Volume = 0.22;
%newMatrix = pyUpsampleLabel(originalMatrix, dx, sigma, Volume);
pyenv;
newMatrix = pyrunfile("UpsampleMultiLabels.py","newMatrix", multiLabelMatrix = py.numpy.array(originalMatrix), sigma = sigma, targetVolume = Volume, scale = dx);

% while sum(newMatrix,"all") == 0
%     newMatrix = UpsampleLabel(originalMatrix, dx, sigma);
% end
%% Create reference data
% Define rasterisation grid.
Nref = floor(N / dx);
fac = 1 / dx;
radiusRef = radius / dx;
%referenceMatrix = makeShapes("Complex", [radiusRef], [207,207,276], [0, 0, 0]);
referenceMatrix = makeShapes("MultiLabel", [radiusRef], [Nref,Nref,floor(80/0.29)], [0, 0, 0]);
%referenceMatrix = makeShapes("BallHole",[radiusRef, floor(radiusRef/3)], [Nref,Nref,Nref],[0,0,0]);
%% Plot
newMatrix = double(newMatrix);
figure;
subplot(1, 5, 1);
imagesc(newMatrix(:, :, round(end/2)));
axis image;
title('Output Image');

subplot(1, 5, 2);
imagesc(referenceMatrix(:, :, round(end/2)));
axis image;
title('Reference Image')

subplot(1, 5, 3);
imagesc(newMatrix(:, :, round(end/2)) - referenceMatrix(:, :, round(end/2)));
axis image;
title('Difference Image - Z-axis')

subplot(1, 5, 4);
imagesc(squeeze(newMatrix(round(end/2), :, :) - referenceMatrix(round(end/2), :, :)));
axis image;
title('Difference Image - X-axis')

subplot(1, 5, 5);
imagesc(squeeze(newMatrix(:, round(end/2), :) - referenceMatrix(:, round(end/2), :)));
axis image;
title('Difference Image - Y-axis')

%%
DoC = DegreeOfComplexity(originalMatrix);
DifferenceMatrix = abs(referenceMatrix-newMatrix);
voxelPlot(single(DifferenceMatrix>0))
Diff = sum(DifferenceMatrix,"all");
DoCgrade = Diff * DoC ^ 3;
fprintf('Grade by Degree of Complexity: %d\n',DoCgrade);
Volumegrade = Diff / sum(referenceMatrix,"all");
fprintf('Grade by Volume: %d\n',Volumegrade);
