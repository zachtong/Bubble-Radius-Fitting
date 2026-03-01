function createImagesPanel(app)
%CREATEIMAGESPANEL  Create images panel with folder, format, and bit depth controls.

    % Create ImagesPanel
    app.ImagesPanel = uipanel(app.GridLayout);
    app.ImagesPanel.Title = 'Images';
    app.ImagesPanel.Layout.Row = [1 5];
    app.ImagesPanel.Layout.Column = [1 5];

    % Create ImageFolderButton
    app.ImageFolderButton = uibutton(app.ImagesPanel, 'push');
    app.ImageFolderButton.ButtonPushedFcn = createCallbackFcn(app, @ImageFileButtonPushed, true);
    app.ImageFolderButton.Position = [8 79 108 20];
    app.ImageFolderButton.Text = 'Image Folder';

    % Create ImageformatDropDownLabel
    app.ImageformatDropDownLabel = uilabel(app.ImagesPanel);
    app.ImageformatDropDownLabel.HorizontalAlignment = 'right';
    app.ImageformatDropDownLabel.Position = [8 44 108 23];
    app.ImageformatDropDownLabel.Text = 'Image format';

    % Create ImageformatDropDown
    app.ImageformatDropDown = uidropdown(app.ImagesPanel);
    app.ImageformatDropDown.Items = {'tiff', 'tif', 'jpeg', 'bmp', 'png', 'jpg'};
    app.ImageformatDropDown.Position = [128 44 112 23];
    app.ImageformatDropDown.Value = 'tiff';

    % Create ImagebitdepthDropDownLabel
    app.ImagebitdepthDropDownLabel = uilabel(app.ImagesPanel);
    app.ImagebitdepthDropDownLabel.HorizontalAlignment = 'right';
    app.ImagebitdepthDropDownLabel.Position = [8 10 108 22];
    app.ImagebitdepthDropDownLabel.Text = 'Image bit depth';

    % Create ImagebitdepthDropDown
    app.ImagebitdepthDropDown = uidropdown(app.ImagesPanel);
    app.ImagebitdepthDropDown.Items = {'8', '10', '12', '16', '24', '32', '48'};
    app.ImagebitdepthDropDown.ValueChangedFcn = createCallbackFcn(app, @ImagebitdepthDropDownValueChanged, true);
    app.ImagebitdepthDropDown.Position = [128 10 112 22];
    app.ImagebitdepthDropDown.Value = '16';

    % Create EditField
    app.EditField = uieditfield(app.ImagesPanel, 'text');
    app.EditField.ValueChangedFcn = createCallbackFcn(app, @ImageFileButtonPushed, true);
    app.EditField.Editable = 'off';
    app.EditField.Position = [128 79 200 20];

end
