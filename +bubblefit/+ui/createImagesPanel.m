function createImagesPanel(app)
%CREATEIMAGESPANEL  Create images panel with folder selection.

    % Create ImagesPanel
    app.ImagesPanel = uipanel(app.GridLayout);
    app.ImagesPanel.Title = 'Images';
    app.ImagesPanel.Layout.Row = [1 5];
    app.ImagesPanel.Layout.Column = [1 5];

    % Create ImageFolderButton
    app.ImageFolderButton = uibutton(app.ImagesPanel, 'push');
    app.ImageFolderButton.ButtonPushedFcn = @(src,event)ImageFileButtonPushed(app,event);
    app.ImageFolderButton.Position = [8 79 108 20];
    app.ImageFolderButton.Text = 'Image Folder';

    % Create EditField (shows selected folder path)
    app.EditField = uieditfield(app.ImagesPanel, 'text');
    app.EditField.Editable = 'off';
    app.EditField.Position = [128 79 200 20];

end
