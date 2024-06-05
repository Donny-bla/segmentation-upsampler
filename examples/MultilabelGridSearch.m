%% Create some data
clear all;

% Low resolution parameters
N = 60; % Grid size in X and Y directions
radius = round(N / 3); % Radius of the shape
% Generate a complex multi-label shape using the makeShapes function
originalMatrix = makeShapes("MultiLabel", [radius], [N, N, 80], [0, 0, 0]);

%% Set Upsample Setting
dx = 0.3; % Grid spacing for upsampling

% Define ranges for sigma (smoothing factor) and isovalue (threshold)
sigma = 0.6:0.025:1.1; % Range of sigma values
isovalue = 0.44:0.0035:0.51; % Range of isovalue values
% Other parameter setting used in test
% sigma = 0.6:0.04:1.4;
% Volume = -0.3:0.03:0.3;
% Volume = -0.5:0.1:0.5;
% isovalue = 0.4:0.02:0.6;
% sigma = 0.6:0.02:1;
%% Create reference data
% Define parameters for reference data rasterization
Nref = floor(N / dx); % Grid size for reference data in X and Y directions
radiusRef = radius / dx; % Scaled radius for the reference shape

% Generate the reference and full shapes using the makeShapes function
referenceMatrix = makeShapes("MultiLabel", [radiusRef], [Nref, Nref, floor(80 / dx)], [0, 0, 0]);
fullMatrix = makeShapes("Ball", [radiusRef - 2], [Nref, Nref, floor(80 / dx)], [0, 0, 0]);

%% Initialize arrays to store grades
AllDiff = []; % Array to store volume differences
AllGaps = []; % Array to store gaps in the full matrix

% Loop through each sigma value
for s = sigma    
    Volumegrade = []; % Initialize array to store volume grades for each sigma
    Gapsgrade = []; % Initialize array to store gap grades for each sigma
    
    % Loop through each isovalue
    for iso = isovalue
        disp(s) % Display the current sigma value

        % Initialize Python environment
        pyenv;
        
        % Upsample the original shape using the pyrunfile function
        newMatrix = pyrunfile("UpsampleMultiLabels.py", "newMatrix", ...
                              multiLabelMatrix = py.numpy.array(originalMatrix), ...
                              sigma = s, targetVolume = 0.22, ...
                              scale = dx, iso = iso);
        newMatrix = double(newMatrix);

        % Calculate the difference between the new and reference matrices
        DifferenceMatrix = referenceMatrix ~= newMatrix;
        Diff = sum(DifferenceMatrix, "all"); % Sum of differences
    
        % Compute grades based on volume differences and gaps
        Volumegrade(end+1) = Diff / sum(referenceMatrix > 0, "all");
        Gapsgrade(end+1) = sum(newMatrix(fullMatrix == 1) == 0);
    end

    % Store grades for the current sigma value
    AllGaps = [AllGaps; Gapsgrade];
    AllDiff = [AllDiff; Volumegrade];
end

%% Plotting
figure

% Plot the number of gaps
subplot(1, 2, 1)
colormap(subplot(1, 2, 1), 'hot'); % Set colormap to 'hot'
cb = colorbar(); % Add colorbar
cb.Label.String = 'Number of Gaps'; % Label for colorbar
cb.FontSize = 14; % Font size for colorbar label
hold on
imagesc(isovalue, sigma, AllGaps) % Display gap grades as an image
contour(isovalue, sigma, AllGaps, [0 500], 'LineWidth', 2, 'Color', 'green', 'LineStyle', '--'); % Add contour for 500 gaps
contour(isovalue, sigma, AllDiff, [0 0.04], 'LineWidth', 2, 'Color', 'blue', 'LineStyle', '--'); % Add contour for volume grade 0.04
hold off
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)
legend("500 Gaps", "Volume Grade 0.04", 'FontSize', 14)

% Plot the volume grade
subplot(1, 2, 2)
colormap(subplot(1, 2, 2), 'hot'); % Set colormap to 'hot'
cb = colorbar(); % Add colorbar
cb.Label.String = 'Grade by Volume'; % Label for colorbar
cb.FontSize = 14; % Font size for colorbar label
hold on
imagesc(isovalue, sigma, AllDiff) % Display volume grades as an image
contour(isovalue, sigma, AllDiff, [0 0.04], 'LineWidth', 2, 'Color', 'blue', 'LineStyle', '--'); % Add contour for volume grade 0.04
hold off
set(gca, 'FontSize', 14);
title("Multi-label Dense Scan of Sigma and Isovalue", 'FontSize', 20)
xlabel("Isovalue", 'FontSize', 20)
ylabel("Sigma", 'FontSize', 20)
legend("0.04", 'FontSize', 14)
