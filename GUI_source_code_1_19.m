classdef GUI_source_code_1_19 < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                      matlab.ui.Figure
        GridLayout                    matlab.ui.container.GridLayout
        PreturntheThresholdRemovingfactorslidertomaketheLabel  matlab.ui.control.Label
        LoadexistingR_datamatButton   matlab.ui.control.Button
        ImagesPanel                   matlab.ui.container.Panel
        EditField                     matlab.ui.control.EditField
        ImagebitdepthDropDown         matlab.ui.control.DropDown
        ImagebitdepthDropDownLabel    matlab.ui.control.Label
        ImageformatDropDown           matlab.ui.control.DropDown
        ImageformatDropDownLabel      matlab.ui.control.Label
        ImageFolderButton             matlab.ui.control.Button
        PostprocessingPanel           matlab.ui.container.Panel
        ConverttophysicalworldunitsasRofTdatamatPanel  matlab.ui.container.Panel
        FitRmaxafterframeEditField    matlab.ui.control.NumericEditField
        FitRmaxafterframeEditFieldLabel  matlab.ui.control.Label
        ExportButton_2                matlab.ui.control.Button
        um2pxEditField                matlab.ui.control.NumericEditField
        um2pxEditFieldLabel           matlab.ui.control.Label
        FPSEditField                  matlab.ui.control.NumericEditField
        FPSEditFieldLabel             matlab.ui.control.Label
        ExporttoR_datamatPanel        matlab.ui.container.Panel
        ExportpathEditField           matlab.ui.control.EditField
        ExportpathEditFieldLabel      matlab.ui.control.Label
        UsedefaultpathButton          matlab.ui.control.Button
        StoretoanotherpathButton      matlab.ui.control.Button
        ExportButton                  matlab.ui.control.Button
        Label_2                       matlab.ui.control.Label
        Label                         matlab.ui.control.Label
        TabGroup                      matlab.ui.container.TabGroup
        PretuneTab                    matlab.ui.container.Tab
        RemovingFactorEditField       matlab.ui.control.NumericEditField
        RemovingFactorEditFieldLabel  matlab.ui.control.Label
        ThresholdEditField            matlab.ui.control.NumericEditField
        ThresholdEditFieldLabel       matlab.ui.control.Label
        RemovingfactorLabel           matlab.ui.control.Label
        SliderConnectedArea           matlab.ui.control.Slider
        SliderThreshold               matlab.ui.control.Slider
        ThresholdLabel                matlab.ui.control.Label
        BubblecrossgreenedgesLabel    matlab.ui.control.Label
        DownEdgeOrNot                 matlab.ui.control.CheckBox
        TopEdgeOrNot                  matlab.ui.control.CheckBox
        RightEdgeOrNot                matlab.ui.control.CheckBox
        LeftEdgeOrNot                 matlab.ui.control.CheckBox
        ClearandrefreshButton         matlab.ui.control.Button
        FittingandPreviewButton       matlab.ui.control.Button
        ImageEditField                matlab.ui.control.NumericEditField
        ImageEditFieldLabel           matlab.ui.control.Label
        LEditFieldLabel_4             matlab.ui.control.Label
        LEditField_D1                 matlab.ui.control.NumericEditField
        LEditFieldLabel_3             matlab.ui.control.Label
        LEditField_U1                 matlab.ui.control.NumericEditField
        LEditFieldLabel_2             matlab.ui.control.Label
        LEditField_R1                 matlab.ui.control.NumericEditField
        LEditField_L1                 matlab.ui.control.NumericEditField
        LEditFieldLabel               matlab.ui.control.Label
        ROIButton                     matlab.ui.control.Button
        ManualTab                     matlab.ui.container.Tab
        ClearandrefreshButton_3       matlab.ui.control.Button
        ClickatleastthreepointsLabel  matlab.ui.control.Label
        ManuallyselectbubbleedgepointsButton  matlab.ui.control.Button
        ImageEditField_2              matlab.ui.control.NumericEditField
        ImageEditField_2Label_2       matlab.ui.control.Label
        AutomaticTab                  matlab.ui.container.Tab
        RealtimeplayCheckBox          matlab.ui.control.CheckBox
        LoadtunedparametersButton     matlab.ui.control.Button
        ClearandrefreshButton_2       matlab.ui.control.Button
        endNum                        matlab.ui.control.NumericEditField
        toLabel                       matlab.ui.control.Label
        startNum                      matlab.ui.control.NumericEditField
        ImageEditField_2Label         matlab.ui.control.Label
        ROIButton_2                   matlab.ui.control.Button
        LEditFieldLabel_7             matlab.ui.control.Label
        LEditField_R3                 matlab.ui.control.NumericEditField
        LEditField_L3                 matlab.ui.control.NumericEditField
        LEditField_7Label             matlab.ui.control.Label
        LEditFieldLabel_6             matlab.ui.control.Label
        LEditField_U3                 matlab.ui.control.NumericEditField
        LEditFieldLabel_5             matlab.ui.control.Label
        LEditField_D3                 matlab.ui.control.NumericEditField
        FittingandPreviewButton_2     matlab.ui.control.Button
        ModeDropDown                  matlab.ui.control.DropDown
        ModeDropDownLabel             matlab.ui.control.Label
        UIAxes_binary                 matlab.ui.control.UIAxes
        UIAxes_Rtcurve                matlab.ui.control.UIAxes
        UIAxes_raw                    matlab.ui.control.UIAxes
    end


    properties (Access = public)
        imageNo = 1;
        imageTotalNum;
        images;
        folderPath;
        ImgThr;
        imageFormat = 'tiff'; % default
        gridx;
        gridy;
        par;
        Radius;
        Radius_backup;
        CircleFitPar;
        CircleXY;
        ImgGrayScaleMax = 2^16-1;   % Double check image bit depth
        ImgGrayScaleMaxuint8 = 255; % Do not change this line
        % TiffDiffGauss;
        removingFactor = 90;
        BigOrSmall = 0;
        removeobjradius = 0;
        pixelScale;
        um2px;
        FPS;
        Rmax_Fit_Length;
        savePath;
        savePath2;
        saveFormat;
        ParameterTuneOrNot = 0;
        stopiter;
        realtimePlayOrNot;
        bubbleCrossEdges = [0 0 0 0];
        cur_img;
        cur_img_binary;
        cur_img_ROI;
        cur_img_binary_ROI;        
    end

    methods (Access = private)

        %% UPDATE ALL PARAMETERS
        function LoadParas(app)
            switch app.TabGroup.SelectedTab
                case app.PretuneTab
                    app.ImgThr = app.SliderThreshold.Value/100;
                    app.gridy = [app.LEditField_L1.Value,app.LEditField_R1.Value];
                    app.gridx = [app.LEditField_U1.Value,app.LEditField_D1.Value];
                    app.imageNo = app.ImageEditField.Value;
                    app.imageFormat = app.ImageformatDropDown.Value;
                    app.removingFactor = round(app.SliderConnectedArea.Value/100 * app.gridx(2) * app.gridy(2));
                    app.realtimePlayOrNot = app.RealtimeplayCheckBox.Value;
                    app.bubbleCrossEdges = [app.TopEdgeOrNot.Value, app.RightEdgeOrNot.Value, app.DownEdgeOrNot.Value, app.LeftEdgeOrNot.Value];
                case app.ManualTab
                    %app.ImgThr = app.ImagethresholdEditField_3.Value;
                    app.imageNo = app.ImageEditField_2.Value;
                    app.bubbleCrossEdges = [app.TopEdgeOrNot.Value, app.RightEdgeOrNot.Value, app.DownEdgeOrNot.Value, app.LeftEdgeOrNot.Value];

                case app.AutomaticTab
                    %app.ImgThr = app.ImagethresholdEditField_2.Value;
                    app.gridy = [app.LEditField_L3.Value,app.LEditField_R3.Value];
                    app.gridx = [app.LEditField_U3.Value,app.LEditField_D3.Value];
                    app.imageNo = app.startNum.Value;
                    app.imageTotalNum = app.endNum.Value;
                    app.imageFormat = app.ImageformatDropDown.Value;
                    app.removingFactor = round(app.SliderConnectedArea.Value/100 * app.gridx(2) * app.gridy(2));
                    app.realtimePlayOrNot = app.RealtimeplayCheckBox.Value;
                    app.bubbleCrossEdges = [app.TopEdgeOrNot.Value, app.RightEdgeOrNot.Value, app.DownEdgeOrNot.Value, app.LeftEdgeOrNot.Value];

            end
            app.um2px = app.um2pxEditField.Value;
            app.FPS = app.FPSEditField.Value;
            app.Rmax_Fit_Length = app.FitRmaxafterframeEditField.Value;
        end



        %% You already have binary current image, then do the circle detect
        % and fitting (display) for just one frame
        function PreviewSingleImage(app)

            % Detect bubble boundary using extracted pipeline
            [bws2, XY] = bubblefit.imageproc.detectBubble( ...
                app.cur_img_binary_ROI, app.bubbleCrossEdges, ...
                app.removingFactor, app.removeobjradius, ...
                app.BigOrSmall, app.gridx, app.gridy);

            % Circle fitting
            try
                currentPar=bubblefit.CircleFitByTaubin(XY);
            catch
                currentPar = [0,0,0];
            end
            app.Radius(app.imageNo) = currentPar(3);
            app.CircleFitPar(app.imageNo,:) = [currentPar(1),currentPar(2)];
            app.CircleXY{app.imageNo} = XY;

            % Display binary image
            if app.realtimePlayOrNot == 0 && app.imageNo ~= app.endNum.Value;
            else
                title(app.UIAxes_raw, ['Image # ',num2str(app.imageNo)]);
                title(app.UIAxes_binary, ['Image # ',num2str(app.imageNo)]);

                cla(app.UIAxes_binary);
                cla(app.UIAxes_raw);
                imshow(bws2,'Parent',app.UIAxes_binary)
            end

            % Display raw image
            if app.TabGroup.SelectedTab == app.PretuneTab
                % Display detected circle
                imshow(imread(app.images{app.imageNo}),'Parent', app.UIAxes_raw,'DisplayRange',[0,app.ImgGrayScaleMax]);
                hold(app.UIAxes_raw, 'on');
                viscircles(app.UIAxes_raw,[currentPar(2),currentPar(1)],currentPar(3),'Color','b');
                plot(XY(:,2),XY(:,1),'r.','Parent', app.UIAxes_raw);

                % Display ROI
                hold(app.UIAxes_raw, 'on');
                rectangle(app.UIAxes_raw, 'Position', [app.gridy(1),app.gridx(1),app.gridy(2)-app.gridy(1),app.gridx(2)-app.gridx(1)], 'EdgeColor', 'green', 'LineWidth', 2);
                hold(app.UIAxes_raw, 'off');
            elseif app.TabGroup.SelectedTab == app.AutomaticTab

                if app.realtimePlayOrNot == 0 && app.imageNo ~= app.endNum.Value
                else
                    % Display detected circle
                    imshow(imread(app.images{app.imageNo}),'Parent', app.UIAxes_raw,'DisplayRange',[0,app.ImgGrayScaleMax]);
                    hold(app.UIAxes_raw, 'on');
                    viscircles(app.UIAxes_raw,[currentPar(2),currentPar(1)],currentPar(3),'Color','b');
                    plot(XY(:,2),XY(:,1),'r.','Parent', app.UIAxes_raw);
                                    % Display ROI
                hold(app.UIAxes_raw, 'on');
                rectangle(app.UIAxes_raw, 'Position', [app.gridy(1),app.gridx(1),app.gridy(2)-app.gridy(1),app.gridx(2)-app.gridx(1)], 'EdgeColor', 'green', 'LineWidth', 2);
                hold(app.UIAxes_raw, 'off');
                end
            end

        end

        %% Generate binary image
        function GetCurrentbinaryImage(app)
            [app.cur_img, app.cur_img_binary, app.cur_img_ROI, app.cur_img_binary_ROI] = ...
                bubblefit.imageproc.loadAndNormalize( ...
                    app.images, app.imageNo, ...
                    app.ImagebitdepthDropDown.Value, ...
                    app.ImgThr, app.gridx, app.gridy);
        end

        %% Real-time display for pretune
        function realtimeDisplay_threshold(app, threshold)
            % Update para
            LoadParas(app);
            app.ImgThr = threshold/100;

            % ROI modify and display binary image
            GetCurrentbinaryImage(app); % You will get an binary image -- app.cur_img

            % Display realtime
            title(app.UIAxes_raw, ['Image # ',num2str(app.imageNo)]);
            title(app.UIAxes_binary, ['Image # ',num2str(app.imageNo)]);
            cla(app.UIAxes_binary);
            cla(app.UIAxes_raw);
            imshow(imread(app.images{app.imageNo}),'Parent', app.UIAxes_raw,'DisplayRange',[0,app.ImgGrayScaleMax]);
            imshow(~app.cur_img_binary_ROI,'Parent', app.UIAxes_binary);

            hold(app.UIAxes_raw, 'on'); 
            rectangle(app.UIAxes_raw, 'Position', [app.gridy(1),app.gridx(1),app.gridy(2)-app.gridy(1),app.gridx(2)-app.gridx(1)], 'EdgeColor', 'green', 'LineWidth', 2);
            hold(app.UIAxes_raw, 'off'); 


        end


        function realtimeDisplay_connectedArea(app, removingFactor)
            %% Update para
            LoadParas(app);
            app.removingFactor = round(removingFactor/100 * app.gridx(2) * app.gridy(2));

            % ROI modify and display binary image
            GetCurrentbinaryImage(app);

            % Use shared detection pipeline (skip morphological closing for tuning preview)
            [bws2, ~] = bubblefit.imageproc.detectBubble( ...
                app.cur_img_binary_ROI, app.bubbleCrossEdges, ...
                app.removingFactor, 0, ...
                app.BigOrSmall, app.gridx, app.gridy);

            % Display realtime
            title(app.UIAxes_raw, ['Image # ',num2str(app.imageNo)]);
            title(app.UIAxes_binary, ['Image # ',num2str(app.imageNo)]);
            cla(app.UIAxes_binary);
            cla(app.UIAxes_raw);
            imshow(imread(app.images{app.imageNo}),'Parent', app.UIAxes_raw,'DisplayRange',[0,app.ImgGrayScaleMax]);
            imshow(bws2,'Parent', app.UIAxes_binary);

            hold(app.UIAxes_raw, 'on');
            rectangle(app.UIAxes_raw, 'Position', [app.gridy(1),app.gridx(1),app.gridy(2)-app.gridy(1),app.gridx(2)-app.gridx(1)], 'EdgeColor', 'green', 'LineWidth', 2);
            hold(app.UIAxes_raw, 'off');

        end

        % Display certain time Radius_array
        function plotNewPoints(app)
            hold(app.UIAxes_Rtcurve, 'on');
            plot(app.imageNo,app.Radius(app.imageNo),'r+','Parent',app.UIAxes_Rtcurve);
        end

        % Display certain time Radius_array
        function plotAllPoints(app)
            hold(app.UIAxes_Rtcurve, 'on');
            plot([app.startNum.Value:app.endNum.Value],app.Radius(app.startNum.Value:app.endNum.Value),'r+','Parent',app.UIAxes_Rtcurve);
        end

        function    deleteOldPoints(app) % Hide old points
            hold(app.UIAxes_Rtcurve, 'on');
            plot(app.imageNo,app.Radius(app.imageNo),'w+','Parent',app.UIAxes_Rtcurve);

        end

    end


    % Callbacks that handle component events
    methods (Access = private)

        % Code that executes after component creation
        function startupFcn(app)
            % Init
            screen_size = get(0, 'ScreenSize'); % get the size of screen
            app.UIFigure.Position = [1300, screen_size(4)-1000, 1000, 800];
            app.TabGroup.SelectedTab = app.PretuneTab;

        end

        % Callback function: EditField, ImageFolderButton
        function ImageFileButtonPushed(app, event)
            app.imageFormat = app.ImageformatDropDown.Value;
            app.folderPath = uigetdir;
            app.EditField.Value = app.folderPath;
    
            % ----------- Zach: Support Mac OS -------------------------------------
            % temp = [app.folderPath,'\*.',app.imageFormat];
            temp = fullfile(app.folderPath, ['*.',app.imageFormat]); 

            files = dir(temp); % Double check image file type
            app.images = cell(length(files),1);
            for i = 1:length(files)
                % app.images{i} = [app.folderPath,'\',files(i).name];
                app.images{i} = fullfile(app.folderPath, files(i).name);
            end
            % ---------------------------------------------------------------------

            if size(app.images,1) == 0
                errordlg('No valid images loaded, please check image format!', 'Error');
                return
            end

            % Initialization
            app.Radius = zeros(1,length(files))-1;
            temp_image = imread(app.images{1});
            app.LEditField_R1.Value = size(temp_image,2);
            app.LEditField_R3.Value = size(temp_image,2);
            app.LEditField_D1.Value = size(temp_image,1) ;
            app.LEditField_D3.Value = size(temp_image,1);



            % For Mode 3
            app.endNum.Value = size(app.images,1);

            % For R-t curve axes
            % X
            xlabel(app.UIAxes_Rtcurve, 'Frame No.');
            app.UIAxes_Rtcurve.XLim = [1,app.endNum.Value];
            xTicks = 1:20:app.endNum.Value;
            app.UIAxes_Rtcurve.XTick = xTicks;
            % Y
            ylabel(app.UIAxes_Rtcurve, 'Radius [Pixels]');
            egImageSize = imread(app.images{1});

            app.UIAxes_Rtcurve.YLim = [0,max(size(egImageSize))* 0.7];
            YTicks = 1:20:max(size(egImageSize)/2);
            app.UIAxes_Rtcurve.YTick = YTicks;

        end

        % Value changed function: ModeDropDown
        function ModeDropDownValueChanged(app, event)
            mode = app.ModeDropDown.Value;
            switch mode
                case 'Pre-tune'
                    app.TabGroup.SelectedTab = app.PretuneTab;
                case 'Manual'
                    app.TabGroup.SelectedTab = app.ManualTab;
                    % LoadParasBasedonPretune_mode2(app); replaced by the
                    % load_tuned_parameters function.
                case 'Automatic'
                    app.TabGroup.SelectedTab = app.AutomaticTab;
                    % LoadParasBasedonPretune_mode3(app); replaced by the
                    % load_tuned_parameters function.
            end
        end

        % Selection change function: TabGroup
        function TabGroupSelectionChanged(app, event)



            selectedMode = app.TabGroup.SelectedTab;
            app.ModeDropDown.Value = selectedMode.Title;

            % We don't do this anymore, this function was replaced by the
            % load_tuned_parameters function.
            % if selectedMode == app.PretuneTab
            %
            % elseif selectedMode == app.ManualTab
            %     LoadParasBasedonPretune_mode2(app);
            % elseif selectedMode == app.AutomaticTab
            %     LoadParasBasedonPretune_mode3(app);
            % end

        end

        % Button pushed function: ROIButton
        function ROIButtonPushed(app, event)
            % Update para
            LoadParas(app);
            % ROI modify and display binary image
            GetCurrentbinaryImage(app); % You will get an binary image -- app.TiffDiffGauss
            imshow(app.cur_img,'Parent', app.UIAxes_raw);
            % ROIfigureHandle = figure("Name",'Modify ROI','Position', [800, 500, 600, 400]);
            % imshow(app.cur_img);

            %%%%%%%%%            
            
            % Define the scaling factor and resize the image
            scale_factor = 2.5;
            resized_img = imresize(app.cur_img, scale_factor, 'bicubic'); % 使用imresize放大图像
            
            % Create a new figure and display the *resized* image
            ROIfigureHandle = figure('Name', 'Modify ROI', 'Position', [800, 500, 600, 400]);
            imshow(resized_img); 
            h = drawrectangle;
            pos = h.Position;
            
            % Get the position and scale it back to the original image coordinates
            pos = pos / scale_factor; 
            
            %%%%%%%%%%%%%%%%%%
  
            app.gridy = [pos(1),pos(1)+pos(3)];
            app.gridx = [pos(2),pos(2)+pos(4)];
            close(ROIfigureHandle);

            % Adjust ROI domain
            if app.gridx(1)<1, app.gridx(1) = 1; end
            if app.gridy(1)<1, app.gridy(1) = 1; end
            if app.gridx(2)>size(app.cur_img,1), app.gridx(2)=size(app.cur_img,1);end
            if app.gridy(2)>size(app.cur_img,2), app.gridy(2)=size(app.cur_img,2);end

            % app.ROIDomainRedefine = 1;

            app.LEditField_L1.Value = app.gridy(1);
            app.LEditField_R1.Value = app.gridy(2);
            app.LEditField_U1.Value = app.gridx(1);
            app.LEditField_D1.Value = app.gridx(2);

            realtimeDisplay_threshold(app,app.SliderThreshold.Value);


        end

        % Button pushed function: FittingandPreviewButton
        function FittingandPreviewButtonPushed(app, event)
            % Update para
            LoadParas(app);
            % Display
            GetCurrentbinaryImage(app); % You will get an binary image -- app.cur_img
            cla(app.UIAxes_raw);
            deleteOldPoints(app);
            PreviewSingleImage(app);
            plotNewPoints(app);

        end

        % Button pushed function: ROIButton_2
        function ROIButton_2Pushed(app, event)

            % Update para
            LoadParas(app);

            % ROI modify and display binary image
            GetCurrentbinaryImage(app); % You will get an binary image -- app.cur_img
            imshow(uint8(app.cur_img),'Parent', app.UIAxes_binary);
            ROIfigureHandle = figure("Name",'Modify ROI','Position', [800, 500, 600, 400]);
            imshow(uint8(app.cur_img));
            [app.gridy(1),app.gridx(1)] = ginput(1);
            [app.gridy(2),app.gridx(2)] = ginput(1);
            close(ROIfigureHandle);

            % Adjust ROI domain
            if app.gridx(1)<1, app.gridx(1) = 1; end
            if app.gridy(1)<1, app.gridy(1) = 1; end
            if app.gridx(2)>size(app.cur_img,1), app.gridx(2)=size(app.cur_img,1);end
            if app.gridy(2)>size(app.cur_img,2), app.gridy(2)=size(app.cur_img,2);end

            app.LEditField_L3.Value = app.gridy(1);
            app.LEditField_R3.Value = app.gridy(2);
            app.LEditField_U3.Value = app.gridx(1);
            app.LEditField_D3.Value = app.gridx(2);

            % try
            %     app.cur_img( temp111(2):temp222(2), temp111(1):temp222(1) ) =  255;
            %     figure, imshow(uint8(app.cur_img));
            % catch
            % end

        end

        % Button pushed function: FittingandPreviewButton_2
        function FittingandPreviewButton_2Pushed(app, event)

            % Update para
            LoadParas(app);

            app.stopiter = true;

            if app.realtimePlayOrNot
                for i = app.startNum.Value : app.endNum.Value

                    % % Update para
                    % LoadParas(app);
                    %
                    %
                    % pause(1e-4)
                    % if app.stopiter
                    %     break
                    %
                    % end

                    GetCurrentbinaryImage(app);
                    deleteOldPoints(app);
                    PreviewSingleImage(app);
                    plotNewPoints(app);

                    pause(0.1)

                    app.imageNo = app.imageNo+1;
                end

            else % no need to wait for point-wise display
                d = uiprogressdlg(app.UIFigure,'Title','Please wait...','Message','Processing...','Cancelable','on');

                for i = app.startNum.Value : app.endNum.Value


                    % % Update para
                    % LoadParas(app);
                    %
                    %
                    % pause(1e-4)
                    % if app.stopiter
                    %     break
                    %
                    % end

                    GetCurrentbinaryImage(app);
                    deleteOldPoints(app);
                    PreviewSingleImage(app);
                    app.imageNo = app.imageNo+1;

                    d.Value = ceil(i-app.startNum.Value)/(app.endNum.Value -app.startNum.Value);
                    d.Message = sprintf('Processing... %d%% Finished!', floor(d.Value*100));
                    pause(0.01)
                    if d.CancelRequested
                        break;
                    end
                end

                plotAllPoints(app);
                close(d);
            end



        end

        % Button pushed function: ExportButton
        function ExportButtonPushed(app, event)
            LoadParas(app);
            bubblefit.export.exportRData(app.savePath, app.Radius, app.CircleFitPar, app.CircleXY);
        end

        % Button pushed function: ClearandrefreshButton
        function ClearandrefreshButtonPushed(app, event)
            app.Radius_backup = app.Radius;
            app.Radius = zeros(size(app.Radius)) - 1;
            app.CircleFitPar = zeros(length(app.Radius),2);
            app.CircleXY = [];
            cla(app.UIAxes_Rtcurve);
        end

        % Button pushed function: ManuallyselectbubbleedgepointsButton
        function ManuallyselectbubbleedgepointsButtonPushed(app, event)
            % Update para
            LoadParas(app);
            ManualfigureHandle = figure("Name",'Select at least 3 points','Position', [500, 500, 1000, 1000]);
            
            % Define scale factor, read original image, and resize it
            scale_factor = 2.5;
            original_img = imread(app.images{app.imageNo});
            resized_img = imresize(original_img, scale_factor, 'bicubic');

            % Display the resized image
            imshow(resized_img, 'DisplayRange', [0,app.ImgGrayScaleMax]);
            hold on; 

XY = [];
while true
    try
        [x, y, button] = ginput(1);
        
        if isempty(button) || button == 13
            break; % 
        end
        
        XY = [XY; y, x];
        
        plot(x, y, 'ro', 'MarkerSize', 6, 'LineWidth', 1.5);
        
    catch
        disp('User cancelled.');
        break;
    end
end

close(ManualfigureHandle);

% Scale the collected points back to original image coordinates ---
XY = XY / scale_factor;

if size(XY, 1) < 3
    error('Please select at least 3 points!');
end



            try
                currentPar=bubblefit.CircleFitByTaubin(XY);
            catch
                currentPar = [0,0,0];
            end

            deleteOldPoints(app);
            app.Radius(app.imageNo) = currentPar(3);
            plotNewPoints(app);


            app.CircleFitPar(app.imageNo,:) = [currentPar(1),currentPar(2)];
            app.CircleXY{app.imageNo} = XY;

            % Display detected circle
            title(app.UIAxes_raw, ['Image # ',num2str(app.imageNo)]);
            title(app.UIAxes_binary, ['Image # ',num2str(app.imageNo)]);
            cla(app.UIAxes_binary);
            cla(app.UIAxes_raw);
            imshow(imread(app.images{app.imageNo}),'Parent', app.UIAxes_raw,'DisplayRange',[0,app.ImgGrayScaleMax]);
            %imshow(TiffDiffNorm,'DisplayRange',[0,ImgGrayScaleMaxuint8]);
            hold(app.UIAxes_raw, 'on');
            viscircles(app.UIAxes_raw,[currentPar(2),currentPar(1)],currentPar(3),'Color','b');
            plot(XY(:,2),XY(:,1),'r.','Parent', app.UIAxes_raw);

        end

        % Value changed function: FPSEditField
        function FPSEditFieldValueChanged(app, event)
            app.FPS = app.FPSEditField.Value;

        end

        % Value changed function: um2pxEditField
        function um2pxEditFieldValueChanged(app, event)
            app.um2px = app.um2pxEditField.Value;

        end

        % Button pushed function: ExportButton_2
        function ExportButton_2Pushed(app, event)
            LoadParas(app);
            [success, msg] = bubblefit.export.exportRofTData( ...
                app.savePath, app.Radius, app.um2px, app.FPS, app.Rmax_Fit_Length);
            if ~success
                uialert(app.UIFigure, msg, 'Error');
            end
        end

        % Button pushed function: StoretoanotherpathButton
        function StoretoanotherpathButtonPushed(app, event)
            % Update para
            LoadParas(app);
            [file, path, idx] = uiputfile({'*.mat', 'MAT-files (*.mat)'; '*.csv', 'CSV-files (*.csv)'}, 'Save as');
            app.savePath = fullfile(path, file);
            app.ExportpathEditField.Value = app.savePath;
        end

        % Button pushed function: UsedefaultpathButton
        function UsedefaultpathButtonPushed(app, event)
            % Update para
            LoadParas(app);
            app.savePath = [app.folderPath,'/R_data.mat'];
            app.ExportpathEditField.Value = app.savePath;

        end

        % Value changed function: ExportpathEditField
        function ExportpathEditFieldValueChanged(app, event)
            app.savePath = app.ExportpathEditField.Value;
        end

        % Button pushed function: LoadtunedparametersButton
        function LoadtunedparametersButtonPushed(app, event)

            %app.ImagethresholdEditField_2.Value = app.ImagethresholdEditField.Value;
            %app.RemoveconnectedareapixelEditField_2.Value = app.RemoveconnectedareapixelEditField.Value;
            app.LEditField_D3.Value = app.LEditField_D1.Value;
            app.LEditField_U3.Value = app.LEditField_U1.Value;
            app.LEditField_R3.Value = app.LEditField_R1.Value;
            app.LEditField_L3.Value = app.LEditField_L1.Value;

            % Load para
            LoadParas(app);


        end

        % Button pushed function: ClearandrefreshButton_3
        function ClearandrefreshButton_3Pushed(app, event)
            app.Radius_backup = app.Radius;
            app.Radius = zeros(size(app.Radius)) - 1;
            app.CircleFitPar = zeros(length(app.Radius),2);
            app.CircleXY = [];
            cla(app.UIAxes_Rtcurve);
        end

        % Button pushed function: ClearandrefreshButton_2
        function ClearandrefreshButton_2Pushed(app, event)
            app.Radius_backup = app.Radius;
            app.Radius = zeros(size(app.Radius)) - 1;
            app.CircleFitPar = zeros(length(app.Radius),2);
            app.CircleXY = [];
            cla(app.UIAxes_Rtcurve);
        end

        % Callback function
        function StopButtonPushed(app, event)
            app.stopiter=false;
        end

        % Callback function
        function ImagethresholdEditField_2ValueChanged(app, event)
            app.ImgThr = app.ImagethresholdEditField_2.Value;
        end

        % Callback function
        function ImagethresholdEditFieldValueChanged(app, event)
            app.ImgThr = app.ImagethresholdEditField.Value;

        end

        % Callback function
        function ImagethresholdEditField_3ValueChanged(app, event)
            app.ImgThr = app.ImagethresholdEditField_3.Value;

        end

        % Value changed function: ImagebitdepthDropDown
        function ImagebitdepthDropDownValueChanged(app, event)
            app.ImgGrayScaleMax = 2^str2double(app.ImagebitdepthDropDown.Value) - 1;
        end

        % Button pushed function: LoadexistingR_datamatButton
        function LoadexistingR_datamatButtonPushed(app, event)

            % Open a dialog box for the user to select a .mat file
            [fileName, app.folderPath] = uigetfile('*.mat', 'Select the R_data.mat file');
            
            % Check if the user cancelled the selection
            if isequal(fileName, 0) || isequal(app.folderPath, 0)
                disp('User cancelled the file selection.');
                return; % Exit the function
            end

            % Construct the full path to the selected file
            fullFilePath = fullfile(app.folderPath, fileName);


            try
                Rt = load(fullFilePath); % Use the new path to load the file
                disp(['File ''', fileName, ''' loaded successfully.']);
            catch
                disp(['An error occurred while loading the file: ', fileName]);
                % It's good practice to also return here if loading fails
                return; 
            end
            
            app.CircleFitPar = Rt.CircleCenterSave;
            app.CircleXY = Rt.CircleEdgePtSave;
            app.Radius = Rt.CircleR;
            app.imageNo = 1:1:length(app.Radius);

            % Update para
            % LoadParas(app);

            % Display
            %GetCurrentbinaryImage(app); % You will get an binary image -- app.TiffDiffGauss
            cla(app.UIAxes_raw);
            deleteOldPoints(app);
            %PreviewSingleImage(app);
            plotNewPoints(app);

        end

        % Value changed function: FitRmaxafterframeEditField
        function FitRmaxafterframeEditFieldValueChanged(app, event)
            app.Rmax_Fit_Length = app.FitRmaxafterframeEditField.Value;

        end

        % Value changed function: ImageEditField
        function ImageEditFieldValueChanged(app, event)
            value = app.ImageEditField.Value;
            realtimeDisplay_connectedArea(app,app.SliderConnectedArea.Value);
        end

        % Value changing function: SliderThreshold
        function SliderThresholdValueChanging(app, event)
            changingValue = event.Value;
            app.ThresholdEditField.Value = changingValue;
            realtimeDisplay_threshold(app,changingValue);
        end

        % Value changed function: ThresholdEditField
        function ThresholdEditFieldValueChanged(app, event)
            value = app.ThresholdEditField.Value;
            app.SliderThreshold.Value = value;
            realtimeDisplay_threshold(app, value);
        end

        % Value changing function: SliderConnectedArea
        function SliderConnectedAreaValueChanging(app, event)
            changingValue = event.Value;
            app.RemovingFactorEditField.Value = changingValue;
            % realtimeDisplay_connectedArea(app,changingValue);
        end

        % Value changed function: SliderConnectedArea
        function SliderConnectedAreaValueChanged(app, event)
            value = app.SliderConnectedArea.Value;
            realtimeDisplay_connectedArea(app,value);
        end

        % Value changed function: RemovingFactorEditField
        function RemovingFactorEditFieldValueChanged(app, event)
            value = app.RemovingFactorEditField.Value;
            app.SliderConnectedArea.Value = value;
            realtimeDisplay_connectedArea(app, value);
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Create main layout, axes
            bubblefit.ui.createMainLayout(app);

            % Create Mode dropdown
            app.ModeDropDownLabel = uilabel(app.GridLayout);
            app.ModeDropDownLabel.HorizontalAlignment = 'right';
            app.ModeDropDownLabel.Layout.Row = 6;
            app.ModeDropDownLabel.Layout.Column = 1;
            app.ModeDropDownLabel.Text = 'Mode';

            app.ModeDropDown = uidropdown(app.GridLayout);
            app.ModeDropDown.Items = {'Pre-tune', 'Manual', 'Automatic'};
            app.ModeDropDown.ValueChangedFcn = createCallbackFcn(app, @ModeDropDownValueChanged, true);
            app.ModeDropDown.Layout.Row = 6;
            app.ModeDropDown.Layout.Column = [2 3];
            app.ModeDropDown.Value = 'Pre-tune';

            % Create TabGroup
            app.TabGroup = uitabgroup(app.GridLayout);
            app.TabGroup.SelectionChangedFcn = createCallbackFcn(app, @TabGroupSelectionChanged, true);
            app.TabGroup.Layout.Row = [7 10];
            app.TabGroup.Layout.Column = [1 5];

            % Create tabs
            bubblefit.ui.createPretuneTab(app);
            bubblefit.ui.createManualTab(app);
            bubblefit.ui.createAutomaticTab(app);

            % Create labels
            app.Label = uilabel(app.GridLayout);
            app.Label.HorizontalAlignment = 'center';
            app.Label.VerticalAlignment = 'top';
            app.Label.FontName = 'Arial';
            app.Label.FontWeight = 'bold';
            app.Label.Layout.Row = 1;
            app.Label.Layout.Column = 7;
            app.Label.Text = '';

            app.Label_2 = uilabel(app.GridLayout);
            app.Label_2.HorizontalAlignment = 'center';
            app.Label_2.VerticalAlignment = 'top';
            app.Label_2.FontName = 'arial';
            app.Label_2.FontWeight = 'bold';
            app.Label_2.Layout.Row = 8;
            app.Label_2.Layout.Column = 6;
            app.Label_2.Text = '';

            % Create panels
            bubblefit.ui.createPostprocessingPanel(app);
            bubblefit.ui.createImagesPanel(app);

            % Create top-level buttons and labels
            app.LoadexistingR_datamatButton = uibutton(app.GridLayout, 'push');
            app.LoadexistingR_datamatButton.ButtonPushedFcn = createCallbackFcn(app, @LoadexistingR_datamatButtonPushed, true);
            app.LoadexistingR_datamatButton.Layout.Row = 6;
            app.LoadexistingR_datamatButton.Layout.Column = [4 5];
            app.LoadexistingR_datamatButton.Text = 'Load existing R_data.mat';

            app.PreturntheThresholdRemovingfactorslidertomaketheLabel = uilabel(app.GridLayout);
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.HorizontalAlignment = 'center';
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.FontSize = 18;
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.FontWeight = 'bold';
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.FontColor = [1 0 0];
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.Layout.Row = [1 2];
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.Layout.Column = 7;
            app.PreturntheThresholdRemovingfactorslidertomaketheLabel.Text = {'Adjust the sliders to distinguish'; 'the bubble (white) and background (black)'};

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = GUI_source_code_1_19

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            % Execute the startup function
            runStartupFcn(app, @startupFcn)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end