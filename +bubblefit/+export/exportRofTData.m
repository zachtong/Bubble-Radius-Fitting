function [success, msg] = exportRofTData(savePath, Radius, um2px, FPS, Rmax_Fit_Length)
%EXPORTROFTDATA  Convert pixel radius data to physical units and export.
%   [success, msg] = bubblefit.export.exportRofTData(savePath, Radius, um2px, FPS, Rmax_Fit_Length)
%
%   Computes Rmax via quadratic interpolation around the peak, shifts time
%   so Rmax is at t=0, converts to physical units, and saves to RofTdata.mat.
%
%   Inputs:
%     savePath         - base save path (RofTdata.mat saved in same folder)
%     Radius           - 1xN array of fitted radii (pixels)
%     um2px            - micrometers per pixel conversion factor
%     FPS              - frames per second
%     Rmax_Fit_Length   - window size for quadratic fitting around Rmax
%
%   Outputs:
%     success - true if export succeeded
%     msg     - error message (empty on success)

    deltax = um2px;
    deltat = 1 / FPS;
    RmaxFitHalfLength = round((Rmax_Fit_Length - 1) / 2);

    R = Radius'; R = R(:);
    t = (1:length(R))'; t = t(:);

    [Rmaxtemp, RmaxTimeLoctemp] = max(R); % Find Rmax discrete

    % Check if the Rmax_fit_length is legal
    if RmaxTimeLoctemp - RmaxFitHalfLength < 1
        success = false;
        msg = 'Please check your Rmax_Fit_length!';
        return;
    end

    RmaxTimeLoctempList = (RmaxTimeLoctemp - RmaxFitHalfLength : ...
                           RmaxTimeLoctemp + RmaxFitHalfLength)';
    RmaxtempList = R(RmaxTimeLoctempList);

    % Do quadratic fitting for a more accurate Rmax
    try
        p = polyfit(RmaxTimeLoctempList, RmaxtempList, 2);
        RmaxTimeLoctemp = -p(2) / 2 / p(1);
        RmaxAlltemp = (4*p(1)*p(3) - p(2)^2) / (4*p(1));
    catch
        RmaxAlltemp = Rmaxtemp;
    end

    % Assign variables with physical units
    R = [R(t < RmaxTimeLoctemp); RmaxAlltemp; R(t > RmaxTimeLoctemp)] * deltax;
    t = [t(t < RmaxTimeLoctemp) - RmaxTimeLoctemp; 0; ...
         t(t > RmaxTimeLoctemp) - RmaxTimeLoctemp] * deltat;
    RmaxAll = RmaxAlltemp * deltax;
    RmaxTimeLoc = RmaxTimeLoctemp * deltat;

    savePath2 = [fileparts(savePath), '/RofTdata.mat'];
    save(savePath2, 't', 'R', 'RmaxAll', 'RmaxTimeLoc');

    success = true;
    msg = '';

end
