%% loading images

files = dir('Jin_*.tiff'); % Double check image file type

ImgGrayScaleMax = 2^16-1;   % Double check image bit depth
ImgGrayScaleMaxuint8 = 255; % Do not change this line

im = cell(length(files),1);
for i = 1:length(files)
    im{i} = files(i).name;
end
 
 

%%
% 
% Load your fitted R-t matfile "R_data.mat"



%% %%%%% Make movie %%%%%
try
    close(v);
catch
end

close all;
files = dir('Jin*.tiff'); ImgGrayScaleMax = 2^16-1;
im = cell(length(files),1);
for i = 1:length(files)
    im{i} = files(i).name;
end

v = VideoWriter('bubble_Rt.mp4','MPEG-4');
open(v);
figure, 
for tempk =  2 :length(files)

    try
        
        clf

        subplot(2,1,1);
        imshow(imread(im{tempk},1),'DisplayRange',[0,ImgGrayScaleMax]); 
        % title(['Frame #',num2str(tempk)],'FontWeight','normal');
        % ylabel(['Frame #',num2str(tempk)],'FontWeight','normal');
        hold on; viscircles([CircleCenterSave(tempk,2),CircleCenterSave(tempk,1)],CircleR(tempk) ,'Color','b');
        ax1 = gca;  % Get current axis
        set(ax1, 'Position', [0.1, 0.54, 0.8, 0.4]);  % Set position [left, bottom, width, height]
        set(gca,'fontsize',16);

        % axis([1,512,1,128]);

        subplot(2,1,2);
        hold on;
        plot([2:1:tempk], CircleR(2:tempk), 'bo-','LineWidth',1.1);
        h1 =  plot(tempk, CircleR(tempk), 'ro','LineWidth',1.2 );
        set(h1, 'markerfacecolor', get(h1, 'color')); % Use same color to fill in markers
        box on; axis([0,256,0, 25*ceil(max(CircleR)/25) ]);

        ylabel('R (px)','FontWeight','normal');
        xlabel(['Frame #',num2str(tempk)],'FontWeight','normal');

        ax2 = gca;  % Get current axis
        set(ax2, 'Position', [0.26, 0.15, 0.48, 0.35]);  % Set position [left, bottom, width, height]
        set(gca,'fontsize',16);

        frame = getframe(gcf);
        writeVideo(v,frame);


        waitbar(tempk/length(files));

    catch
    end

end
close(v);

