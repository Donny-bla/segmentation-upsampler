function DoC = DegreeOfComplexity(originalModel)
% DEGREEOFCOMPLEXITY Calculate the Degree of Complexity (DoC) of a 3D 
% binary model.
%
% DESCRIPTION:
%     DoC = DegreeOfComplexity(originalModel) calculates the Degree 
%     of Complexity (DoC) of the input binary 3D model. The DoC is 
%     computed as the ratio of the surface area of the original model 
%     to its volume. It quantifies the surface complexity relative to 
%     the volume.
%
% USAGE:
%     DoC = DegreeOfComplexity(originalModel);
%
% INPUT:
%     originalModel - Binary 3D array representing the original model.
%
% OUTPUT:
%     DoC           - Degree of Complexity of the model.
%
% ABOUT:
%     author        - Liangpu Liu
%     date          - 25th Aug 2024
%     last update   - 25th Aug 2024
%
% See also: strel, imerode

    % Erode the original model to obtain inner structures
    se = strel('sphere', 1);
    erodedModel = imerode(originalModel, se);

    % Extract the surface by subtracting the eroded model from the original
    modelSurface = originalModel - erodedModel;

    % Calculate the sum of surface voxels to get surface area
    Surface = sum(modelSurface, 'all');

    % Calculate the sum of all voxels in the original model to get volume
    Volume = sum(originalModel, 'all');

    % Compute the DoC as the ratio of surface area to volume
    DoC = Surface / Volume;

end
