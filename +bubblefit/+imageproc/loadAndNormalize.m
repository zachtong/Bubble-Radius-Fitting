function [cur_img, cur_img_binary, cur_img_ROI, cur_img_binary_ROI] = ...
    loadAndNormalize(images, imageNo, bitDepthStr, threshold, gridx, gridy)
%LOADANDNORMALIZE  Load image, normalize, apply threshold, and extract ROI.
%   [cur_img, cur_img_binary, cur_img_ROI, cur_img_binary_ROI] = ...
%       bubblefit.imageproc.loadAndNormalize(images, imageNo, bitDepthStr, threshold, gridx, gridy)
%
%   Inputs:
%     images       - cell array of image file paths
%     imageNo      - index of current image
%     bitDepthStr  - bit depth string from dropdown (e.g., '16')
%     threshold    - normalized threshold value (0 to 1)
%     gridx        - [row_start, row_end] ROI bounds
%     gridy        - [col_start, col_end] ROI bounds
%
%   Outputs:
%     cur_img            - normalized image [0, max]
%     cur_img_binary     - binary image after threshold
%     cur_img_ROI        - ROI of normalized image
%     cur_img_binary_ROI - ROI of binary image

    temp_img = imread(images{imageNo});
    bitsPerChannel = str2double(bitDepthStr) / size(temp_img, 3);
    ref_img = double(imread(images{1})) / (2^bitsPerChannel - 1);
    temp_cur_img = double(imread(images{imageNo})) / (2^bitsPerChannel - 1);

    % If RGB, convert to grayscale
    if size(ref_img, 3) == 3
        ref_img = rgb2gray(ref_img);
        temp_cur_img = rgb2gray(temp_cur_img);
    end

    % Normalize to [0, max]
    cur_img = (max(temp_cur_img(:)) - min(temp_cur_img(:))) * ...
              (temp_cur_img - min(temp_cur_img(:)));

    % Apply threshold
    cur_img_binary = cur_img > threshold;

    % Extract ROI
    cur_img_ROI = cur_img(gridx(1):gridx(2), gridy(1):gridy(2));
    cur_img_binary_ROI = cur_img_binary(gridx(1):gridx(2), gridy(1):gridy(2));

end
