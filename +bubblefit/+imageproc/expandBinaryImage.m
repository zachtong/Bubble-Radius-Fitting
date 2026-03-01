function expandedBw = expandBinaryImage(bw, bubbleCrossEdges)
%EXPANDBINARYIMAGE  Expand binary image to handle edge-crossing bubbles.
%   expandedBw = bubblefit.imageproc.expandBinaryImage(bw, bubbleCrossEdges)
%
%   Doubles the image in the first non-crossing direction, filling the
%   expansion with ones (white), so that a bubble touching an edge does not
%   get merged with the background during connected-component analysis.
%
%   Inputs:
%     bw               - binary ROI image
%     bubbleCrossEdges - 1x4 logical [Top, Right, Down, Left]: 1 = bubble crosses that edge
%
%   Output:
%     expandedBw       - expanded binary image

    [originalRows, originalCols] = size(bw);
    bubbleNonCrossEdges = ~bubbleCrossEdges;
    % Element_1,2,3,4 = TOP, RIGHT, DOWN, LEFT
    % e.g. bubbleCrossEdges = [1 1 0 0] means the bubble will cross top and right
    % edges during process
    ExpandDirection = find(bubbleNonCrossEdges == 1);
    ExpandDirection = ExpandDirection(1); % use the first allowable direction

    if ExpandDirection == 1
        expandedBw = ones(originalRows * 2, originalCols);
        expandedBw(originalRows+1:2*originalRows,1:originalCols) = bw;
    elseif ExpandDirection == 2
        expandedBw = ones(originalRows, originalCols *2);
        expandedBw(1:originalRows,1:originalCols) = bw;
    elseif ExpandDirection == 3
        expandedBw = ones(originalRows * 2, originalCols);
        expandedBw(1:originalRows,1:originalCols) = bw;
    elseif ExpandDirection == 4
        expandedBw = ones(originalRows, originalCols *2);
        expandedBw(1:originalRows,originalCols+1:2*originalCols) = bw;
    end

end
