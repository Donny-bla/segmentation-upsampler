function DoC = DegreeOfComplexity(originalModel)

se = strel('sphere',1);
erodedModel = imerode(originalModel, se);

modelSurface = originalModel-erodedModel;
Surface = sum(modelSurface,"all");
Volume = sum(originalModel,"all");

DoC = Surface/Volume;

end