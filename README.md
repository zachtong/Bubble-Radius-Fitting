# BubbleRadiusFitting
This is a Matlab-based GUI for bubble radius fitting

*Algorithm Development: Dr. Jin Yang (Email: jin.yang@austin.utexas.edu)
*GUI Development: Zach Tong (Email: zachtong@utexas.edu)
*Prerequisites: You may need to install an image processing toolbox and your Matlab version can install this mlappinstall file.

Usage Instructions:
0. Run the Bubble Radius Fitting.mlappinstall file and open it in your Matlab_APPS.

1. Loading Images: Begin by loading the folder containing your images.

2. Initial evaluation: Pre-tune using the first image where bubbles are visible to assess the overall image quality.
	2.1 Select ROI: Define the Region of Interest (ROI) by selecting two points to create a rectangular area.
	2.2 Adjust Removal Threshold: Experiment with the threshold for removing connected areas. A threshold greater than 500 is recommended.

3. Automatic Mode: Activate the Automatic mode. Note that the ROI and the threshold for removing connected areas should be set based on the maximum bubble size encountered in your images.

4. Parameter Adjustment: If necessary, you can adjust the parameters and rerun the Automatic mode to update your radius-time (R-t) curves.

5. Manual Mode for Outliers: For any outliers, Manual mode allows you to select several points along the bubble edge to accurately fit the bubble radius.

6. Exporting Data: Save your radius (R) data by clicking the 'Export' button.

Further Assistance: For more information or assistance, please contact either Dr. Jin Yang or Zach Tong.
