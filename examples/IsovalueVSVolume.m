% Investigate the effect of volume ratio in selecting isovalue
%% Generate an original 3D shape matrix with complex structure
originalMatrix = makeShapes("Complex", [20], [60,60,60], [0,0,0]);

% Calculate the volume of the original shape
originalVolume = sum(originalMatrix > 0, "all");

% Apply Gaussian smoothing with different sigma values
smoothMatrix0p7 = imgaussfilt3(originalMatrix, 0.7);
smoothMatrix1p5 = imgaussfilt3(originalMatrix, 1.5);

%% Initialize variables for volume ratios
v_0p7 = []; % Volume ratios for sigma = 0.7
v_1p5 = []; % Volume ratios for sigma = 1.5
iso = 0:0.0001:1; % Range of isovalues to investigate

% Loop through each isovalue
for ii = iso
    % Calculate the volume of smoothed shapes above the current isovalue
    smoothedVolume0p7 = sum(smoothMatrix0p7 > ii, "all");
    smoothedVolume1p5 = sum(smoothMatrix1p5 > ii, "all");
    
    % Compute the volume ratio for sigma = 0.7
    t = -1;
    if smoothedVolume0p7 < originalVolume
        t = 1;
    end
    v_0p7(end+1) = t / log(abs(smoothedVolume0p7 - originalVolume) / originalVolume);

    % Compute the volume ratio for sigma = 1.5
    t = -1;
    if smoothedVolume1p5 < originalVolume
        t = 1;
    end
    v_1p5(end+1) = t / log(abs(smoothedVolume1p5 - originalVolume) / originalVolume);
end

% Plot the results
hold on
plot(iso, v_0p7) % Plot volume ratios for sigma = 0.7
plot(iso, v_1p5) % Plot volume ratios for sigma = 1.5

% Set plot limits and labels
ylim([-2 2])
xlim([0 1])
grid on
ylabel("Volume ratio")
legend("sigma = 0.7", "sigma = 1.5")
xlabel("isovalue")
set(gca, "Fontsize", 20)
hold off
