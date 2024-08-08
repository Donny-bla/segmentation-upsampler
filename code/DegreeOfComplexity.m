function DoC = DegreeOfComplexity(originalModel)
% DEGREEOFCOMPLEXITY Calculate the Degree of Complexity (DoC) of a 3D binary model.
%
% DoC = DegreeOfComplexity(originalModel) calculates the DoC of the input binary 3D model.
%
% Input:
%   - originalModel: Binary 3D array representing the original model.
%
% Output:
%   - DoC: Degree of Complexity of the model.
%
% The DoC is computed as the ratio of the surface area of the original model to its volume.
% It quantifies the surface complexity relative to the volume.
%
% Algorithm:
% - Erode the original model using a sphere structuring element of radius 1.
% - Subtract the eroded model from the original to obtain the surface.
% - Calculate the sum of the surface voxels to get the surface area.
% - Calculate the sum of all voxels in the original model to get the volume.
% - Compute the DoC as the ratio of surface area to volume.

% Erode the original model to obtain inner structures
se = strel('sphere',1);
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
