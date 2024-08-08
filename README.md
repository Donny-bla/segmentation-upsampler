
# Segmentation Upsampler

This is a Python based software for upsampling segmentated image. Using mesh based method, aimed to reduce staircasing effect in upsampling and improve accuracy of ultrasound simulation.
## Installation

*While the software is Python based. MATLAB is used to generate sample shapes and run tests.

The software was developed under following environment:\
Python version 3.9\
MATLAB R2023b\
To use lateral version of Python, do check whether its compatibility using this link: https://www.mathworks.com/support/requirements/python-compatibility.html.


Python package Installation:\
pip install numpy scipy vtk numba

MATLAB package:\
k-wave (http://www.k-wave.org/)

## Examples

Code $multilabelExample.m$ is an example of processing generated complex shape compare to a high resolution ground truth.

Code $vertrbraExample.m$ is an example of processing medical image. Figure 1 presents a demonstration of the upsampling of a multi-label spine segmentation with input parameters $\sigma = 0.7$ and isovalue = 0.4. The input data is sourced from Liebl $et$ $al$. 2021 [^1]. This demonstration involves upsampling at a scale of 0.8 with spacing at [0.2910, 0.2910, 1.2500]. 

![spineDemo](paper/figure/spineDemo.svg)

*Figure 1: Mesh-based upsampling demonstration with a segmented spine (subverse003) from the Verse2020 spine segmentation dataset [^1].*

Code $AustinWomanKindeySliceExample.m$ is another example of processing medical image. Figure 2 illustrates another example of an upsampled multi-label medical image with input parameters $\sigma = 0.4$ and isovalue = 0.4, showcasing a liver obtained from the female Visible Human Project dataset [^2]. This demonstration also involves upsampling at a scale of 0.8 with spacing at [1, 1, 1].

![liverDemo](paper/figure/liverDemo.svg)

*Figure 2: Mesh-based upsampling demonstration with a kidney and surrounding organs from the female Visible Human Project dataset [^2].*

[^1]:Liebl, H., Schinz, D., Sekuboyina, A., Malagutti, L., Löffler, M. T., Bayat, A., ... & Kirschke, J. S. (2021). A computed tomography vertebral segmentation dataset with anatomical variations and multi-vendor scanner data. Scientific data, 8(1), 284.
[^2]:Massey, J. W., & Yilmaz, A. E. (2016, August). AustinMan and AustinWoman: High-fidelity, anatomical voxel models developed from the VHP color images. In 2016 38th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC) (pp. 3346-3349). IEEE.
