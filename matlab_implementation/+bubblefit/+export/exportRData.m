function exportRData(savePath, Radius, CircleFitPar, CircleXY)
%EXPORTRDATA  Export circle fitting results to R_data.mat.
%   bubblefit.export.exportRData(savePath, Radius, CircleFitPar, CircleXY)
%
%   Inputs:
%     savePath     - full file path for output .mat file
%     Radius       - 1xN array of fitted radii
%     CircleFitPar - Nx2 array of circle center coordinates
%     CircleXY     - cell array of edge point coordinates

    CircleR = Radius';
    CircleCenterSave = CircleFitPar;
    CircleEdgePtSave = CircleXY;

    save(savePath, 'CircleR', 'CircleCenterSave', 'CircleEdgePtSave');

end
