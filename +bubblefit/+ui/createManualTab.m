function createManualTab(app)
%CREATEMANUALTAB  Create Manual tab and its child components.

    % Create ManualTab
    app.ManualTab = uitab(app.TabGroup);
    app.ManualTab.Title = 'Manual';

    % Create ImageEditField_2Label_2
    app.ImageEditField_2Label_2 = uilabel(app.ManualTab);
    app.ImageEditField_2Label_2.HorizontalAlignment = 'right';
    app.ImageEditField_2Label_2.Position = [9 255 52 22];
    app.ImageEditField_2Label_2.Text = 'Image  #';

    % Create ImageEditField_2
    app.ImageEditField_2 = uieditfield(app.ManualTab, 'numeric');
    app.ImageEditField_2.Limits = [1 Inf];
    app.ImageEditField_2.ValueDisplayFormat = '%.0f';
    app.ImageEditField_2.HorizontalAlignment = 'left';
    app.ImageEditField_2.Position = [76 255 41 22];
    app.ImageEditField_2.Value = 1;

    % Create ManuallyselectbubbleedgepointsButton
    app.ManuallyselectbubbleedgepointsButton = uibutton(app.ManualTab, 'push');
    app.ManuallyselectbubbleedgepointsButton.ButtonPushedFcn = @(src,event)ManuallyselectbubbleedgepointsButtonPushed(app,event);
    app.ManuallyselectbubbleedgepointsButton.Position = [16 75 317 31];
    app.ManuallyselectbubbleedgepointsButton.Text = 'Manually select bubble edge points';

    % Create ClickatleastthreepointsLabel
    app.ClickatleastthreepointsLabel = uilabel(app.ManualTab);
    app.ClickatleastthreepointsLabel.Position = [21 111 139 22];
    app.ClickatleastthreepointsLabel.Text = 'Click at least three points';

    % Create ClearandrefreshButton_3
    app.ClearandrefreshButton_3 = uibutton(app.ManualTab, 'push');
    app.ClearandrefreshButton_3.ButtonPushedFcn = @(src,event)ClearandrefreshButton_3Pushed(app,event);
    app.ClearandrefreshButton_3.Position = [214 35 120 30];
    app.ClearandrefreshButton_3.Text = 'Clear and refresh';

end
