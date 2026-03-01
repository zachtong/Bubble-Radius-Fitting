function createPretuneTab(app)
%CREATEPRETUNETAB  Create Pre-tune tab and its child components.

    % Create PretuneTab
    app.PretuneTab = uitab(app.TabGroup);
    app.PretuneTab.Title = 'Pre-tune';

    % Create ROIButton
    app.ROIButton = uibutton(app.PretuneTab, 'push');
    app.ROIButton.ButtonPushedFcn = @(src,event)ROIButtonPushed(app,event);
    app.ROIButton.Position = [15 220 56 23];
    app.ROIButton.Text = 'ROI';

    % Create LEditFieldLabel
    app.LEditFieldLabel = uilabel(app.PretuneTab);
    app.LEditFieldLabel.HorizontalAlignment = 'right';
    app.LEditFieldLabel.Position = [91 219 11 22];
    app.LEditFieldLabel.Text = 'L';

    % Create LEditField_L1
    app.LEditField_L1 = uieditfield(app.PretuneTab, 'numeric');
    app.LEditField_L1.Limits = [1 Inf];
    app.LEditField_L1.ValueDisplayFormat = '%.0f';
    app.LEditField_L1.HorizontalAlignment = 'left';
    app.LEditField_L1.Position = [109 219 32 22];
    app.LEditField_L1.Value = 1;

    % Create LEditField_R1
    app.LEditField_R1 = uieditfield(app.PretuneTab, 'numeric');
    app.LEditField_R1.Limits = [1 Inf];
    app.LEditField_R1.ValueDisplayFormat = '%.0f';
    app.LEditField_R1.HorizontalAlignment = 'left';
    app.LEditField_R1.Position = [176 220 32 22];
    app.LEditField_R1.Value = 1;

    % Create LEditFieldLabel_2
    app.LEditFieldLabel_2 = uilabel(app.PretuneTab);
    app.LEditFieldLabel_2.HorizontalAlignment = 'right';
    app.LEditFieldLabel_2.Position = [144 220 25 22];
    app.LEditFieldLabel_2.Text = 'R';

    % Create LEditField_U1
    app.LEditField_U1 = uieditfield(app.PretuneTab, 'numeric');
    app.LEditField_U1.Limits = [1 Inf];
    app.LEditField_U1.ValueDisplayFormat = '%.0f';
    app.LEditField_U1.HorizontalAlignment = 'left';
    app.LEditField_U1.Position = [241 219 32 22];
    app.LEditField_U1.Value = 1;

    % Create LEditFieldLabel_3
    app.LEditFieldLabel_3 = uilabel(app.PretuneTab);
    app.LEditFieldLabel_3.HorizontalAlignment = 'right';
    app.LEditFieldLabel_3.Position = [209 219 25 22];
    app.LEditFieldLabel_3.Text = 'U';

    % Create LEditField_D1
    app.LEditField_D1 = uieditfield(app.PretuneTab, 'numeric');
    app.LEditField_D1.Limits = [1 Inf];
    app.LEditField_D1.ValueDisplayFormat = '%.0f';
    app.LEditField_D1.HorizontalAlignment = 'left';
    app.LEditField_D1.Position = [303 219 32 22];
    app.LEditField_D1.Value = 1;

    % Create LEditFieldLabel_4
    app.LEditFieldLabel_4 = uilabel(app.PretuneTab);
    app.LEditFieldLabel_4.HorizontalAlignment = 'right';
    app.LEditFieldLabel_4.Position = [271 219 25 22];
    app.LEditFieldLabel_4.Text = 'D';

    % Create ImageEditFieldLabel
    app.ImageEditFieldLabel = uilabel(app.PretuneTab);
    app.ImageEditFieldLabel.HorizontalAlignment = 'right';
    app.ImageEditFieldLabel.Position = [9 255 52 22];
    app.ImageEditFieldLabel.Text = 'Image  #';

    % Create ImageEditField
    app.ImageEditField = uieditfield(app.PretuneTab, 'numeric');
    app.ImageEditField.Limits = [1 Inf];
    app.ImageEditField.ValueDisplayFormat = '%.0f';
    app.ImageEditField.ValueChangedFcn = @(src,event)ImageEditFieldValueChanged(app,event);
    app.ImageEditField.HorizontalAlignment = 'left';
    app.ImageEditField.Position = [76 255 41 22];
    app.ImageEditField.Value = 1;

    % Create FittingandPreviewButton
    app.FittingandPreviewButton = uibutton(app.PretuneTab, 'push');
    app.FittingandPreviewButton.ButtonPushedFcn = @(src,event)FittingandPreviewButtonPushed(app,event);
    app.FittingandPreviewButton.Position = [15 8 178 28];
    app.FittingandPreviewButton.Text = 'Fitting and Preview';

    % Create ClearandrefreshButton
    app.ClearandrefreshButton = uibutton(app.PretuneTab, 'push');
    app.ClearandrefreshButton.ButtonPushedFcn = @(src,event)ClearandrefreshButtonPushed(app,event);
    app.ClearandrefreshButton.Position = [213 8 120 30];
    app.ClearandrefreshButton.Text = 'Clear and refresh';

    % Create LeftEdgeOrNot
    app.LeftEdgeOrNot = uicheckbox(app.PretuneTab);
    app.LeftEdgeOrNot.Text = 'Left';
    app.LeftEdgeOrNot.Position = [99 179 42 22];

    % Create RightEdgeOrNot
    app.RightEdgeOrNot = uicheckbox(app.PretuneTab);
    app.RightEdgeOrNot.Text = 'Right';
    app.RightEdgeOrNot.Position = [155 178 50 22];

    % Create TopEdgeOrNot
    app.TopEdgeOrNot = uicheckbox(app.PretuneTab);
    app.TopEdgeOrNot.Text = 'Top';
    app.TopEdgeOrNot.Position = [219 178 41 22];

    % Create DownEdgeOrNot
    app.DownEdgeOrNot = uicheckbox(app.PretuneTab);
    app.DownEdgeOrNot.Text = 'Down';
    app.DownEdgeOrNot.Position = [271 179 53 22];

    % Create BubblecrossgreenedgesLabel
    app.BubblecrossgreenedgesLabel = uilabel(app.PretuneTab);
    app.BubblecrossgreenedgesLabel.Position = [19 176 78 30];
    app.BubblecrossgreenedgesLabel.Text = {'Bubble cross'; 'green edges?'};

    % Create ThresholdLabel
    app.ThresholdLabel = uilabel(app.PretuneTab);
    app.ThresholdLabel.HorizontalAlignment = 'right';
    app.ThresholdLabel.Position = [69 144 58 22];
    app.ThresholdLabel.Text = 'Threshold';

    % Create SliderThreshold
    app.SliderThreshold = uislider(app.PretuneTab);
    app.SliderThreshold.ValueChangingFcn = @(src,event)SliderThresholdValueChanging(app,event);
    app.SliderThreshold.Position = [11 132 137 3];
    app.SliderThreshold.Value = 50;

    % Create SliderConnectedArea
    app.SliderConnectedArea = uislider(app.PretuneTab);
    app.SliderConnectedArea.ValueChangedFcn = @(src,event)SliderConnectedAreaValueChanged(app,event);
    app.SliderConnectedArea.ValueChangingFcn = @(src,event)SliderConnectedAreaValueChanging(app,event);
    app.SliderConnectedArea.Position = [181 132 140 3];
    app.SliderConnectedArea.Value = 50;

    % Create RemovingfactorLabel
    app.RemovingfactorLabel = uilabel(app.PretuneTab);
    app.RemovingfactorLabel.HorizontalAlignment = 'right';
    app.RemovingfactorLabel.Position = [204 144 96 22];
    app.RemovingfactorLabel.Text = 'Removing  factor';

    % Create ThresholdEditFieldLabel
    app.ThresholdEditFieldLabel = uilabel(app.PretuneTab);
    app.ThresholdEditFieldLabel.HorizontalAlignment = 'right';
    app.ThresholdEditFieldLabel.Position = [33 61 58 22];
    app.ThresholdEditFieldLabel.Text = 'Threshold';

    % Create ThresholdEditField
    app.ThresholdEditField = uieditfield(app.PretuneTab, 'numeric');
    app.ThresholdEditField.ValueChangedFcn = @(src,event)ThresholdEditFieldValueChanged(app,event);
    app.ThresholdEditField.Position = [106 59 42 26];

    % Create RemovingFactorEditFieldLabel
    app.RemovingFactorEditFieldLabel = uilabel(app.PretuneTab);
    app.RemovingFactorEditFieldLabel.HorizontalAlignment = 'right';
    app.RemovingFactorEditFieldLabel.Position = [179 61 93 22];
    app.RemovingFactorEditFieldLabel.Text = 'RemovingFactor';

    % Create RemovingFactorEditField
    app.RemovingFactorEditField = uieditfield(app.PretuneTab, 'numeric');
    app.RemovingFactorEditField.ValueChangedFcn = @(src,event)RemovingFactorEditFieldValueChanged(app,event);
    app.RemovingFactorEditField.Position = [287 61 45 22];

end
