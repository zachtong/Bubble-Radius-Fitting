function [bws2, edgeXY] = detectBubble(binaryROI, bubbleCrossEdges, removingFactor, ...
    removeobjradius, BigOrSmall, gridx, gridy)
%DETECTBUBBLE  Detect bubble boundary in binary ROI image.
%   [bws2, edgeXY] = bubblefit.imageproc.detectBubble(binaryROI, bubbleCrossEdges,
%       removingFactor, removeobjradius, BigOrSmall, gridx, gridy)
%
%   Pipeline: expand image -> remove small areas -> find largest blob ->
%   crop back -> boundary extraction.
%
%   Inputs:
%     binaryROI        - binary ROI image
%     bubbleCrossEdges - 1x4 logical [Top, Right, Down, Left]
%     removingFactor   - minimum connected area size (pixels) to keep
%     removeobjradius  - morphological closing disk radius (0 = skip)
%     BigOrSmall       - 0 = small bubble (default), 1 = big bubble (TBD)
%     gridx            - [row_start, row_end] ROI bounds in full image
%     gridy            - [col_start, col_end] ROI bounds in full image
%
%   Outputs:
%     bws2   - processed binary image (original ROI size) showing detected bubble
%     edgeXY - N-by-2 array of edge coordinates in full-image space [row, col]

    % Named constants for connected component filtering
    MAX_AXIS_RATIO = 2.2;      % max major axis vs image short side
    MAX_ECCENTRICITY = 1.6;    % max major/minor axis ratio
    MIN_HOLE_AREA = 40;        % min area for hole removal after blob selection

    bw = binaryROI;
    [originalRows, originalCols] = size(bw);

    % Expand image to handle edge-crossing bubbles
    expandedBw = bubblefit.imageproc.expandBinaryImage(bw, bubbleCrossEdges);

    % Remove small connected areas
    expandedBw = bwareaopen(expandedBw, removingFactor);

    % Optional morphological closing
    if removeobjradius > 1
        se = strel('disk', removeobjradius);
        expandedBw = imclose(expandedBw, se);
        expandedBw = imfill(expandedBw, 'holes');
        expandedBw = imfill(expandedBw, 'holes');
    end

    if BigOrSmall == 1 % Big bubble
        % TBD
        bws2 = expandedBw;
    else
        bws = 1 - expandedBw;
        CC = bwconncomp(bws);
        props = regionprops(CC, 'Area', 'PixelIdxList', 'MajorAxisLength', 'MinorAxisLength');
        for tempjj = 1:length(props)
            if props(tempjj).MajorAxisLength > MAX_AXIS_RATIO*min(size(bws)) || ...
               props(tempjj).MajorAxisLength > MAX_ECCENTRICITY*props(tempjj).MinorAxisLength
                props(tempjj).Area = 0;
            end
        end
        [~, indexOfMax] = max([props.Area]);

        largestBlobIndexes = props(indexOfMax).PixelIdxList;

        bws2 = false(size(bws));
        bws2(largestBlobIndexes) = 1; % Only keep the largest blob area

        bws2 = bwareaopen(double(1-bws2), MIN_HOLE_AREA);
        bws2 = 1 - bws2; % Flip white and black colors
    end

    % Crop back to original size
    bws2 = bubblefit.imageproc.cropExpandedImage(bws2, originalRows, originalCols, bubbleCrossEdges);

    % Edge detection
    edgebws2 = edge(bws2);
    [row, col] = find(edgebws2 == 1);

    % Convert to full-image coordinates
    edgeXY = [row + gridx(1) - 1, col + gridy(1) - 1];

end
