function shapeObject = makeShapes(shapeType, objectSize, gridSize, ...
                                  objectPosition)
% MAKESHAPES Generate various shapes within a 3D grid.
%
% DESCRIPTION:
%     MAKESHAPES generates a specified shape within a 3D grid based on
%     the given shape type, object size, grid size, and object position.
%     This function supports generating various geometric shapes, such
%     as spheres, cubes, cylinders, cones, and complex multi-label shapes.
%
% USAGE:
%     shapeObject = makeShapes(shapeType, objectSize, gridSize, ...
%                              objectPosition);
%
% INPUTS:
%     shapeType      - Enumerated type specifying the shape to generate
%     objectSize     - Size of the object along each dimension [x, y, z]
%     gridSize       - Size of the grid along each dimension [x, y, z]
%     objectPosition - Position of the object within the grid [x, y, z]
%
% OUTPUTS:
%     shapeObject    - 3D array representing the generated shape within 
%                      the grid
%
% SUPPORTED SHAPE TYPES:
%     - Ball
%     - Bowl
%     - Cube
%     - Cylinder
%     - Cone
%     - BallHole
%     - CubeHole
%     - Complex
%     - MultiLabel
%
% ABOUT:
%     author         - Your Name
%     date           - 25th Aug 2024
%     last update    - 25th Aug 2024
%
% See also: makeBall, makeShapes
%
% LICENSE:
%     This function is part of the k-Wave Toolbox (http://www.k-wave.org).
%     Copyright (C) 2009-2013 Author Name and Author Name.
%
%     This file is part of k-Wave. k-Wave is free software: you can
%     redistribute it and/or modify it under the terms of the GNU Lesser
%     General Public License as published by the Free Software Foundation,
%     either version 3 of the License, or (at your option) any later
%     version.
%
%     k-Wave is distributed in the hope that it will be useful, but 
%     WITHOUT ANY WARRANTY; without even the implied warranty of
%     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
%     GNU Lesser General Public License for more details.
%
%     You should have received a copy of the GNU Lesser General Public 
%     License along with k-Wave. If not, see <http://www.gnu.org/licenses/>.

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
        shapeObject = makeBall(gridSize(1), gridSize(2), gridSize(3), ...
                               objectPosition(1), objectPosition(2), ...
                               objectPosition(3), objectSize(1));
    case ShapeTypes.Bowl
        % Create a bowl shape
        LargeSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), ...
                               objectPosition(1), objectPosition(2), ...
                               objectPosition(3), objectSize(1));
        SmallSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), ...
                               objectPosition(1), objectPosition(2), ...
                               objectPosition(3), objectSize(2));
        LargeSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        SmallSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        shapeObject = LargeSphere - SmallSphere;
        shapeObject = single(shapeObject > 0);
    case ShapeTypes.Cube
        % Create a cube shape
        halfL = floor(objectSize(1) / 2);
        otherHalfL = objectSize(1) - halfL - 1;
        shapeObject(objectPosition(1) - halfL : objectPosition(1) + ...
                    otherHalfL, objectPosition(2) - halfL : ...
                    objectPosition(2) + otherHalfL, ...
                    objectPosition(3) - halfL : ...
                    objectPosition(3) + otherHalfL) = 1;
    case ShapeTypes.Cylinder
        % Create a cylinder shape
        plane = zeros(gridSize(1), gridSize(2));
        for ii = 1:gridSize(1)
            for jj = 1:gridSize(2)
                coord = [ii - objectPosition(1), jj - objectPosition(2)];
                if(coord(1)^2 + coord(2)^2 <= objectSize(1)^2)
                    plane(ii, jj) = 1;
                end
            end
        end
        halfH = floor(objectSize(2) / 2) + 1;
        for kk = objectPosition(3) - halfH : ...
                objectPosition(3) + (objectSize(2) - halfH)
            if(kk > 0 && kk <= gridSize(3))
                shapeObject(:, :, kk) = plane;
            end
        end
    case ShapeTypes.Cone
        halfH = floor(objectSize(2) / 2) + 1;
        for kk = objectPosition(3) - halfH : ...
                objectPosition(3) + (objectSize(2) - halfH)
            if(kk < 0 || kk > gridSize(3))
                continue;
            end
            plane = zeros(gridSize(1), gridSize(2));
            r = objectSize(1) - floor(objectSize(1) / objectSize(2) * ...
                (kk - (objectPosition(3) - halfH)));
            for ii = 1:gridSize(1)
                for jj = 1:gridSize(2)
                    coord = [ii - objectPosition(1), jj - ...
                             objectPosition(2)];
                    if(coord(1)^2 + coord(2)^2 <= r^2)
                        plane(ii, jj) = 1;
                    end
                end
            end            
            shapeObject(:, :, kk) = plane;
        end
    case ShapeTypes.BallHole
        hole = makeShapes(ShapeTypes.Cylinder, [objectSize(2), ...
                    gridSize(3)], gridSize, objectPosition);
        shapeObject = makeShapes(ShapeTypes.Ball, [objectSize(1)], ...
                                 gridSize, objectPosition) - hole;
        shapeObject = single(shapeObject > 0);
    case ShapeTypes.CubeHole
        hole = makeShapes(ShapeTypes.Cylinder, [objectSize(2), ...
                    gridSize(3)], gridSize, objectPosition);
        shapeObject = makeShapes(ShapeTypes.Cube, [objectSize(1)], ...
                                 gridSize, objectPosition) - hole;
        shapeObject = single(shapeObject > 0);
    case ShapeTypes.Complex
        base = makeBall(gridSize(1), gridSize(2), gridSize(3), ...
                        objectPosition(1), objectPosition(2), ...
                        objectPosition(3), objectSize(1));
        shapeObject = base - makeBall(gridSize(1), gridSize(2), ...
                                      gridSize(3), objectPosition(1), ...
                                      objectPosition(2) - ...
                                      objectSize(1), ...
                                      objectPosition(3), ...
                                      floor(objectSize(1)/2));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), ...
                                             gridSize(3), ...
                                             objectPosition(1), ...
                                             objectPosition(2) + ...
                                             objectSize(1), ...
                                             objectPosition(3), ...
                                             floor(objectSize(1)/3));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), ...
                                             gridSize(3), ...
                                             objectPosition(1) - ...
                                             objectSize(1), ...
                                             objectPosition(2), ...
                                             objectPosition(3), ...
                                             floor(objectSize(1)/4));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), ...
                                             gridSize(3), ...
                                             objectPosition(1) + ...
                                             objectSize(1), ...
                                             objectPosition(2), ...
                                             objectPosition(3), ...
                                             floor(objectSize(1)/5));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), ...
                                             gridSize(3), ...
                                             objectPosition(1), ...
                                             objectPosition(2), ...
                                             objectPosition(3) - ...
                                             objectSize(1), ...
                                             floor(objectSize(1)*2/3));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), ...
                                             gridSize(3), ...
                                             objectPosition(1), ...
                                             objectPosition(2), ...
                                             objectPosition(3) + ...
                                             objectSize(1), ...
                                             floor(objectSize(1)*3/4));
        shapeObject = single(shapeObject > 0);
    case ShapeTypes.MultiLabel
        base = makeShapes(ShapeTypes.Complex, objectSize, gridSize, ...
                          objectPosition);
        shapeObject = base + 2 * makeBall(gridSize(1), gridSize(2), ...
                                          gridSize(3), objectPosition(1), ...
                                          objectPosition(2) - ...
                                          objectSize(1), ...
                                          objectPosition(3), ...
                                          floor(objectSize(1)/2));
        shapeObject = shapeObject + 3 * makeBall(gridSize(1), ...
                                                 gridSize(2), ...
                                                 gridSize(3), ...
                                                 objectPosition(1), ...
                                                 objectPosition(2) + ...
                                                 objectSize(1), ...
                                                 objectPosition(3), ...
                                                 floor(objectSize(1)/3));
        shapeObject = shapeObject + 4 * makeBall(gridSize(1), ...
                                                 gridSize(2), ...
                                                 gridSize(3), ...
                                                 objectPosition(1) - ...
                                                 objectSize(1), ...
                                                 objectPosition(2), ...
                                                 objectPosition(3), ...
                                                 floor(objectSize(1)/4));
        shapeObject = shapeObject + 5 * makeBall(gridSize(1), ...
                                                 gridSize(2), ...
                                                 gridSize(3), ...
                                                 objectPosition(1) + ...
                                                 objectSize(1), ...
                                                 objectPosition(2), ...
                                                 objectPosition(3), ...
                                                 floor(objectSize(1)/5));
        shapeObject = shapeObject + 6 * makeBall(gridSize(1), ...
                                                 gridSize(2), ...
                                                 gridSize(3), ...
                                                 objectPosition(1), ...
                                                 objectPosition(2), ...
                                                 objectPosition(3) - ...
                                                 objectSize(1), ...
                                                 floor(objectSize(1)*2/3));
        shapeObject = shapeObject + 7 * makeBall(gridSize(1), ...
                                                 gridSize(2), ...
                                                 gridSize(3), ...
                                                 objectPosition(1), ...
                                                 objectPosition(2), ...
                                                 objectPosition(3) + ...
                                                 objectSize(1), ...
                                                 floor(objectSize(1)*3/4));
end
end
