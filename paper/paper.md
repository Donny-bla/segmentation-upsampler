
---
title: 'Resampling segmented medical image data for treatment planning in ultrasound therapy'
tags:
  - Python

authors:
  - name: xxx
    affiliation: 1
affiliations:
 - name: -
   index: 1
date: 13 July 2024
bibliography: paper.bib
<!--
# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: Astrophysical Journal <- The name of the AAS journal. 
-->
---

# Summary


# Statement of need

Ultrasound therapy has seen remarkable progress recently, with its applications extending from targeted cancer treatments to non-invasive brain function modulation [^1]. The use of ultrasound therapy often requires simulation to enhance its effectiveness in different clinical scenarios [^2][^1].

Ultrasound simulation can provide insights into the diagnosis, treatment, and monitoring of various health conditions. For instance, ultrasound can stimulate neuronal behaviour. By conducting simulations, we can monitor the variation of pressure and heat during medical treatment [^3][^4].

One of the primary limitations in this field is the resolution of medical images. Medical images, such as those obtained through Magnetic Resonance Imaging (MRI) or Computed Tomography (CT) scans, can provide sufficient information for radiologists' diagnosis. However, the resolution of these segments is often insufficient for the detailed simulations required in ultrasound studies. In practice, an MR Image is typically 1 mm isotropic resolution, while a CT is typically 0.5 mm in plane and 1-2 mm between planes. Ultrasound simulations need 6-12 grid points per wavelength, which at 500 kHz in water, corresponds to a required resolution of 0.25 to 0.5 mm [^5]. During ultrasound simulation, these images are typically segmented into labels, each representing a different type of tissue or material by segmentation AI or other tools. The resolution of these segmented images tends to limit simulation accuracy [^5].

To bridge this gap, an 'upsampling' process is required. This process involves increasing the resolution of the segmented images to match that required for simulation. However, naive, interpolation-based upsampling methods, such as nearest neighbour or linear interpolation, often lead to 'staircasing' effects [^5]. This is where the boundaries between labels become artificially jagged due to the increased resolution. Those images cannot represent any biological feature.

The challenge, therefore, lies in developing an upsampling method that can increase the resolution of segmented medical images smoothly, without introducing staircasing effects or other artifacts.

# Algorithm design
## Overview
This chapter introduces an algorithm that utilizes a mesh-based method for the process of upsampling. The workflow of the algorithm is depicted in the Fig 1.

![Workflow diagram](Figures/workflow.jpg)
*Figure 1: Workflow diagram*

A single labelled image can be equated to a binary image. Initially, this image undergoes a smoothing process in a grid-based manner. The smoothing will convert a binary image into a double/single precision image. The purpose of the smoothing process is to add extra information, based on the assumption that objects are generally smooth. A smoother surface tends to be a better assumption of the natural shape of the object. From the smoothed image, an isosurface is extracted indicating points within a spatial volume where the values are constant.

Subsequently, the algorithm generates a triangulated surface mesh and rasterizes it. The surface mesh serves as the original shape in a continuous grid space. The rasterization process determines whether points in a high-resolution grid fall within the surface mesh.
## Input & Output
The final algorithm accepts and returns the following variables:

**Input:**
OriginalImage: low resolution input
dx: scale of upsampling
sigma: sigma for Gaussian smoother
I: isovalue for isosurface extraction

**Output:**
NewImage: high resolution output

While the *OriginalImage* and *dx* are required inputs from the user, the sigma and isovalue parameters necessitate further investigation to ascertain the optimal settings. This will be discussed in the subsequent section. It is important to note that the choice of these parameters can significantly impact the quality of the upsampled image.

# Application
## Test Objects

Our test objects include simple shapes such as a sphere, a bowl, a cylinder, and a sphere with a hole shown in Figures \ref{fig:sphere_hole}, \ref{fig:cylinder}, \ref{fig:bowl}, and \ref{fig:sphere}. We also have a complex object used in many tests, as shown in Figure \ref{fig:complex}. This complex object is used in all subsequent numerical experiments unless otherwise specified.

![Testing object: sphere with hole](new_figures/figures/spherehole_testobject.eps)
*Figure 4: Testing object: sphere with hole*\label{fig:sphere_hole}

![Testing object: cylinder](new_figures/figures/cylinder_testobject.eps)
*Figure 5: Testing object: cylinder*\label{fig:cylinder}

![Testing object: bowl](new_figures/figures/bowl_testobject.eps)
*Figure 6: Testing object: bowl*\label{fig:bowl}

![Testing object: sphere](new_figures/figures/sphere_testobject.eps)
*Figure 7: Testing object: sphere*\label{fig:sphere}

![‘Complex’ Test Object: three-dimensional isometric projection](new_figures/figures/complex_object.eps)
*Figure 8: 'Complex' Test Object: three-dimensional isometric projection*\label{fig:complex}

![‘Complex’ Test Object: top view, front view and side view](new_figures/figures/complex_threeview.eps)
*Figure 9: 'Complex' Test Object: top view, front view and side view*\label{fig:three-view}

Objects can be generated programmatically at any desired grid resolution, so it is possible to create both low and high-resolution versions of the same test object. The sphere is generated using the k-wave toolbox [^1]. Other simple objects like a bowl and a sphere with a hole are generated by simple subtraction. A bowl is generated by subtracting a small semi-sphere from a larger one at the centre. A sphere with a hole is generated by subtracting a cylinder from a sphere at the centre. These simple objects can represent the general shape of some anatomical structures. For instance, the bowl can be likened to a skull, the cylinder can be likened to most long bones, the sphere with a hole is similar to a vertebra, and the sphere and sphere with a hole can be used for modelling an eyeball.

The complex testing object is generated by subtracting smaller spheres from a larger sphere in six different directions. The base sphere has a radius of \(r\) and its centre is at \((0,0,0)\). Six smaller spheres with radii of \(0.75r, 0.67r, 0.5r, 0.33r, 0.25r, 0.2r\) are subtracted at \((\pm r,0,0), (0,\pm r, 0), (0,0,\pm r)\) respectively. Note that the radius used in this project is 20 voxels.

While the whole shape may not closely resemble any specific human body part, those sphere depressions of different sizes offer many sharp edges. They also provide shapes similar to a ball-socket shoulder or leg joint.

This complex object is also used in multilabel testing. The multilabel testing object is generated by adding back those smaller spheres in each direction and allocating each with a different label. It's a testing object that provides simple boundary attachment of different labels.

## Error Metrics

To evaluate the test results, we will compare the results with high-resolution ground truth and identify the number of 'incorrect' labels. This parameter will be referred to as *Diff* in the following sections. A Boolean difference matrix is obtained by comparing the result and the reference image. *Diff* is the sum of all voxels in the difference matrix. Here, we present two methods to normalize the *Diff*.

\[Diff = \Sigma(ref\neq out)\]

\[Grade\  by\  Volume = \frac{\Sigma(ref\neq out)}{\Sigma ref}\]

\[Grade\ by\ Shape = \frac{\Sigma(ref\neq out)}{(\frac{A_{i}}{\Sigma in})^3dx^3}\]

In these equations, \(\Sigma ref\) represents the volume of the high-resolution ground truth; \(A_i\) and \(\Sigma in\) represent the surface area and volume of the input image, respectively; and \textit{dx} represents the scale of upsampling.

It's worth noting that the surface area \(A_i\) is the sum of all voxels on the outermost layer. To compute this, the input image is eroded using a morphological spherical operator with a radius of 1, which is a kernel that works well for these testing objects. Then, the outermost layer is obtained by subtracting the eroded image from the input image.

The Grade by Volume is equivalent to the correct percentage. The Grade by Shape relates to the complexity of the image and is independent of the reference image. These two normalization methods could lead to different conclusions when comparing different test objects. However, both of them are based on the *Diff* and will give the same conclusion when testing a single object. The following sections will focus on developing an algorithm that minimizes these two parameters.

## Comparsion against naive upsampling approach
Figure \ref{fig:upsample_methods} presents a comparison of the results obtained from different upsampling methods applied to the 'complex' testing object. This figure illustrates the variation in error against the scale of upsampling for the same object. The variable dx is the reciprocal of the scale of upsampling, meaning that a smaller dx represents a larger scale of upsampling. While we cannot neglect that some algorithms may have an advantage in upsampling particular shapes, the 'complex' test object is considered to be complex enough to encompass all common features of shape and thus serves as a fair object for comparison.

![Comparison against other methods. As depicted in the figure, the trilinear interpolation method has the highest error. The performance of our mesh-based method is slightly better compared to the Nearest Neighbor method. The sudden improvement at 0.5 may be related to the rounding of the index. Note that this mesh-based method is always better than the other two methods.](new_figures/figures/method_comparsion.eps)
*Figure 10: Comparison against other methods. As depicted in the figure, the trilinear interpolation method has the highest error. The performance of our mesh-based method is slightly better compared to the Nearest Neighbor method. The sudden improvement at 0.5 may be related to the rounding of the index. Note that this mesh-based method is always better than the other two methods.*

Interestingly, all three methods show a trend of decreasing error percentage as the scale of upsampling increases, especially when the scale reaches 0.5. A general trend shown in this comparison could either be an improvement in performance or an effect caused by the method of error normalization. Since the volume normalizes the difference, the volume may increase faster than the number of differences. This observation underscores the importance of carefully considering the impact of normalization methods on the interpretation of results.

## Demonstration

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
[^1]: Bachu, E. (2021). High-Intensity Focused Ultrasound in Cancer Treatment.
[^2]: Pacini, S., & Bachu, E. (2003). Recombinant Techniques in Ultrasound Therapy.
[^3]: Xu, Y. (2024). Strategies in Ultrasound Simulation.
[^4]: Aubry, J. (2022). Benchmark for Ultrasound Simulation.
[^5]: Robertson, J. (2017). Accurate Imaging for Ultrasound Simulation.

