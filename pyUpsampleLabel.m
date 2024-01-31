function UpsampledMatrix = pyUpsampleLabel(originalMatrix, dx, sigma, varargin)
if nargin<4
    Volume = -0.17;
else
    Volume = varargin{1};
end

newM = pyrunfile("UpsampleLabel.py","newMatrix", originalMatrix = py.numpy.array(originalMatrix), sigma = sigma, targetVolume = Volume, scale = dx);
UpsampledMatrix = single(newM);
UpsampledMatrix = permute(UpsampledMatrix,[3,2,1]);

