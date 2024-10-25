---
title: 'pySegmentationUpsampler: Resampling segmented medical image data for treatment planning in ultrasound therapy'
tags:
  - Python
  - Image upsampling
  - Ultrasound simulation

authors:
  - name: Donny Liangpu Liu
    orcid: 0009-0002-4523-1980
    equal-contrib: false
    affiliation: 1
  - name: Rui Xu
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
    
affiliations:
 - name:  Department of Medical Physics and Biomedical Engineering, University College London, UK 
   index: 1
date: 8 August 2017
bibliography: paper.bib 

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

Recent advances in ultrasound therapy are supported by improved simulation methods. Simulation methods can enhance diagnostic, therapeutic, and monitoring capabilities. A challenge in medical ultrasound simulation is the insufficient resolution of the medical images (usually MRI and CT scans) used to generate patient-specific simulation domains. Accurate patient-specific ultrasound simulation typically requires medical image upsampling, but naive upsampling methods can introduce artifacts and inaccuracies that corrupt simulation accuracy.

To address this, a new mesh-based algorithm is developed for upsampling 3-dimensional segmented medical images. The algorithm smooths the image, extracts an isosurface, generates a triangulated mesh, and rasterizes it to the required resolution. This method reduces staircasing and other upsampling artifacts, compared to traditional upsampling methods. This toolbox includes several examples including the upsampling of a complex code-based test object, and multi-labelled segmentations of a spine and a kidney with surrouding organs. This mesh-based upsampling approach may enhance ultrasound simulation accuracy in personalized medicine. While this method is designed for processing segmented medical images for ultrasound simulation, it may be used to upsample medical images for other uses, or more broadly upsample any segmented object.

# Statement of need

Therapeutic ultrasound applications extend from targeted cancer treatment to non-invasive deep brain neuromodulation [@vidaljove2022first, @martin2024ultrasound]. The development and success of new therapeutic ultrasound applications is often enabled by adoption of advanced simulation methods [@aubry2022benchmark]. For example, ultrasound neuromodulation is developing as a tool in personalized medicine. Subject-specific simulations can be used to estimate treatment pressures and heating, giving confidence in the safety and efficacy of the treatment[@martin2024ultrasound, @xu2024strategies]. Subject-specific simulations may also be used to calculate transducer element phase and amplitude corrections[@martin2024ultrasound] or to design acoustic holograms [@jimenezgambin2019holograms] for focusing through aberrating media such as the skull.

One limitation in patient-specific ultrasound simulation is medical image resolution. The resolution of a clinical magnetic resonance image is typically 1 mm (isotropic), while x-ray computed tomography resolution is typically 0.5 mm in plane and 1-2 mm between planes. Accurate grid-based ultrasound simulations typically require 6-12 grid points per wavelength, which at the commonly utilized ultrasound frequency of 500 kHz and in water or most soft tissues, corresponds to an isotropic resolution of 0.25 to 0.5 mm [@robertson2017accurate]. Prior to ultrasound simulation, these images are typically segmented into labels, with each label representing a different type of tissue or material. Image segmentation can be completed manually, semi-automatically [@yushkevich2016itksnap], and now with artificial intelligence methods [@milletari2016vnet]. The resulting label-map is then used to define the acoustic (and thermal) properties throughout the simulation grid. The resolution of these segmented images and the accuracy of the segmentation tends to limit simulation accuracy [@robertson2017accurate].

An 'upsampling' process is required to bridge the gap between image resolution and the required simulation resolution. However, naive interpolation-based upsampling methods, such as nearest neighbour or linear interpolation, may lead to 'staircasing' effects at a detriment to simulation accuracy [@robertson2017accurate]. Poor image segmentation may also lead to a staircased simulation domain and inaccurate simulation results.

The challenge lies in developing an upsampling method that can increase the resolution of segmented medical images smoothly, without introducing staircasing effects or other artifacts. The upsampling method should also be able to partially smooth staircasing artifacts introduced by poor image segmentation.

# Algorithm design
## Overview

![Workflow diagram](figure/workflow.svg)

*Figure 1: The input 3D image is binarized, then smoothed with a Gaussian smoothing kernel to create a 3D floating point array. A mesh is then generated and improved using python VTK [@schroeder2006visualization], before being rasterized to the target resolution to create the upsampled image.*

This section introduces an algorithm that utilizes a mesh-based method for the upsampling process. The workflow of the algorithm is depicted in Figure 1. An image with a single label can be equated to a binary image. To begin, the algorithm converts the binary image to a floaing point array, then smooths the image using a Gaussian smoothing kernel [@virtanen2020scipy, @keerthi2003asymptotic]. Smoothing is implemented on the basis that smooth surfaces are a better approximation of the natural shape of a biological object. Next, an isosurface is extracted from the smoothed image, generated from points within the volume with a constant value. Subsequently, the algorithm generates a triangulated free-space surface mesh isosurface through vtkFlyingEdges3D [@schroeder2006visualization, @schroeder2015flying]. A hole-filling function is implemented to improve the mesh quality. Finally, the free-space mesh is rasterized to the output grid with the required discretization by doing a pixelwised operation of vtk distance filter [@schroeder2006visualization, @quammen2011boolean] for accurate ultrasound simulation.

The workflow described above applies to the upsampling of a binary image. The algorithm is repeated for each label in a segmented medical image with multiple labels. However, multi-label upsampling introduces a new challenge: gaps with missing labels and overlapping segmentations at the boundaries between different labels. The algorithm handles overlaps by sorting the input labels by volume. The algorithm then starts the upsampling process with the largest volume, then repeatedly overwrites the output with the following smaller volumes. Gaps with missing labels are addressed with the careful selection of the isovalue to ensure that the volume enclosed by the isosurface is slightly larger than the original volume. The impact of isovalue selection is displayed in Figure 2. The toolbox also includes an optional hole-filling post-processing step that enables users to choose lower isovalues and close gaps between labels in a multi-label image. The post-processing checks the value of an empty voxel in each of the smoothed label matrices and the empty voxel is filled with the value of the highest smoothed label matrix. 

![Overlapping Gaussian](figure/overlapping_Gaussian.svg)

*Figure 2: Multi-label upsampling requires a balance between Gaussian smoothing level and isovalue selection in order to accurately create the mesh interface. A high isovalue e.g., a) 0.6 leaves gaps between labels after mesh creation. b) An isovalue of 0.5 is optimal in 1D but may leave gaps in 3D. c) A low isovalue (e.g., 0.4) reduces gaps but will result in biased label 1 or 2 volumes.*

The choice of $\sigma$ and $I$ parameters may impact the quality of the upsampled image. The optimal parameters depend on the geometry of the segmented object. Object-specific $(\sigma, I)$ optimisation may be needed for complex objects that have both sharp edges and smooth or curved surfaces. 

# Application

We used the code-defined test object displayed in Fig. 3 to identify optimal $\sigma$ and $I$ values. The test object is generated by subtracting smaller spheres from a larger sphere. Spheres are generated using the $makeSphere$ function from the k-Wave[@treeby2010kwave] acoustic simulation toolbox. The base sphere has a radius of $r$ and is centered at $(0,0,0)$. Six smaller spheres with radii of $0.75r, 0.67r, 0.5r, 0.33r, 0.25r, 0.2r$ are subtracted at $(\pm r,0,0), (0,\pm r, 0), (0,0,\pm r)$ respectively. The radius $r$ was set to 20 voxels. The spherical subtractions from the base sphere generate sharp edges, similar to certain bony anatomical features that need to be preserved during upsampling for simulation accuracy. Some upsampling algorithms may have an advantage in upsampling simple geometric shapes. To counteract this, the test object has convex components, concave components, and edges of varying ‘sharpness’, with the aim of representing a broad range of possible biological features. 

![‘Complex’ Test Object: a) three-dimensional isometric projection, b) top view, c) front view, and d) side view of the complex test object.](figure/complex_object_combined.svg)

*Figure 3: 'Complex' Test Object: three-dimensional isometric projection, b) top view, c) front view, and d) side view of the complex test object.*

We evaluate the upsampling algorithm accuracy with a given $(\sigma, isovalue)$ parameter pair by comparing the upsampled image ($out$) with the high-resolution ground truth ($ref$). A Boolean difference matrix of the two images is used to obtain the number of erroneous labels. The percentage error is then obtained by normalising the number of erroneous labels by the volume of the high-resolution ground truth.

$$%Error = 100 \times \frac{\Sigma(ref\neq out)}{\Sigma ref}\$$

Figure 4 presents a comparison of the results obtained from two commonly-used upsampling methods (nearest-neighbor interpolation and trilinear interpolation) and our mesh-based upsampling method. Our mesh-based upsampling algorithm (with $\sigma = 0.68, I = 0.513$) outperforms nearest-neighbor interpolation and trilinear interpolation across the range of tested upsampling values.

![Comparison against other methods. Upsampling accuracy comparison of the mesh-based upsampling algorithm against trilinear and nearest-neighbour upsampling.](figure/method_comparison_GBV.svg)

*Figure 4: Percentage upsampling error for the mesh-based upsampling algorithm versus two naive upsampling algorithms: trilinear and nearest-neighbour upsampling. The errors are evaluated across a range of upsampling scales.*

# Acknowledgements

This work was supported in part by a UKRI Future Leaders Fellowship (Grant MR/T019166/1) and in part by the Wellcome/EPSRC Centre for Interventional and Surgical Sciences (WEISS) (No. 203145Z/16/Z). For the purpose of open access, the author has applied a CC BY public copyright licence to any Author Accepted Manuscript version arising from this submission. 

# References
