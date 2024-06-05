%% Create some data
clear all;

N = 60;
radius = round(N / 3);

% Generate a complex shape using the makeShapes function
shapes = cell(1);
shapes{1} = makeShapes("Complex", [radius], [N, N, N], [0, 0, 0]);
originalMatrix = shapes{1};

%% Set Upsample Setting
pyenv;
% Define parameters for upsampling
sigma = 0.68;
Volume = 0.22;
isovalue = 0.513;

% Define range of upsampling scales
dx = [0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95];
%% Initialize arrays to store grades
AllVolumegrade = [];
AllDoCdxgrade = [];

% Loop through each method (3 methods in total)
for s = 1:3
    % Calculate Degree of Complexity (DoC) for the original shape
    DoC = DegreeOfComplexity(originalMatrix);
    
    % Initialize arrays to store grades for each scale
    Volumegrade = [];
    DoCdxgrade = [];
    
    % Loop through each upsampling scale
    for ii = dx
        disp(ii)  % Display the current scale
        
        % Create reference data for the current scale
        Nref = floor(double(N / ii));
        radiusRef = floor(radius / ii);
        referenceMatrix = makeShapes("Complex", [radiusRef], [Nref, Nref, Nref], [0, 0, 0]);
        
        % Upsample the original shape using different methods
        switch s
            case 1
                % Method 1: Upsample using Python script
                newMatrix = pyrunfile("UpsampleMultiLabels.py", "newMatrix", ...
                    multiLabelMatrix = py.numpy.array(originalMatrix), ...
                    sigma = sigma, targetVolume = Volume, scale = ii, iso = isovalue);
                newMatrix = single(newMatrix);
            case 2
                % Method 2: Upsample using trilinear interpolation
                newMatrix = trinterp(originalMatrix, ii);
                newMatrix = single(newMatrix > 0);
            case 3
                % Method 3: Upsample using nearest neighbor interpolation
                newMatrix = nearestn(originalMatrix, ii);
                newMatrix = single(newMatrix > 0);
        end

        % Calculate the difference between the reference and upsampled shapes
        DifferenceMatrix = referenceMatrix ~= newMatrix;
        Diff = sum(DifferenceMatrix, "all");
        
        % Compute grades based on volume differences and Degree of Complexity
        Volumegrade(end+1) = Diff / sum(referenceMatrix > 0, "all");
        DoCdxgrade(end+1) = Diff * (DoC * ii) ^ 3;
    end

    % Store grades for the current method
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% Plotting
figure

% Plot grades by shape
subplot(1, 2, 1)
hold on
plot(dx, AllDoCdxgrade)
hold off
set(gca, "Fontsize", 14)
title("Grade by Shape", "Fontsize", 20)
xlim([0.2, 0.95])
xlabel("dx", "Fontsize", 20)
ylabel("Grade", "Fontsize", 20)
legend("MeshBased", "Trinterp", "NearestN", "Fontsize", 18)

% Plot grades by volume
subplot(1, 2, 2)
hold on
plot(dx, AllVolumegrade)
hold off
set(gca, "Fontsize", 14)
title("Grade by Volume", "Fontsize", 20)
xlim([0.2, 0.95])
xlabel("dx", "Fontsize", 20)
ylabel("Grade", "Fontsize", 20)
legend("MeshBased", "Trinterp", "NearestN", "Fontsize", 18)
