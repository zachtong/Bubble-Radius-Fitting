function [cur_img, cur_img_binary, cur_img_ROI, cur_img_binary_ROI] = ...
    loadAndNormalize(images, imageNo, sensitivity, gridx, gridy)
%LOADANDNORMALIZE  Load image, normalize, apply adaptive threshold, and extract ROI.
%   [cur_img, cur_img_binary, cur_img_ROI, cur_img_binary_ROI] = ...
%       bubblefit.imageproc.loadAndNormalize(images, imageNo, sensitivity, gridx, gridy)
%
%   Inputs:
%     images       - cell array of image file paths
%     imageNo      - index of current image
%     sensitivity  - adaptive threshold sensitivity (0 to 1)
%     gridx        - [row_start, row_end] ROI bounds
%     gridy        - [col_start, col_end] ROI bounds
%
%   Outputs:
%     cur_img            - normalized grayscale image [0, 1]
%     cur_img_binary     - binary image after adaptive threshold
%     cur_img_ROI        - ROI of normalized image
%     cur_img_binary_ROI - ROI of binary image

    raw_img = imread(images{imageNo});

    % If RGB, convert to grayscale
    if size(raw_img, 3) == 3
        raw_img = rgb2gray(raw_img);
    end

    % Normalize to [0, 1] for display purposes
    img_double = double(raw_img);
    img_min = min(img_double(:));
    img_max = max(img_double(:));
    if img_max > img_min
        cur_img = (img_double - img_min) / (img_max - img_min);
    else
        cur_img = zeros(size(img_double));
    end

    % Adaptive thresholding (handles non-uniform illumination and speckle)
    % imbinarize accepts uint8/uint16 directly; 'bright' foreground = background pixels
    cur_img_binary = imbinarize(raw_img, 'adaptive', 'Sensitivity', sensitivity);

    % Extract ROI
    cur_img_ROI = cur_img(gridx(1):gridx(2), gridy(1):gridy(2));
    cur_img_binary_ROI = cur_img_binary(gridx(1):gridx(2), gridy(1):gridy(2));

end
