function upsampledMatrix = trinterp(originalMatrix, dx)
% Conduct image upsampling through trilinear interpolation
%
% USAGE:
%     newMatrix = trinterp(originalMatrix, dx);
%
% INPUT:
%     originalModel - Binary 3D array representing the original model.
%     dx            - Scale of upsampling 
%
% OUTPUT:
%     newMatrix     - Upsampled image.
%
% ABOUT:
%     author        - Liangpu Liu
%     date          - 4th Sep 2024
%     last update   - 4th Sep 2024
%

    [y,x,z] = size(originalMatrix);
    [X,Y,Z] = meshgrid(0:1:x-1, 0:1:y-1, 0:1:z-1);
    [Xq, Yq, Zq] = meshgrid(0:dx:x-dx, 0:dx:y-dx, 0:dx:z-dx);
    
    % Interpolate using linear method
    upsampledMatrix = interp3(X, Y, Z, originalMatrix, Xq, Yq, Zq, 'linear');
    upsampledMatrix = single(upsampledMatrix);
end
