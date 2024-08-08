%% Create some data
clear all;

% Generate different 3D shapes using the makeShapes function
shapes = cell(1, 5);
shapes{1} = makeShapes("BallHole", [10, round(10/3)], [30,30,30], [0, 0, 0]);
shapes{2} = makeShapes("Bowl", [18, round(18/2)], [40,40,40], [0, 0, 0]);
shapes{3} = makeShapes("Cylinder", [15, 30], [35,35,35], [0, 0, 0]);
shapes{4} = makeShapes("Ball", [20], [45,45,45], [0, 0, 0]);

% Initialize cell array to store reference shapes
referenceShapes = cell(1, 4);

filePath = matlab.desktop.editor.getActiveFilename;
idx = strfind(filePath, '\');
folderPath = filePath(1:idx(end));
codeDirect = folderPath + "code";
addpath(codeDirect)
%% Set Upsample Setting
% Define upsampling parameters
Volume = 0;
sigma = 0.6;
isovalue = 0.44;
% Apply the range of upsampling scales for comparsion
dx = 0.2:0.1:1;
pyenv;

%% Initialize arrays to store grades
AllVolumegrade = [];
AllDoCdxgrade = [];

% Loop through each shape
for s = 1:4
    % Get the original shape matrix and calculate its Degree of Complexity (DoC)
    originalMatrix = shapes{s};
    DoC = DegreeOfComplexity(originalMatrix);
    
    % Initialize arrays to store grades for each scale
    Volumegrade = [];
    DoCdxgrade = [];
    
    % Loop through each upsampling scale
    for ii = dx
        % Generate reference shapes for the current scale
        referenceShapes{1} = makeShapes("BallHole", [floor(10/ii), floor(10/3/ii)], [floor(30/ii),floor(30/ii),floor(30/ii)], [0, 0, 0]);
        referenceShapes{2} = makeShapes("Bowl", [floor(18/ii), floor(18/2/ii)], [floor(40/ii),floor(40/ii),floor(40/ii)], [0, 0, 0]);
        referenceShapes{3} = makeShapes("Cylinder", [floor(15/ii), floor(30/ii)], [floor(35/ii),floor(35/ii),floor(35/ii)], [0, 0, 0]);
        referenceShapes{4} = makeShapes("Ball", [floor(20/ii)], [floor(45/ii),floor(45/ii),floor(45/ii)], [0, 0, 0]);
        referenceMatrix = referenceShapes{s};
        
        % Display the current scale
        disp(ii)
        
        %Upsample the original shape using a Python script
        newMatrix = pyrunfile(codeDirect + "\UpsampleMultiLabels.py", ...
                              "newMatrix", ...
                              multiLabelMatrix = py.numpy.array(originalMatrix), ...
                              sigma = s, ...
                              targetVolume = Volume, ...
                              scale = [ii, ii, ii], ...
                              spacing = [1 1 1], ...
                              iso = isovalue, ...
                              fillGaps = false, ...
                              NB = true);
        
        % Convert the new matrix to double for processing
        newMatrix = double(newMatrix);
        
        % Calculate the difference between the reference and upsampled shapes
        DifferenceMatrix = abs(referenceMatrix - single(newMatrix > 0));
        Diff = sum(DifferenceMatrix, "all");
        
        % Compute grades based on Degree of Complexity and volume differences
        Volumegrade(end+1) = Diff / sum(referenceMatrix, "all");
        DoCdxgrade(end+1) = Diff * (DoC * ii) ^ 3;
    end
    
    % Store grades for the current shape
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end

%% Plotting
% Plot the grades by shape
figure
subplot(1,2,1)
hold on
plot(dx(1:end-1), AllDoCdxgrade(:,1:end-1))
hold off
set(gca, 'FontSize', 20);
title("Grade by Shape")
xlabel("Scale of Upsampling")
ylabel("Grade")
xlim([0.2,0.9])
legend("SphereHole", "Bowl", "Cylinder", "Sphere")

% Plot the grades by volume
subplot(1,2,2)
hold on
plot(dx(1:end-1), AllVolumegrade(:,1:end-1))
hold off
set(gca, 'FontSize', 20);
title("Grade by Volume")
xlabel("Scale of Upsampling")
ylabel("Grade")
xlim([0.2,0.9])
legend("SphereHole", "Bowl", "Cylinder", "Sphere")
