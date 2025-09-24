# Adaptive microscopy approach for automation of a laser ablation workflow

These Python scripts automate laser ablation experiments to infer mechanical properties on cell surfaces during embryo development. They are written in Python 2.7 and designed to run within the IronPython environment of VisiView (v4.1) software, utilizing the VisiView API to control the microscope. The workflow ensures reproducibility and robustness while circumventing limitations within the native software.

<img width="1093" height="370" alt="image" src="https://github.com/user-attachments/assets/0bd52e1a-cb69-408e-863c-f4f491b9272e" />

This figure illustrates an automated laser ablation experiment measuring the mechanical properties of adherens junctions in a Drosophila embryo. A diagram of the embryo is shown alongside a magnified, time-lapsed view of the junctions before (blue, t=-5s) and after (yellow, t=10s) being severed by a laser at the site indicated by the red cross. This is what the Python scripts automate. A kymograph visualizes the displacement of the junction over time, clearly showing the separation that occurs at t=0s. This displacement is quantified in the graph to the right, which plots the average displacement in micrometers over time from 20 wild-type (WT) experiments, with the shaded area representing the standard deviation. The rapid separation immediately following the laser cut is highlighted as the "initial recoil", which is the most direct (but still indirect) estimation we get of mechanical tension.

## Scripts Overview

### `scripts/Ablation_And_Acquisition_OnTheFly_GFP.py`
This is the primary script for executing laser ablation experiments with synchronized time-lapse imaging. It orchestrates the entire workflow, from pre-ablation imaging to post-ablation monitoring.

**Key Features:**
*   **Automated Workflow:** Captures baseline imaging, executes ablation at a precise timepoint, and continues with post-ablation monitoring.
*   **High-Speed Acquisition:** Achieves 0.1s temporal resolution using VisiView's "streaming" mode, bypassing the variable initiation delays (0.3-1.5s) of the standard FRAP mode.
*   **"OnTheFly" Laser Control:** Utilizes the VisiView API's "OnTheFly" functionality for reproducible, near-instantaneous ablation while preventing unwanted activation of acquisition lasers.
*   **Precise Timing:** All operations are timestamped with microsecond precision for accurate correlation with physiological responses.
*   **Comprehensive Logging:** Generates detailed reports including ROI coordinates, per-pixel ablation times, and a complete experimental timeline.
*   **Z-Stack Capability:** Allows focal plane adjustments for ablating at different tissue depths. This is critical for the 40x objective, where the ablation focus is typically offset by ~10µm from the imaging plane.

#### Usage and Setup
1.  **Channel:** Set up a single acquisition channel. Ensure other modes (multi-channel, Z-series, Stage points) are disabled.
2.  **Time Series:** Enable the **"Stream"** option in the time series tab.
3.  **Autofocus:** Disable autofocus (PFS) to prevent Z-corrections during the experiment.
4.  **ROI:** Define one Region of Interest (ROI) in the active window before starting.
5.  **Calibration:** Calibrate the ablation laser for your chosen configuration (e.g., 60x/2x) before use.
6.  **Objective Note:** The 60x/2x configuration ablates at the focal plane; the 40x objective requires a ~10µm Z-offset.

#### Recommended Parameters
*   **Laser Power:** 20-40% (optimize for clean, reproducible junction recoil without bubble formation).
*   **OnTheFly Exposure:** 10-20ms per pixel, single cycle.
*   **Optimization Tip:** Test multiple junctions to assess recoil variability and find the optimal power balance. Note that some junctions may not recoil if they are not under tension.

---

### `scripts/OneCut_OnTheFly_BrightField.py` / `scripts/OneCut_OnTheFly_GFP.py`
Quick test scripts for system validation. They perform a single ablation using the current ROI without starting image acquisition, allowing verification of laser alignment and power settings.
*   Use the `BrightField` version after initial calibration.
*   Use the `GFP` version to test on fluorescent samples using the 488 laser.
*   Both scripts automatically switch to the correct imaging channel if needed.

---

### `scripts/AblationOnTheFly_Functions.py`
A library of core functions imported by the other scripts. It converts user-defined VisiView ROIs (line, rectangle, circle) into optimized pixel coordinate sequences for the laser.

*   **Manual Coordinate Calculation:** The VisiView API does not provide ROI pixel coordinates directly. These functions calculate them manually to enable the "OnTheFly" ablation mode, which is faster and more precise than the standard FRAP functionality.
*   **Ablation Density Control:** The `skip` parameter allows fine-tuning of ablation density, from complete coverage (`skip=0`) to sparse patterns (`skip=3`) for delicate samples.
*   **Path Optimization:** Implements serpentine scanning and Bresenham's line algorithm to minimize stage movement and ensure pixel-perfect accuracy.

---

### `scripts/Load_Region.py`
A script that loads a saved ROI object (`roi_used_for_dorsal_closure_visiview.rgn`) to ensure the ablation region is of consistent size and positioned for experiments.

---

## Downstream Data Analysis

1.  **Kymograph Generation:** Kymographs were generated from image data in Fiji using the **Multi Kymograph** plugin.
2.  **Data Extraction:** Kymographs were traced by hand using the polygon selection tool, and a custom Fiji macro was used to extract the coordinates.
3.  **Velocity Calculation:** The initial recoil velocity was determined using R. A monotonically constrained nonparametric regression model was fitted to each experiment's data. An interpolating B-splines function was then used to extract the first-order derivative at the moment of ablation (t=0), yielding the initial recoil velocity.

---

## Hardware and Software Requirements

These scripts were developed for a VisiScope Confocal-FRAP Cell Explorer spinning disk confocal microscope with the following specifications.

### Hardware Configuration
*   **Microscope:** Nikon Eclipse Ti-E
*   **Confocal System:** Yokogawa Spinning Disc System W1 (dual disc: 25 µm pinholes for low NA, 50 µm for high NA objectives)
*   **Cameras:** 2 × EMCCD Andor iXon Ultra (1024×1024 pixels, 13×13 μm pixel size)
*   **Objectives:**
    *   Nikon Apo LWD 40× NA 1.15 lambda S (xy-resolution: 0.33×0.33 µm)
    *   Nikon Apo Plan VC 60× A/1.20 WI (xy-resolution: 0.22×0.22 µm)
*   **Stage:** Motorized xyz stage
*   **Focusing:**
    *   Perfect Focus System (PFS) for drift correction (*Note: Must be turned off for laser ablation*)
    *   Highly precise motorized z-focus/nosepiece
*   **Ablation Laser:** STV-01E-1x0 UV laser (Teem Photonics)
    *   **Wavelength:** 355 nm
    *   **Pulse Width:** 0.4 ns
    *   **Pulse Energy:** 1 µJ
    *   **Repetition Rate:** 4 kHz

### Software Requirements
*   **Control Software:** VisiView v4.1
*   **Environment:** IronPython 2.7 (as provided by VisiView)
