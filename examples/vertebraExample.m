%% Generate and process 3D medical image without evaluating the results.
% This script upsamples a 3D segmented vertebra
% citation: Liebl, H., Schinz, D., Sekuboyina, A., Malagutti, L., Löffler, M. T., Bayat, A., ... & Kirschke, J. S. (2021). A computed tomography vertebral segmentation dataset with anatomical variations and multi-vendor scanner data. Scientific data, 8(1), 284
% url: https://osf.io/t98fz/

%% Important Variables
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (will be ignored unless Volume is not applied)
% Volume: Target volume for upsampling (0 to not applied)

dx = 0.8;                     
sigma = 0.7;                  
isovalue = 0.4;               
Volume = 0;  
spacing = [0.2910 0.2910 1.2500];

%% Create some data
% Generate an initial 3D shape matrix with multiple labels.
Mask = niftiread("sub-gl003_dir-ax_seg-vert_msk.nii.gz");
originalMatrix = double(Mask);

%% Upsample the original matrix
% Use a Python script to upsample the original matrix.
pyenv;
newMatrix = pyrunfile("UpsampleMultiLabels.py", ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      sigma = sigma, ...
                      targetVolume = Volume, ...
                      scale = [dx, dx, dx], ...
                      spacing = spacing, ...
                      iso = isovalue, ...
                      fillGaps = false, ...
                      NB = true);

newMatrix = double(newMatrix);
%% Plot results
figure;
subplot(1, 3, 1);
crossSection = squeeze(originalMatrix(end/2, :, :));
crossSection = imrotate(crossSection,90);
imagesc(crossSection);
axis image; title(sprintf('Input Image\n(Spacing Undefined)')); set(gca, "Fontsize", 20);

subplot(1, 3, 2);
crossSection = squeeze(originalMatrix(end/2, :, :));
crossSection = imrotate(crossSection,90);
imagesc([0:0.2910:512*0.2910],[0:1.25:214*1.25],crossSection);
axis image; title(sprintf('Input Image\n(Spacing Defined)')); set(gca, "Fontsize", 20);

subplot(1, 3, 3);
crossSection = squeeze(newMatrix(end/2-1, :, :));
crossSection = imrotate(crossSection,90);
imagesc(crossSection);
axis image; title(sprintf('Output Image\n(Spacing defined)')); set(gca, "Fontsize", 20);

