function rf = computeRemovingFactor(sliderValue, gridx, gridy)
%COMPUTEREMOVINGFACTOR  Map slider value to pixel area using logarithmic scale.
%   rf = bubblefit.imageproc.computeRemovingFactor(sliderValue, gridx, gridy)
%
%   Uses logarithmic mapping so the slider is effective across its full range:
%   left half covers noise-scale areas (10-3600 px), right half covers
%   structural-scale areas (3600-130000 px).
%
%   Inputs:
%     sliderValue - slider position (0 to 100)
%     gridx       - [row_start, row_end] ROI bounds
%     gridy       - [col_start, col_end] ROI bounds
%
%   Output:
%     rf - minimum connected area size (pixels) for bwareaopen

    roiArea = (gridx(2) - gridx(1)) * (gridy(2) - gridy(1));

    minArea = 10;
    maxArea = max(round(roiArea * 0.5), minArea + 1);

    if sliderValue <= 0
        rf = minArea;
    else
        rf = round(minArea * (maxArea / minArea) ^ (sliderValue / 100));
    end

end
