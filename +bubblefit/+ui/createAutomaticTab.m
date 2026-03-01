function createAutomaticTab(app)
%CREATEAUTOMATICTAB  Create Automatic tab and its child components.

    % Create AutomaticTab
    app.AutomaticTab = uitab(app.TabGroup);
    app.AutomaticTab.Title = 'Automatic';

    % Create FittingandPreviewButton_2
    app.FittingandPreviewButton_2 = uibutton(app.AutomaticTab, 'push');
    app.FittingandPreviewButton_2.ButtonPushedFcn = @(src,event)FittingandPreviewButton_2Pushed(app,event);
    app.FittingandPreviewButton_2.Position = [14 73 322 28];
    app.FittingandPreviewButton_2.Text = 'Fitting and Preview';

    % Create LEditField_D3
    app.LEditField_D3 = uieditfield(app.AutomaticTab, 'numeric');
    app.LEditField_D3.Limits = [1 Inf];
    app.LEditField_D3.ValueDisplayFormat = '%.0f';
    app.LEditField_D3.Position = [301 183 32 22];
    app.LEditField_D3.Value = 1;

    % Create LEditFieldLabel_5
    app.LEditFieldLabel_5 = uilabel(app.AutomaticTab);
    app.LEditFieldLabel_5.HorizontalAlignment = 'right';
    app.LEditFieldLabel_5.Position = [269 183 25 22];
    app.LEditFieldLabel_5.Text = 'D';
    app.LEditFieldLabel_5.Tooltip = 'Down boundary of ROI (pixels)';

    % Create LEditField_U3
    app.LEditField_U3 = uieditfield(app.AutomaticTab, 'numeric');
    app.LEditField_U3.Limits = [1 Inf];
    app.LEditField_U3.ValueDisplayFormat = '%.0f';
    app.LEditField_U3.Position = [239 183 32 22];
    app.LEditField_U3.Value = 1;

    % Create LEditFieldLabel_6
    app.LEditFieldLabel_6 = uilabel(app.AutomaticTab);
    app.LEditFieldLabel_6.HorizontalAlignment = 'right';
    app.LEditFieldLabel_6.Position = [207 183 25 22];
    app.LEditFieldLabel_6.Text = 'U';
    app.LEditFieldLabel_6.Tooltip = 'Upper boundary of ROI (pixels)';

    % Create LEditField_7Label
    app.LEditField_7Label = uilabel(app.AutomaticTab);
    app.LEditField_7Label.HorizontalAlignment = 'right';
    app.LEditField_7Label.Position = [89 183 11 22];
    app.LEditField_7Label.Text = 'L';
    app.LEditField_7Label.Tooltip = 'Left boundary of ROI (pixels)';

    % Create LEditField_L3
    app.LEditField_L3 = uieditfield(app.AutomaticTab, 'numeric');
    app.LEditField_L3.Limits = [1 Inf];
    app.LEditField_L3.ValueDisplayFormat = '%.0f';
    app.LEditField_L3.Position = [107 183 32 22];
    app.LEditField_L3.Value = 1;

    % Create LEditField_R3
    app.LEditField_R3 = uieditfield(app.AutomaticTab, 'numeric');
    app.LEditField_R3.Limits = [1 Inf];
    app.LEditField_R3.ValueDisplayFormat = '%.0f';
    app.LEditField_R3.Position = [174 184 32 22];
    app.LEditField_R3.Value = 1;

    % Create LEditFieldLabel_7
    app.LEditFieldLabel_7 = uilabel(app.AutomaticTab);
    app.LEditFieldLabel_7.HorizontalAlignment = 'right';
    app.LEditFieldLabel_7.Position = [142 184 25 22];
    app.LEditFieldLabel_7.Text = 'R';
    app.LEditFieldLabel_7.Tooltip = 'Right boundary of ROI (pixels)';

    % Create ROIButton_2
    app.ROIButton_2 = uibutton(app.AutomaticTab, 'push');
    app.ROIButton_2.ButtonPushedFcn = @(src,event)ROIButton_2Pushed(app,event);
    app.ROIButton_2.Position = [13 181 56 23];
    app.ROIButton_2.Text = 'ROI';

    % Create ImageEditField_2Label
    app.ImageEditField_2Label = uilabel(app.AutomaticTab);
    app.ImageEditField_2Label.HorizontalAlignment = 'right';
    app.ImageEditField_2Label.Position = [9 255 52 22];
    app.ImageEditField_2Label.Text = 'Image #';

    % Create startNum
    app.startNum = uieditfield(app.AutomaticTab, 'numeric');
    app.startNum.Limits = [1 Inf];
    app.startNum.ValueDisplayFormat = '%.0f';
    app.startNum.Position = [76 255 41 22];
    app.startNum.Value = 1;

    % Create toLabel
    app.toLabel = uilabel(app.AutomaticTab);
    app.toLabel.Position = [131 255 25 22];
    app.toLabel.Text = 'to';

    % Create endNum
    app.endNum = uieditfield(app.AutomaticTab, 'numeric');
    app.endNum.Limits = [1 Inf];
    app.endNum.ValueDisplayFormat = '%.0f';
    app.endNum.Position = [151 255 41 22];
    app.endNum.Value = 1;

    % Create ClearandrefreshButton_2
    app.ClearandrefreshButton_2 = uibutton(app.AutomaticTab, 'push');
    app.ClearandrefreshButton_2.ButtonPushedFcn = @(src,event)ClearandrefreshButton_2Pushed(app,event);
    app.ClearandrefreshButton_2.Position = [215 35 120 30];
    app.ClearandrefreshButton_2.Text = 'Clear and refresh';

    % Create LoadtunedparametersButton
    app.LoadtunedparametersButton = uibutton(app.AutomaticTab, 'push');
    app.LoadtunedparametersButton.ButtonPushedFcn = @(src,event)LoadtunedparametersButtonPushed(app,event);
    app.LoadtunedparametersButton.Position = [13 217 317 28];
    app.LoadtunedparametersButton.Text = 'Load tuned parameters';

    % Create RealtimeplayCheckBox
    app.RealtimeplayCheckBox = uicheckbox(app.AutomaticTab);
    app.RealtimeplayCheckBox.Text = 'Realtime play';
    app.RealtimeplayCheckBox.Tooltip = 'Checked: show each frame (slower). Unchecked: batch mode with progress bar (faster)';
    app.RealtimeplayCheckBox.Position = [14 44 95 22];
    app.RealtimeplayCheckBox.Value = true;

    % Create StopButton
    app.StopButton = uibutton(app.AutomaticTab, 'push');
    app.StopButton.ButtonPushedFcn = @(src,event)StopButtonPushed(app,event);
    app.StopButton.Position = [120 35 80 30];
    app.StopButton.Text = 'Stop';

end
