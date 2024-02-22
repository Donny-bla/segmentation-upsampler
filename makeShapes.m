function shapeObject = makeShapes(shapeType, objectSize, gridSize, objectPosition)
arguments
    shapeType ShapeTypes
    objectSize (1, :)
    gridSize (1, 3)
    objectPosition (1, 3)
end

if objectPosition(1) == 0
    objectPosition(1) = floor(gridSize(1) / 2) + 1;
end
if objectPosition(2) == 0
    objectPosition(2) = floor(gridSize(2) / 2) + 1;
end
if objectPosition(3) == 0
    objectPosition(3) = floor(gridSize(3) / 2) + 1;
end
shapeObject = zeros(gridSize(1),gridSize(2),gridSize(3));
switch(shapeType)
    case ShapeTypes.Ball
        shapeObject = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(1));
    case ShapeTypes.Bowl
        LargeSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(1));
        SmallSphere = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(2));
        LargeSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        SmallSphere(:, :, floor(gridSize(3)/2):gridSize(3)) = 0;
        shapeObject = LargeSphere - SmallSphere;
        shapeObject = single(shapeObject>0);
    case ShapeTypes.Cube
        halfL = floor(objectSize(1) / 2);
        otherHalfL = objectSize(1) - halfL - 1;

        shapeObject(objectPosition(1) - halfL : objectPosition(1) + otherHalfL,objectPosition(2) - halfL : objectPosition(2) + otherHalfL,objectPosition(3) - halfL : objectPosition(3) + otherHalfL) = 1;
    case ShapeTypes.Cylinder
        plane = zeros(gridSize(1),gridSize(2));
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
                shapeObject(: , : , kk) = plane;
            end
        end
    case ShapeTypes.Cone
        halfH = floor(objectSize(2) / 2) + 1;
        for kk = objectPosition(3) - halfH: objectPosition(3) + (objectSize(2)-halfH)
            if(kk < 0 || kk > gridSize(3))
                continue;
            end
            plane = zeros(gridSize(1),gridSize(2));
            r = objectSize(1) - floor(objectSize(1)/objectSize(2) * (kk- (objectPosition(3) - halfH)));
            for ii=1:gridSize(1)
                for jj=1:gridSize(2)
                    coord = [ii - objectPosition(1), jj - objectPosition(2)];
                    if(coord(1)^2 + coord(2)^2 <= r^2)
                        plane(ii,jj) = 1;
                    end
                end
            end            
            shapeObject(: , : , kk) = plane;
        end
    case ShapeTypes.BallHole
        hole = makeShapes("Cylinder", [objectSize(2),gridSize(3)], gridSize, objectPosition);
        shapeObject = makeShapes("Ball", [objectSize(1)], gridSize, objectPosition) - hole;
        shapeObject = single(shapeObject>0);
    case ShapeTypes.CubeHole
        hole = makeShapes("Cylinder", [objectSize(2),gridSize(3)], gridSize, objectPosition);
        shapeObject = makeShapes("Cube", [objectSize(1)], gridSize, objectPosition) - hole;
        shapeObject = single(shapeObject>0);
    case ShapeTypes.Complex
        base = makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3), objectSize(1));
        shapeObject = base - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2) - objectSize(1), objectPosition(3), floor(objectSize(1)/2));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2) + objectSize(1), objectPosition(3), floor(objectSize(1)/3));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1) - objectSize(1), objectPosition(2), objectPosition(3), floor(objectSize(1)/4));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1) + objectSize(1), objectPosition(2), objectPosition(3), floor(objectSize(1)/5));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3) - objectSize(1), floor(objectSize(1)*2/3));
        shapeObject = shapeObject - makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3) + objectSize(1), floor(objectSize(1)*3/4));
        shapeObject = single(shapeObject>0);
    case ShapeTypes.MultiLabel
        base = makeShapes("Complex", objectSize, gridSize, objectPosition);
        shapeObject = base + 2 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2) - objectSize(1), objectPosition(3), floor(objectSize(1)/2));
        shapeObject = shapeObject + 3 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2) + objectSize(1), objectPosition(3), floor(objectSize(1)/3));
        shapeObject = shapeObject + 4 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1) - objectSize(1), objectPosition(2), objectPosition(3), floor(objectSize(1)/4));
        shapeObject = shapeObject + 5 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1) + objectSize(1), objectPosition(2), objectPosition(3), floor(objectSize(1)/5));
        shapeObject = shapeObject + 6 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3) - objectSize(1), floor(objectSize(1)*2/3));
        shapeObject = shapeObject + 7 * makeBall(gridSize(1), gridSize(2), gridSize(3), objectPosition(1), objectPosition(2), objectPosition(3) + objectSize(1), floor(objectSize(1)*3/4));
        
end

end
