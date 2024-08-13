function upsampledMatrix = nearestn(originalMatrix, dx)

    [x,y,z] = size(originalMatrix);
    [X,Y,Z] = meshgrid(0:1:x-1, 0:1:y-1, 0:1:z-1);
    [Xq, Yq, Zq] = meshgrid(0:dx:x-dx, 0:dx:y-dx, 0:dx:z-dx);
    
    % Interpolate using linear method
    upsampledMatrix = interp3(X, Y, Z, originalMatrix, Xq, Yq, Zq, "nearest");
    upsampledMatrix = single(upsampledMatrix);
end
