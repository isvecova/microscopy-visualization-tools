% Define object
object = zeros(100, 100);
object(40:60, 40:60) = 1;

% Define PSF
x = linspace(-10, 10, 100);
y = linspace(-10, 10, 100);
[X, Y] = meshgrid(x, y);
psf = exp(-(X.^2 + Y.^2) / 20);

% Convolve
blurred = conv2(object, psf, 'same');

% Add noise
noisy_blurred = imnoise(blurred, 'gaussian', 0, 0.01);

% Deconvolution
deconvolved = deconvwnr(noisy_blurred, psf);

% Display
figure;
subplot(1,4,1); imshow(object, []); title('Original Object');
subplot(1,4,2); imshow(psf, []); title('Point Spread Function');
subplot(1,4,3); imshow(noisy_blurred, []); title('Blurred and Noisy');
subplot(1,4,4); imshow(deconvolved, []); title('Deconvolved Image');
