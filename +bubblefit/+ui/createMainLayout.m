function createMainLayout(app)
%CREATEMAINLAYOUT  Create UIFigure, GridLayout, and three Axes.

    % Create UIFigure and hide until all components are created
    app.UIFigure = uifigure('Visible', 'off');
    app.UIFigure.Position = [100 100 1500 772];
    app.UIFigure.Name = 'MATLAB App';

    % Create GridLayout
    app.GridLayout = uigridlayout(app.UIFigure);
    app.GridLayout.ColumnWidth = {35, 61, 39, 61, 104, '3x', '3x'};
    app.GridLayout.RowHeight = {20, 20, 23, 0, 30, 22, '2.1x', 22, 0, 85, '1.3x', 0, '1.5x'};
    app.GridLayout.ColumnSpacing = 12;
    app.GridLayout.RowSpacing = 12;

    % Create UIAxes_raw
    app.UIAxes_raw = uiaxes(app.GridLayout);
    title(app.UIAxes_raw, 'Raw image (Red-detected bubble edge; Blue-fitting; Green: ROI)      Image # ')
    xlabel(app.UIAxes_raw, 'X [px]')
    ylabel(app.UIAxes_raw, 'Y [px]')
    zlabel(app.UIAxes_raw, 'Z')
    app.UIAxes_raw.Layout.Row = [3 9];
    app.UIAxes_raw.Layout.Column = 6;

    % Create UIAxes_Rtcurve
    app.UIAxes_Rtcurve = uiaxes(app.GridLayout);
    title(app.UIAxes_Rtcurve, 'Radius - time curve')
    xlabel(app.UIAxes_Rtcurve, 'Frame No.')
    ylabel(app.UIAxes_Rtcurve, 'Rad [px]')
    zlabel(app.UIAxes_Rtcurve, 'Z')
    app.UIAxes_Rtcurve.XMinorTick = 'on';
    app.UIAxes_Rtcurve.YMinorTick = 'on';
    app.UIAxes_Rtcurve.Layout.Row = [9 13];
    app.UIAxes_Rtcurve.Layout.Column = [6 7];

    % Create UIAxes_binary
    app.UIAxes_binary = uiaxes(app.GridLayout);
    title(app.UIAxes_binary, 'Binary Image (selected ROI)   Image # ')
    xlabel(app.UIAxes_binary, 'X [px]')
    ylabel(app.UIAxes_binary, 'Y [px]')
    zlabel(app.UIAxes_binary, 'Z')
    app.UIAxes_binary.Layout.Row = [3 9];
    app.UIAxes_binary.Layout.Column = 7;

end
