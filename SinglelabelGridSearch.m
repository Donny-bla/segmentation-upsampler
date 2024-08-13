%% Create some data
clear all;

% Set low resolution parameters
N = 60; % Grid size
radius = round(N / 3); % Radius for the shape
% Generate a complex shape using the makeShapes function
originalMatrix = makeShapes("Complex", [radius], [N, N, N], [0, 0, 0]);

filePath = matlab.desktop.editor.getActiveFilename;
idx = strfind(filePath, '\');
folderPath = filePath(1:idx(end));
codeDirect = folderPath + "code";
addpath(codeDirect)
%% Set Upsample Setting
% Define upsampling parameters
dx = 0.25; % Grid spacing for upsampling

% Define ranges for sigma (smoothing factor) and isovalue (threshold)
sigma = 0.6:0.02:1; % Range of sigma values
isovalue = 0.47:0.003:0.53; % Range of isovalue values

% Other parameter setting used in test
% sigma = 0.6:0.04:1.4;
% Volume = -0.3:0.03:0.3;
% sigma = 0:0.2:2;
% Volume = -0.5:0.1:0.5;
% isovalue = 0.4:0.02:0.6;
%% Create reference data
% Define parameters for reference data rasterization
Nref = floor(N / dx); % Grid size for reference data
fac = 1 / dx; % Upscaling factor
radiusRef = radius / dx; % Scaled radius for the reference shape

% Generate the reference shape using the makeShapes function
referenceMatrix = makeShapes("Complex", [radiusRef], [Nref, Nref, Nref], [0, 0, 0]);

%% Initialize arrays to store grades
AllVolumegrade = []; % Array to store volume grades
AllDoCdxgrade = []; % Array to store Degree of Complexity (DoC) grades

% Calculate Degree of Complexity for the original shape
DoC = DegreeOfComplexity(originalMatrix);

% Loop through each sigma value
for s = sigma    
    Volumegrade = []; % Initialize array to store volume grades for each sigma
    DoCdxgrade = []; % Initialize array to store DoC grades for each sigma
    
    % Loop through each isovalue
    for iso = isovalue
        disp(s) % Display the current sigma value
        
        % Upsample the original shape using the pyUpsampleLabel function
        newMatrix = pyrunfile(codeDirect + "\UpsampleMultiLabels.py", ...
                              "newMatrix", ...
                              multiLabelMatrix = py.numpy.array(originalMatrix), ...
                              sigma = s, ...
                              targetVolume = 0, ...
                              scale = [dx, dx, dx], ...
                              spacing = [1 1 1], ...
                              iso = iso, ...
                              fillGaps = false, ...
                              NB = true);
        
        % Calculate the difference between the new and reference matrices
        DifferenceMatrix = newMatrix - referenceMatrix;
        Diff = sum(abs(DifferenceMatrix), "all"); % Sum of absolute differences
    
        % Compute grades based on volume differences and DoC
        Volumegrade(end+1) = Diff / sum(referenceMatrix, "all");
        DoCdxgrade(end+1) = Diff * (DoC * dx)^3;
    end

    % Store grades for the current sigma value
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% Plotting
% Create figure for plotting the results
figure

% Plot grades by Degree of Complexity (DoC)
subplot(1, 2, 1)
hold on
imagesc(isovalue, sigma, AllDoCdxgrade) % Display DoC grades as an image
hold off
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)

% Plot grades by volume
subplot(1, 2, 2)
colormap(subplot(1, 2, 2), 'hot'); % Set colormap to 'hot' for the second subplot
cb = colorbar();
cb.Label.String = 'Grade by Volume';
cb.FontSize = 14;
hold on
imagesc(isovalue, sigma, AllVolumegrade) % Display volume grades as an image
contour(isovalue, sigma, AllVolumegrade, [0 0.04], 'LineWidth', 2, 'Color', 'blue', 'LineStyle', '--');
hold off
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)
legend("0.04", "FontSize", 14)
