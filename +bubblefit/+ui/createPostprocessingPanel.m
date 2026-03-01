function createPostprocessingPanel(app)
%CREATEPOSTPROCESSINGPANEL  Create post-processing panel with export controls.

    % Create PostprocessingPanel
    app.PostprocessingPanel = uipanel(app.GridLayout);
    app.PostprocessingPanel.Title = 'Post processing';
    app.PostprocessingPanel.Layout.Row = [11 13];
    app.PostprocessingPanel.Layout.Column = [1 5];

    % Create ExporttoR_datamatPanel
    app.ExporttoR_datamatPanel = uipanel(app.PostprocessingPanel);
    app.ExporttoR_datamatPanel.Title = 'Export to "R_data.mat"';
    app.ExporttoR_datamatPanel.Position = [16 104 305 124];

    % Create ExportButton
    app.ExportButton = uibutton(app.ExporttoR_datamatPanel, 'push');
    app.ExportButton.ButtonPushedFcn = createCallbackFcn(app, @ExportButtonPushed, true);
    app.ExportButton.Position = [194 52 100 43];
    app.ExportButton.Text = 'Export';

    % Create StoretoanotherpathButton
    app.StoretoanotherpathButton = uibutton(app.ExporttoR_datamatPanel, 'push');
    app.StoretoanotherpathButton.ButtonPushedFcn = createCallbackFcn(app, @StoretoanotherpathButtonPushed, true);
    app.StoretoanotherpathButton.Position = [13 45 163 23];
    app.StoretoanotherpathButton.Text = 'Store to another path';

    % Create UsedefaultpathButton
    app.UsedefaultpathButton = uibutton(app.ExporttoR_datamatPanel, 'push');
    app.UsedefaultpathButton.ButtonPushedFcn = createCallbackFcn(app, @UsedefaultpathButtonPushed, true);
    app.UsedefaultpathButton.Position = [13 73 163 23];
    app.UsedefaultpathButton.Text = 'Use default path';

    % Create ExportpathEditFieldLabel
    app.ExportpathEditFieldLabel = uilabel(app.ExporttoR_datamatPanel);
    app.ExportpathEditFieldLabel.HorizontalAlignment = 'right';
    app.ExportpathEditFieldLabel.Position = [5 11 66 22];
    app.ExportpathEditFieldLabel.Text = 'Export path';

    % Create ExportpathEditField
    app.ExportpathEditField = uieditfield(app.ExporttoR_datamatPanel, 'text');
    app.ExportpathEditField.ValueChangedFcn = createCallbackFcn(app, @ExportpathEditFieldValueChanged, true);
    app.ExportpathEditField.Position = [84 11 206 22];

    % Create ConverttophysicalworldunitsasRofTdatamatPanel
    app.ConverttophysicalworldunitsasRofTdatamatPanel = uipanel(app.PostprocessingPanel);
    app.ConverttophysicalworldunitsasRofTdatamatPanel.Title = 'Convert to physical world units as "RofTdata.mat"';
    app.ConverttophysicalworldunitsasRofTdatamatPanel.Position = [16 9 305 92];

    % Create FPSEditFieldLabel
    app.FPSEditFieldLabel = uilabel(app.ConverttophysicalworldunitsasRofTdatamatPanel);
    app.FPSEditFieldLabel.HorizontalAlignment = 'right';
    app.FPSEditFieldLabel.Position = [14 41 28 22];
    app.FPSEditFieldLabel.Text = 'FPS';

    % Create FPSEditField
    app.FPSEditField = uieditfield(app.ConverttophysicalworldunitsasRofTdatamatPanel, 'numeric');
    app.FPSEditField.Limits = [1 Inf];
    app.FPSEditField.ValueChangedFcn = createCallbackFcn(app, @FPSEditFieldValueChanged, true);
    app.FPSEditField.HorizontalAlignment = 'left';
    app.FPSEditField.Position = [50 41 70 22];
    app.FPSEditField.Value = 1000000;

    % Create um2pxEditFieldLabel
    app.um2pxEditFieldLabel = uilabel(app.ConverttophysicalworldunitsasRofTdatamatPanel);
    app.um2pxEditFieldLabel.HorizontalAlignment = 'right';
    app.um2pxEditFieldLabel.Position = [1 11 41 22];
    app.um2pxEditFieldLabel.Text = 'um2px';

    % Create um2pxEditField
    app.um2pxEditField = uieditfield(app.ConverttophysicalworldunitsasRofTdatamatPanel, 'numeric');
    app.um2pxEditField.Limits = [0.001 Inf];
    app.um2pxEditField.ValueChangedFcn = createCallbackFcn(app, @um2pxEditFieldValueChanged, true);
    app.um2pxEditField.HorizontalAlignment = 'left';
    app.um2pxEditField.Position = [50 11 70 22];
    app.um2pxEditField.Value = 3.2;

    % Create ExportButton_2
    app.ExportButton_2 = uibutton(app.ConverttophysicalworldunitsasRofTdatamatPanel, 'push');
    app.ExportButton_2.ButtonPushedFcn = createCallbackFcn(app, @ExportButton_2Pushed, true);
    app.ExportButton_2.Position = [183 12 100 21];
    app.ExportButton_2.Text = 'Export';

    % Create FitRmaxafterframeEditFieldLabel
    app.FitRmaxafterframeEditFieldLabel = uilabel(app.ConverttophysicalworldunitsasRofTdatamatPanel);
    app.FitRmaxafterframeEditFieldLabel.HorizontalAlignment = 'right';
    app.FitRmaxafterframeEditFieldLabel.Position = [140 41 121 22];
    app.FitRmaxafterframeEditFieldLabel.Text = 'Fit Rmax after frame#';

    % Create FitRmaxafterframeEditField
    app.FitRmaxafterframeEditField = uieditfield(app.ConverttophysicalworldunitsasRofTdatamatPanel, 'numeric');
    app.FitRmaxafterframeEditField.Limits = [3 Inf];
    app.FitRmaxafterframeEditField.ValueDisplayFormat = '%.0f';
    app.FitRmaxafterframeEditField.ValueChangedFcn = createCallbackFcn(app, @FitRmaxafterframeEditFieldValueChanged, true);
    app.FitRmaxafterframeEditField.HorizontalAlignment = 'left';
    app.FitRmaxafterframeEditField.Position = [265 41 30 22];
    app.FitRmaxafterframeEditField.Value = 11;

end
