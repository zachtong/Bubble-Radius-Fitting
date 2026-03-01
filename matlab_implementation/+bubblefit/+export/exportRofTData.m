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

    % Check if the Rmax_fit_length is legal (both boundaries)
    if RmaxTimeLoctemp - RmaxFitHalfLength < 1
        success = false;
        msg = 'Rmax_Fit_Length exceeds data range (left boundary)!';
        return;
    end
    if RmaxTimeLoctemp + RmaxFitHalfLength > length(R)
        success = false;
        msg = 'Rmax_Fit_Length exceeds data range (right boundary)!';
        return;
    end

    RmaxTimeLoctempList = (RmaxTimeLoctemp - RmaxFitHalfLength : ...
                           RmaxTimeLoctemp + RmaxFitHalfLength)';
    RmaxtempList = R(RmaxTimeLoctempList);

    % Do quadratic fitting for a more accurate Rmax
    try
        p = polyfit(RmaxTimeLoctempList, RmaxtempList, 2);

        % Validate: parabola must open downward (p(1) < 0) for a maximum
        if p(1) >= 0
            warning('bubblefit:invalidFit', ...
                'Quadratic fit is not concave (p(1)=%.4g); using discrete Rmax.', p(1));
            RmaxAlltemp = Rmaxtemp;
        else
            fitTimeLoc = -p(2) / 2 / p(1);
            fitRmax = (4*p(1)*p(3) - p(2)^2) / (4*p(1));

            % Validate: interpolated peak must be within data range
            if fitTimeLoc < 1 || fitTimeLoc > length(R)
                warning('bubblefit:peakOutOfRange', ...
                    'Interpolated Rmax at t=%.1f is out of data range [1, %d]; using discrete Rmax.', ...
                    fitTimeLoc, length(R));
                RmaxAlltemp = Rmaxtemp;
            else
                RmaxTimeLoctemp = fitTimeLoc;
                RmaxAlltemp = fitRmax;
            end
        end
    catch
        RmaxAlltemp = Rmaxtemp;
    end

    % Assign variables with physical units
    R = [R(t < RmaxTimeLoctemp); RmaxAlltemp; R(t > RmaxTimeLoctemp)] * deltax;
    t = [t(t < RmaxTimeLoctemp) - RmaxTimeLoctemp; 0; ...
         t(t > RmaxTimeLoctemp) - RmaxTimeLoctemp] * deltat;
    RmaxAll = RmaxAlltemp * deltax;
    RmaxTimeLoc = RmaxTimeLoctemp * deltat;

    savePath2 = fullfile(fileparts(savePath), 'RofTdata.mat');
    save(savePath2, 't', 'R', 'RmaxAll', 'RmaxTimeLoc');

    success = true;
    msg = '';

end
