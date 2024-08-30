filePath = matlab.desktop.editor.getActiveFilename;
idx = strfind(filePath, '\');
folderPath = filePath(1:idx(end));
codeDirect = folderPath + "code";
addpath(codeDirect)

%% Create some data
clear all;
% Low resolution.
N = 60;
radius = round(N/3);
shapes = makeShapes("Complex", [radius], [N,N,N], [0, 0, 0]);

%% Set Upsample Setting
sigma = 0.68;
Volume = 0;
isovalue = 0.513;
dx = [0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95];

pyenv;
%%
AllDoCgrade = [];
AllVolumegrade = [];
AllDoCdxgrade = [];
originalMatrix = shapes{1};
for s = 1:3
    DoC = DegreeOfComplexity(originalMatrix);
    
    DoCgrade = [];
    Volumegrade = [];
    DoCdxgrade = [];
    
    for ii = dx
        % Create reference data
        Nref = floor(double(N / ii));
        radiusRef = floor(radius / ii);
        referenceMatrix = makeShapes("Complex", [radiusRef], [Nref,Nref,Nref], [0, 0, 0]);
        switch(s)
            case 1
                %newMatrix = pyrunfile("UpsampleMultiLabels.py","newMatrix", multiLabelMatrix = py.numpy.array(originalMatrix), sigma = sigma, targetVolume = Volume, scale = ii, iso = isovalue);
                newMatrix = pyrunfile(codeDirect + "\UpsampleMultiLabels.py", ...
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
            case 2
                newMatrix = trinterp(originalMatrix, ii);
                newMatrix = single(newMatrix>0);
            case 3
                newMatrix = nearestn(originalMatrix, ii);
                newMatrix = single(newMatrix>0);
        end

        DifferenceMatrix = referenceMatrix ~= newMatrix;
        Diff = sum(DifferenceMatrix,"all");
        Volumegrade(end+1) = Diff / sum(referenceMatrix>0,"all");
        DoCgrade(end+1) = Diff * DoC ^ 3;
        DoCdxgrade(end+1) = Diff * (DoC*ii)^3;
    end

    AllDoCgrade = [AllDoCgrade; DoCgrade];
    AllDoCdxgrade = [AllDoCdxgrade; DoCdxgrade];
    AllVolumegrade = [AllVolumegrade; Volumegrade];
end
%% Plotting
figure
subplot(1,2,1)
hold on
plot(dx, AllDoCdxgrade)
% plot(dx,AllDoCdxgrade,"*")
hold off
set(gca,"Fontsize",14)
title("grade by shape","Fontsize",20)
xlim([0.2, 0.95])
xlabel("dx","Fontsize",20)
ylabel("grade","Fontsize",20)
legend("MeshBased","Trinterp", "NearestN","Fontsize",18)

subplot(1,2,2)
hold on
plot(dx, AllVolumegrade)
%plot(dx,AllVolumegrade,"*")
hold off
set(gca,"Fontsize",14)
title("grade by volume","Fontsize",20)
xlim([0.2, 0.95])
xlabel("dx","Fontsize",20)
ylabel("grade","Fontsize",20)
legend("MeshBased","Trinterp", "NearestN","Fontsize",18)
