%% Generate and process 3D shapes with different configurations and evaluate the results.
% This script creates 3D shapes in a low-resolution grid, upsamples them, 
% creates reference data, visualizes the results, and evaluates the 
% differences using various metrics.

%% Important Variables
% N: Grid size for the low-resolution grid
% radius: Radius of the shape
% dx: Grid spacing for upsampling
% sigma: Gaussian smoothing parameter 
% isovalue: Isovalue for isosurface extraction (will be ignored unless Volume is not applied)
% Volume: Target volume for upsampling (0 to not applied)
% Nref: Grid size for the reference data
% radiusRef: Radius for the reference shape
N = 60;                       
radius = round(N/3);          
dx = 0.7;                     
sigma = 0.6;                  
isovalue = 0.4;               
Volume = 0;                   
Nref = floor(N / dx);         
fac = 1 / dx;                 
radiusRef = radius / dx;      

%% Create some data
% Generate an initial 3D shape matrix with multiple labels.
originalMatrix = makeShapes("MultiLabel", [radius], [N, N, 80], [0, 0, 0]);

%% Upsample the original matrix
% Use a Python script to upsample the original matrix.
pyenv;
newMatrix = pyrunfile("UpsampleMultiLabels.py", ...
                      "newMatrix", ...
                      multiLabelMatrix = py.numpy.array(originalMatrix), ...
                      sigma = sigma, ...
                      targetVolume = Volume, ...
                      scale = dx, ...
                      iso = isovalue);

%% Create reference data
% Generate a high-resolution reference matrix with the same shape parameters.
referenceMatrix = makeShapes("MultiLabel", [radiusRef], [Nref, Nref, floor(80/dx)], [0, 0, 0]);

%% Plot results
% Convert the new matrix to double precision for processing.
newMatrix = double(newMatrix);

% Flag to control image cropping
cropImage = true;

if cropImage
    % Create a mask for cropping based on a smaller ball
    fullMatrix = makeShapes("Ball", [radiusRef - 2], [Nref, Nref, floor(80/dx)], [0, 0, 0]);
    
    % Find indices where the mask is 1
    [rowIndices, colIndices, depthIndices] = ind2sub(size(fullMatrix), find(fullMatrix == 1));
    
    % Calculate the minimum and maximum indices for cropping
    minRow = min(rowIndices); maxRow = max(rowIndices);
    minCol = min(colIndices); maxCol = max(colIndices);
    minDepth = min(depthIndices); maxDepth = max(depthIndices);
    
    % Plot the cropped images
    figure;
    subplot(2, 3, 1);
    imagesc(originalMatrix(:, :, end/2));
    axis image; title("Input Image"); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 2);
    imagesc(newMatrix(minRow:maxRow, minCol:maxCol, round((minDepth + maxDepth)/2)));
    axis image; title("Output Image"); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 3);
    imagesc(referenceMatrix(minRow:maxRow, minCol:maxCol, round((minDepth + maxDepth)/2)));
    axis image; title("Reference Image"); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 4);
    imagesc(newMatrix(minRow:maxRow, minCol:maxCol, round((minDepth + maxDepth)/2)) - referenceMatrix(minRow:maxRow, minCol:maxCol, round((minDepth + maxDepth)/2)));
    axis image; title('Difference Image - Z-axis'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 5);
    imagesc(squeeze(newMatrix(round((minRow + maxRow)/2), minCol:maxCol, minDepth:maxDepth) - referenceMatrix(round((minRow + maxRow)/2), minCol:maxCol, minDepth:maxDepth)));
    axis image; title('Difference Image - X-axis'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 6);
    imagesc(squeeze(newMatrix(minRow:maxRow, round((minCol + maxCol)/2), minDepth:maxDepth) - referenceMatrix(minRow:maxRow, round((minCol + maxCol)/2), minDepth:maxDepth)));
    axis image; title('Difference Image - Y-axis'); set(gca, "Fontsize", 20);
else
    % Plot the entire images without cropping
    figure;
    subplot(2, 3, 1);
    imagesc(originalMatrix(:, :, end/2));
    axis image; title('Input Image'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 2);
    imagesc(newMatrix(:, :, end/2));
    axis image; title('Output Image'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 3);
    imagesc(referenceMatrix(:, :, end/2));
    axis image; title('Reference Image'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 4);
    imagesc(newMatrix(:, :, end/2) - referenceMatrix(:, :, end/2));
    axis image; title('Difference Image - Z-axis'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 5);
    imagesc(squeeze(newMatrix(end/2, :, :) - referenceMatrix(end/2, :, :)));
    axis image; title('Difference Image - X-axis'); set(gca, "Fontsize", 20);
    
    subplot(2, 3, 6);
    imagesc(squeeze(newMatrix(:, end/2, :) - referenceMatrix(:, end/2, :)));
    axis image; title('Difference Image - Y-axis'); set(gca, "Fontsize", 20);
end

%% Evaluate the result
% Calculate the degree of complexity and differences between the matrices.
DoC = DegreeOfComplexity(originalMatrix);
DifferenceMatrix = abs(referenceMatrix - single(newMatrix > 0));

% Compute and display the grades based on complexity and volume.
Diff = sum(DifferenceMatrix, "all");
DoCgrade = Diff * DoC ^ 3;
fprintf('Grade by Degree of Complexity: %d\n', DoCgrade);

Volumegrade = Diff / sum(referenceMatrix, "all");
fprintf('Grade by Volume: %d\n', Volumegrade);

% Calculate the difference matrix between the new matrix and the full matrix.
DiffMatrix = newMatrix - fullMatrix;
