%% Generate and process 3D medical image without evaluating the results.
% This script upsamples a 3D medical image obtained from austin woman
% citation: J. W. Massey and A. E. Yilmaz, "AustinMan and AustinWoman: High-fidelity, anatomical voxel models developed from the VHP color images," in Proc. 38th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (IEEE EMBC), Orlando, FL, Aug. 2016.
% url: https://web.corral.tacc.utexas.edu/AustinManEMVoxels/AustinWoman/index.html

%% Important Variables
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (will be ignored unless Volume is not applied)
% Volume: Target volume for upsampling (0 to not applied)

dx = 0.8;                     
sigma = 0.4;                  
isovalue = 0.4;               
Volume = 0;  

%% Create some data
% Generate an initial 3D shape matrix with multiple labels.
load("padded_liver.mat")
originalMatrix = paddMatrix;
%originalMatrix = double(Mask);

%% Upsample the original matrix
% Use a Python script to upsample the original matrix.
pyenv;
newMatrix = pyrunfile("UpsampleMultiLabels.py", ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      sigma = sigma, ...
                      targetVolume = Volume, ...
                      scale = [dx, dx, dx], ...
                      spacing = [1 1 1], ...
                      iso = isovalue, ...
                      fillGaps = true, ...
                      NB = true);

newMatrix = double(newMatrix);
%% Plot results
figure;
subplot(1, 2, 1);
imagesc(originalMatrix(:, :, 17));
axis image; title(sprintf('Input Image')); set(gca, "Fontsize", 20);

subplot(1, 2, 2);
imagesc(newMatrix(:, :, 20));
axis image; title(sprintf('Output Image')); set(gca, "Fontsize", 20);

