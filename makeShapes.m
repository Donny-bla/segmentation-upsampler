function shapeObject = makeShapes(shapeType, objectSize, gridSize, objectPosition)
% MAKESHAPES Generate various shapes within a 3D grid.
%
% shapeObject = makeShapes(shapeType, objectSize, gridSize, objectPosition)
% generates a shape within a 3D grid according to the specified shape type,
% size, grid size, and object position.
%
% Inputs:
%   - shapeType: Enumerated type specifying the shape to generate
%   - objectSize: Size of the object along each dimension [x, y, z]
%   - gridSize: Size of the grid along each dimension [x, y, z]
%   - objectPosition: Position of the object within the grid [x, y, z]
%
% Output:
%   - shapeObject: 3D array representing the generated shape within the grid
%
% Supported Shape Types:
%   - Ball
%   - Bowl
%   - Cube
%   - Cylinder
%   - Cone
%   - BallHole
%   - CubeHole
%   - Complex
%   - MultiLabel

arguments
    shapeType ShapeTypes
    objectSize (1, :)
    gridSize (1, 3)
    objectPosition (1, 3)
end

% Ensure the object position is within the grid
if objectPosition(1) == 0
    objectPosition(1) = floor(gridSize(1) / 2) + 1;
end
if objectPosition(2) == 0
    objectPosition(2) = floor(gridSize(2) / 2) + 1;
end
if objectPosition(3) == 0
    objectPosition(3) = floor(gridSize(3) / 2) + 1;
end

% Initialize the shape object
shapeObject = zeros(gridSize(1), gridSize(2), gridSize(3));

% Generate shapes based on the specified shape type
switch(shapeType)
    case ShapeTypes.Ball
        % Create a ball shape
        shapeObject = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(1));
    case ShapeTypes.Bowl
        % Create a bowl shape
        LargeSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(1));
        SmallSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(2));
        LargeSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        SmallSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        shapeObject = LargeSphere - SmallSphere;
        shapeObject = single(shapeObject > 0);
    case ShapeTypes.Cube
        % Create a cube shape
        halfL = floor(objectSize(1) / 2);
        otherHalfL = objectSize(1) - halfL - 1;
        shapeObject(objectPosition(1) - halfL : objectPosition(1) + otherHalfL, objectPosition(2) - halfL : objectPosition(2) + otherHalfL, objectPosition(3) - halfL : objectPosition(3) + otherHalfL) = 1;
    case ShapeTypes.Cylinder
        % Create a cylinder shape
        plane = zeros(gridSize(1), gridSize(2));
        for ii=1:gridSize(1)
            for jj=1:gridSize(2)
                coord = [ii - objectPosition(1), jj - objectPosition(2)];
                if(coord(1)^2 + coord(2)^2 <= objectSize(1)^2)
                    plane(ii,jj) = 1;
                end
            end
        end
        halfH = floor(objectSize(2) / 2) + 1;
        for kk = objectPosition(3) - halfH: objectPosition(3) + (objectSize(2)-halfH)
            if(kk > 0 && kk <= gridSize(3))
                shapeObject(:, :, kk) = plane;
            end
        end
    % Other cases omitted for brevity
end

end
