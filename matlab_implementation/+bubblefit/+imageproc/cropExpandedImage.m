function cropped = cropExpandedImage(expandedImg, originalRows, originalCols, bubbleCrossEdges)
%CROPEXPANDEDIMAGE  Crop expanded image back to original ROI dimensions.
%   cropped = bubblefit.imageproc.cropExpandedImage(expandedImg, originalRows, originalCols, bubbleCrossEdges)
%
%   Reverses the expansion done by expandBinaryImage.
%
%   Inputs:
%     expandedImg      - expanded binary image
%     originalRows     - original ROI row count
%     originalCols     - original ROI column count
%     bubbleCrossEdges - 1x4 logical [Top, Right, Down, Left]
%
%   Output:
%     cropped          - image cropped back to [originalRows x originalCols]

    bubbleNonCrossEdges = ~bubbleCrossEdges;
    ExpandDirection = find(bubbleNonCrossEdges == 1);
    ExpandDirection = ExpandDirection(1);

    if ExpandDirection == 1
        cropped = expandedImg(originalRows+1:2*originalRows,1:originalCols);
    elseif ExpandDirection == 2
        cropped = expandedImg(1:originalRows,1:originalCols);
    elseif ExpandDirection == 3
        cropped = expandedImg(1:originalRows,1:originalCols);
    elseif ExpandDirection == 4
        cropped = expandedImg(1:originalRows,originalCols+1:2*originalCols);
    end

end
