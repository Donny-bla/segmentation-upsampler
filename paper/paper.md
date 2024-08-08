---
title: 'Resampling segmented medical image data for treatment planning in ultrasound therapy'
tags:
  - Python
  - Image upsampling
  - Ultrasound simulation

authors:
  - name: Donny Liangpu Liu
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: 1
  - name: Rui Xu
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Bradley Treeby
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
    
affiliations:
 - name:  Department of Medical Physics and Biomedical Engineering, University College London, UK 
   index: 1
date: 13 August 2017
bibliography: paper.bib 

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

Recent advances in ultrasound therapy are supported by improved simulation methods. These methods enhance diagnostic, therapeutic, and monitoring capabilities. A significant challenge in ultrasound simulations is the insufficient resolution of the medical images (usually MRI and CT scans) used to generate patient-specific simulation domains. Accurate patient-specific ultrasound simulation typically requires medical image upsampling, but naive upsampling methods can introduce artifacts and inaccuracies that corrupt simulation accuracy.

To address this, a new mesh-based algorithm is developed for upsampling 3-dimensional segmented medical images. The algorithm smooths the image, extracts an isosurface, generates a triangulated mesh, and rasterizes it to the required resolution. This method reduces staircasing and other upsampling artifacts, compared to traditional upsampling methods.

The algorithm's effectiveness is demonstrated using a complex test object and medical images of a spine and liver, showing improved accuracy and smoothness. This approach holds promise for enhancing the precision of ultrasound simulations in personalized medicine.

# Statement of need

Ultrasound therapy has progressed substantially, with current applications extending from targeted cancer treatment to non-invasive brain function modulation [^1] [^2]. The development and success of these applications is partially driven by the adoption of advanced simulation methods. Simulation methods have enabled the focusing of ultrasound through complex media such as the skull [^3] using techniques like phase correction [^4] and electronic focusing [^5].

Ultrasound simulation can provide insight into the diagnosis [^6], treatment [^7], and monitoring of various health conditions [^8]. For example, ultrasound neuromodulation is rapidly developing as a tool in personalized medicine. Subject-specific simulations can be used to estimate treatment pressures and heating, giving confidence in the safety and efficacy of the treatment[^9][^10].

One of the primary limitations in patient-specific ultrasound simulation is the resolution of medical images. Medical images, such as those obtained through Magnetic Resonance Imaging (MRI) or Computed Tomography (CT) scans, can provide sufficient information for radiologists' diagnosis. However, the resolution of these images are often insufficient for accurate ultrasound simulation. In practice, an MR Image typically has a 1 mm isotropic resolution, while CT resolution is typically 0.5 mm in plane and 1-2 mm between planes. Ultrasound simulations need 6-12 grid points per wavelength, which at 500 kHz and in water or most soft tissues, corresponds to an isotropic resolution of 0.25 to 0.5 mm [^11]. Prior to ultrasound simulation, these images are typically segmented into labels, with each label representing a different type of tissue or material. Image segmentation can be completed manually, semi-automatically [^12], and now with AI models [^13]. The resulting label-map is then used to define the acoustic (and thermal) properties throughout the simulation grid. The resolution of these segmented images and the accuracy of the segmentation tends to limit simulation accuracy [^11].

An 'upsampling' process is required in order to bridge the gap between image resolution and the required simulation resolution. However, naive interpolation-based upsampling methods, such as nearest neighbour or linear interpolation, may lead to 'staircasing' effects [^11]. Poor image segmentation may also lead to a staircased simulation domain and incorrect simulation results.

The challenge, therefore, lies in developing an upsampling method that can increase the resolution of segmented medical images smoothly, without introducing staircasing effects or other artifacts. The upsampling method should also be able to at least partially smooth staircasing artifacts introduced by poor image segmentation.

# Algorithm design
## Overview

![Workflow diagram](figure/workflow.svg)

*Figure 1: Algorithm workflow*

This section introduces an algorithm that utilizes a mesh-based method for the upsampling process. The workflow of the algorithm is depicted in Figure 1. An image with a single label can be equated to a binary image. To begin, our algorithm converts the binary image to a floaing point array, then smooths the image using a grid-based method. Smoothing is implemented based on the assumption that a smooth surface tends to be a better assumption of the natural shape of a biological object. Next, an isosurface is extracted from the smoothed image, generated from points within the volume with a constant value. Subsequently, the algorithm generates a triangulated free-space surface mesh grid-based isosurface. A hole-filling function is implemented to improve the mesh quality. Finally, the free-space mesh is rasterized in a new grid with the required discretization for accurate ultrasound simulation.

Add description of multi-label upsampling. 

## Input & Output
The algorithm accepts and returns the following variables:

**Input:**

OriginalImage: low resolution input (binary or integer 3D array for images with two or more labels, respectively)

spacing: spacing of the original image (describe units and array type)

$dx$: scale of upsampling (3*1 array for medical image, for instace [0.5, 0.5, 1] will upsample the image by 2 times in x and y axis and no upsampling in z axis.)

$\sigma$: sigma for Gaussian smoother (scalar float, recommand range: 0 - 1)

$I$: isovalue for isosurface extraction (scalar float, recommand range: 0.4 - 0.5)

**Output:**

NewImage: high resolution output with defined spacing

The choice of $\sigma$ and $I$ parameters can significantly impact the quality of the upsampled image. The optimal parameters depend on the geometry of the segmented object and object-specific $(\sigma, I)$ optimisation may be needed for complex objects that have both sharp edges and smooth and curved surfaces. 

# Application
## Test Objects

We used code-defined test objects to identify optimal sigma and isovalues for the upsampling algorithm. The primary test object is a complex shape, as shown in Figure 2, and is used in all following numerical experiments unless otherwise specified.

![‘Complex’ Test Object: a) three-dimensional isometric projection, b) top view, c) front view, and d) side view of the complex test object.](figure/complex_object_combined.svg)

*Figure 2: 'Complex' Test Object: three-dimensional isometric projection, b) top view, c) front view, and d) side view of the complex test object.*

The complex test object is generated by subtracting smaller spheres from a larger sphere. Spheres are generated using the $makeSphere$ function from the k-Wave acoustic simulation toolbox $Add reference$. The base sphere has a radius of $r$ and its centre is at $(0,0,0)$. Six smaller spheres with radii of $0.75r, 0.67r, 0.5r, 0.33r, 0.25r, 0.2r$ are subtracted at $(\pm r,0,0), (0,\pm r, 0), (0,0,\pm r)$ respectively. The radius $r$ was set to 20 voxels. The spherical subtractions from the base sphere generate sharp edges, similar to certain bony anatomical features that need to be preserved during upsampling for simulation accuracy.

## Error Metrics

We evaluate the upsampling algorithm accuracy with a given $(\sigma, isovalue)$ parameter pair by comparing the upsampled image with the high-resolution ground truth and by calculating the number of 'incorrect' labels. This parameter will be referred to as $Diff$ in the following sections. A Boolean difference matrix is obtained by comparing the result and the reference image. $Diff$ is the sum of all voxels in the difference matrix. Here, the $Diff$ is normalised as follows.

$$Diff = \Sigma(ref\neq out)\$$

$$Grade\  by\  Volume = \frac{\Sigma(ref\neq out)}{\Sigma ref}\$$

In these equations, $\Sigma ref\$ represents the volume of the high-resolution ground truth;

The Grade by Volume is equivalent to the percentage of "correct" labels. The Grade by Shape relates to the complexity of the image and is independent of the reference image. These two normalization methods may lead to different conclusions when comparing different test objects. However, both metrics are based on $Diff$ and will give the same conclusion when testing a single object. The following sections will focus on developing an algorithm that minimizes these two test metrics.

## Comparison against naive upsampling approach
Figure 3 presents a comparison of the results obtained from two commonly-used upsampling methods (nearest-neighbor interpolation and trilinear interpolation) and our mesh-based upsampling method applied to the 'complex' test object. Our mesh-based upsampling algorithm (with $\sigma = XX, I = XX$) outperforms nearest-neighbor interpolation and trilinear interpolation across the range of tested upsampling values. This figure illustrates the variation in error against the scale of upsampling for the same object. The variable dx is the reciprocal of the scale of upsampling, meaning that a smaller dx represents a larger scale of upsampling. While some algorithms may have an advantage in upsampling particular shapes, the 'complex' test object has convex components, concave components, edges of varying ‘sharpness’ and may serve as a generic test object for comparison across upsampling methods. 

![Comparison against other methods. As depicted in the figure, the trilinear interpolation method has the highest error. The performance of our mesh-based method is slightly better compared to the Nearest Neighbor method. The sudden improvement at 0.5 may be related to index rounding. The mesh-based method outperforms the other two methods across the tested upsampling scales.](figure/method_comparsion.svg)

*Figure 3: Upsampling accuracy comparison of the mesh-based upsampling algorithm against trilinear and nearest-neighbour upsampling.*

Figure 3 shows that the trilinear interpolation method has the highest error across the tested upsampling regime. The performance of our mesh-based method is slightly better than the nearest-neighbor method. The sudden improvement at $dx = 0.5$ may be related to index rounding. All three methods show a trend of decreasing error percentage as the scale of upsampling increases, especially when $dx$ reaches 0.5. This trend may result from the normalization by volume; the number of voxels in the volume increases faster than the number of voxels at the object interface that are challenging to upsample accurately, as the scale of upsampling increases. 

## Demonstration
Figure 4 presents a demonstration of the upsampling of a multi-label spine segmentation with input parameters $\sigma = 0.7$ and isovalue = 0.4. The input data is sourced from Liebl $et$ $al$. 2021 [^14]. This demonstration involves upsampling at a scale of 0.8 with spacing at [0.2910, 0.2910, 1.2500]. As depicted in the figure, our algorithm successfully smooths some of the originally staircased verteral interfaces. This smoothing effect is particularly evident at the bottom vertebra.

![spineDemo](figure/spineDemo.svg)

*Figure 4: Mesh-based upsampling demonstration with a segmented spine (subverse003) from the Verse2020 spine segmentation dataset [^14].*

Figure 5 illustrates another example of an upsampled multi-label medical image with input parameters $\sigma = 0.4$ and isovalue = 0.4, showcasing a liver obtained from the female Visible Human Project dataset [^15]. This demonstration also involves upsampling at a scale of 0.8 with spacing at [1, 1, 1]. As shown in the figure, our algorithm clearly upsampled the structure for several complex, attached shapes, without leaving gaps between labels.

![liverDemo](figure/liverDemo.svg)

*Figure 5: Mesh-based upsampling demonstration with a kidney and surrounding organs from the female Visible Human Project dataset [^15].*

# Acknowledgements

This work was supported in part by a UKRI Future Leaders Fellowship (Grant MR/T019166/1) and in part by the Wellcome/EPSRC Centre for Interventional and Surgical Sciences (WEISS) (No. 203145Z/16/Z). For the purpose of open access, the author has applied a CC BY public copyright licence to any Author Accepted Manuscript version arising from this submission. 

# References
[^1]: Bachu, V. S., Kedda, J., Suk, I., Green, J. J., & Tyler, B. (2021). High-intensity focused ultrasound: a review of mechanisms and clinical applications. Annals of biomedical engineering, 49(9), 1975-1991.
[^2]: Martin, E., Roberts, M., Grigoras, I. F., Wright, O., Nandi, T., Rieger, S. W., ... & Treeby, B. E. (2024). Ultrasound system for precise neuromodulation of human deep brain circuits. bioRxiv, 2024-06.
[^3]:Jiménez-Gambín, S., Jiménez, N., Benlloch, J. M., & Camarena, F. (2019). Holograms to focus arbitrary ultrasonic fields through the skull. *Physical Review Applied, 12*(1), 014016.
[^4]:Yasuda, J., Yoshikawa, H., & Tanaka, H. (2019). Phase aberration correction for focused ultrasound transmission by refraction compensation. Japanese Journal of Applied Physics, 58(SG), SGGE22.
[^5]:Aulbach, J., Bretagne, A., Fink, M., Tanter, M., & Tourin, A. (2012). Optimal spatiotemporal focusing through complex scattering media. Physical Review E—Statistical, Nonlinear, and Soft Matter Physics, 85(1), 016605.
[^6]:Menz, M. D., Oralkan, Ö., Khuri-Yakub, P. T., & Baccus, S. A. (2013). Precise neural stimulation in the retina using focused ultrasound. Journal of Neuroscience, 33(10), 4550-4560.
[^7]:Romano, C. L., Romano, D., & Logoluso, N. (2009). Low-intensity pulsed ultrasound for the treatment of bone delayed union or nonunion: a review. Ultrasound in medicine & biology, 35(4), 529-536.
[^8]:Blackmore, J., Shrivastava, S., Sallet, J., Butler, C. R., & Cleveland, R. O. (2019). Ultrasound neuromodulation: a review of results, mechanisms and safety. Ultrasound in medicine & biology, 45(7), 1509-1536.
[^9]: Xu, R., Bestmann, S., Treeby, B. E., & Martin, E. (2024). Strategies and safety simulations for ultrasonic cervical spinal cord neuromodulation. Physics in Medicine and Biology.
[^10]: Aubry, J. F., Bates, O., Boehm, C., Butts Pauly, K., Christensen, D., Cueto, C., ... & Van't Wout, E. (2022). Benchmark problems for transcranial ultrasound simulation: Intercomparison of compressional wave models. The Journal of the Acoustical Society of America, 152(2), 1003-1019.
[^11]: Robertson, J. L., Cox, B. T., Jaros, J., & Treeby, B. E. (2017). Accurate simulation of transcranial ultrasound propagation for ultrasonic neuromodulation and stimulation. The Journal of the Acoustical Society of America, 141(3), 1726-1738.
[^12]:Yushkevich, P. A., Gao, Y., & Gerig, G. (2016, August). ITK-SNAP: An interactive tool for semi-automatic segmentation of multi-modality biomedical images. In 2016 38th annual international conference of the IEEE engineering in medicine and biology society (EMBC) (pp. 3342-3345). IEEE.
[^13]:Milletari, F., Navab, N., & Ahmadi, S. A. (2016, October). V-net: Fully convolutional neural networks for volumetric medical image segmentation. In 2016 fourth international conference on 3D vision (3DV) (pp. 565-571). IEEE.
[^14]:Liebl, H., Schinz, D., Sekuboyina, A., Malagutti, L., Löffler, M. T., Bayat, A., ... & Kirschke, J. S. (2021). A computed tomography vertebral segmentation dataset with anatomical variations and multi-vendor scanner data. Scientific data, 8(1), 284.
[^15]:Massey, J. W., & Yilmaz, A. E. (2016, August). AustinMan and AustinWoman: High-fidelity, anatomical voxel models developed from the VHP color images. In 2016 38th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC) (pp. 3346-3349). IEEE.
