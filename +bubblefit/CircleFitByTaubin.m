function Par = CircleFitByTaubin(XY)
%CIRCLEFITBYTAUBIN  Circle fit by Taubin method.
%
%   Par = bubblefit.CircleFitByTaubin(XY)
%
%   G. Taubin, "Estimation Of Planar Curves, Surfaces And Nonplanar
%               Space Curves Defined By Implicit Equations, With
%               Applications To Edge And Range Image Segmentation",
%   IEEE Trans. PAMI, Vol. 13, pages 1115-1138, (1991)
%
%   Input:  XY(n,2) is the array of coordinates of n points x(i)=XY(i,1), y(i)=XY(i,2)
%
%   Output: Par = [a b R] is the fitting circle:
%                         center (a,b) and radius R
%                         Returns [NaN NaN NaN] if fitting fails.

    % Input validation
    if size(XY, 1) < 3
        Par = [NaN NaN NaN];
        return;
    end

    centroid = mean(XY, 1);   % the centroid of the data set

    % Computing moments (vectorized, all moments normed by n)
    XYc = XY - centroid;
    Zi = sum(XYc.^2, 2);

    Mxx = mean(XYc(:,1).^2);
    Myy = mean(XYc(:,2).^2);
    Mxy = mean(XYc(:,1) .* XYc(:,2));
    Mxz = mean(XYc(:,1) .* Zi);
    Myz = mean(XYc(:,2) .* Zi);
    Mzz = mean(Zi.^2);

    %    computing the coefficients of the characteristic polynomial

    Mz = Mxx + Myy;
    Cov_xy = Mxx*Myy - Mxy*Mxy;
    A3 = 4*Mz;
    A2 = -3*Mz*Mz - Mzz;
    A1 = Mzz*Mz + 4*Cov_xy*Mz - Mxz*Mxz - Myz*Myz - Mz*Mz*Mz;
    A0 = Mxz*Mxz*Myy + Myz*Myz*Mxx - Mzz*Cov_xy - 2*Mxz*Myz*Mxy + Mz*Mz*Cov_xy;
    A22 = A2 + A2;
    A33 = A3 + A3 + A3;

    xnew = 0;
    ynew = 1e+20;
    epsilon = 1e-12;
    IterMax = 20;

    % Newton's method starting at x=0

    for iter=1:IterMax
        yold = ynew;
        ynew = A0 + xnew*(A1 + xnew*(A2 + xnew*A3));
        if abs(ynew) > abs(yold)
            warning('bubblefit:newtonDirection', 'Newton-Taubin goes wrong direction: |ynew| > |yold|');
            xnew = 0;
            break;
        end
        Dy = A1 + xnew*(A22 + xnew*A33);
        xold = xnew;
        xnew = xold - ynew/Dy;
        if abs((xnew-xold)/(xnew + eps)) < epsilon, break, end
        if (iter >= IterMax)
            warning('bubblefit:noConverge', 'Newton-Taubin will not converge');
            xnew = nan;
        end
        if (xnew<0.)
            warning('bubblefit:negativeRoot', 'Newton-Taubin negative root: x=%f', xnew);
            xnew = 0;
        end
    end

    %  computing the circle parameters

    DET = xnew*xnew - xnew*Mz + Cov_xy;
    Center = [Mxz*(Myy-xnew)-Myz*Mxy , Myz*(Mxx-xnew)-Mxz*Mxy]/DET/2;

    Par = [Center+centroid , sqrt(Center*Center'+Mz)];

end    %    CircleFitByTaubin
