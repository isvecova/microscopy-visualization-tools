import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from scipy.signal import convolve2d
from skimage.restoration import wiener, richardson_lucy
from numpy.fft import rfft2, irfft2

# Initial parameters
initial_spread = 20
initial_balance = 0.1
initial_noise = 0.005

# Define a simple object (e.g., a bright square in the middle)
object = np.zeros((100, 100))
# object[40:60, 40:60] = 1
object[48:52,48:52] = 1

# Setup the figure and axes
fig, axs = plt.subplots(2, 3, figsize=(15, 8))  # Changed to accommodate 2 rows and 3 columns
plt.subplots_adjust(left=0.1, bottom=0.25)

# Display initial images
img_original = axs[0, 0].imshow(object, cmap='gray')
axs[0, 0].set_title('Original Object')
axs[0, 0].axis('off')

img_psf = axs[0, 1].imshow(object, cmap='gray')  # Placeholder for PSF
axs[0, 1].set_title('Point Spread Function')
axs[0, 1].axis('off')

img_noise = axs[0, 2].imshow(object, cmap='gray')  # Placeholder for Noise
axs[0, 2].set_title('Noise')
axs[0, 2].axis('off')

img_blurred = axs[1, 0].imshow(object, cmap='gray')  # Placeholder for Blurred and Noisy Image
axs[1, 0].set_title('Blurred and Noisy')
axs[1, 0].axis('off')

img_deconvolved = axs[1, 1].imshow(object, cmap='gray')  # Placeholder for Deconvolved Image
axs[1, 1].set_title('Deconvolved Image')
axs[1, 1].axis('off')

# Merge last subplot space for aesthetical adjustment
fig.delaxes(axs[1][2])

# Add sliders for interactive control
axcolor = 'lightgoldenrodyellow'
ax_spread = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_balance = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axcolor)
ax_noise = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)

s_spread = Slider(ax_spread, 'PSF Spread', 5, 50, valinit=initial_spread)
s_balance = Slider(ax_balance, 'Wiener Balance', 0, 0.5, valinit=initial_balance)
s_noise = Slider(ax_noise, 'Noise Level', 0, 0.01, valinit=initial_noise)

# Add Radio Buttons for method selection
rax = plt.axes([0.05, 0.7, 0.15, 0.15], facecolor=axcolor)
radio = RadioButtons(rax, ('Wiener', 'Inverse','Iterative'))

def update(val):
    spread = s_spread.val
    balance = s_balance.val
    noise = s_noise.val
    method = radio.value_selected

    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    x, y = np.meshgrid(x, y)
    psf = np.exp(-(x**2 + y**2) / spread)
    psf /= psf.sum()  # Normalize PSF so that it sums to 1
    # print('psf')
    # print(psf.dtype)
    # print(psf.min(),psf.max())
    blurred = convolve2d(object, psf, mode='same')
    # blurred = irfft2(rfft2(psf)*rfft2(object))
    # print('blurred')
    # print(blurred.dtype)
    # print(blurred.min(),blurred.max())
    noise_component = noise * np.random.normal(size=blurred.shape)
    # print('noise component')
    # print(noise_component.dtype)
    noisy_blurred = blurred + noise_component
    # noisy_blurred = blurred/blurred.max() + noise_component
    #noisy_blurred = noisy_blurred/(noisy_blurred.max())
    # print('noisy')
    # print(noisy_blurred.dtype)
    if method == 'Wiener':
        print('in wiener')
        deconvolved = wiener(noisy_blurred, psf, balance)
    elif method == 'Inverse':
        print('in inverse')
        # deconvolved = deconvolve2d(blurred,psf)
        f_psf = rfft2(psf, s=noisy_blurred.shape)
        f_blurred = rfft2(object)*f_psf
        f_noise = rfft2(noise_component)

        print('any zeros')
        print(np.any(f_psf == 0))
        with np.errstate(divide='ignore', invalid='ignore'):
            f_deconvolved =  f_blurred / f_psf + f_noise / f_psf
            # f_deconvolved = np.nan_to_num(f_deconvolved)
        deconvolved = irfft2(f_deconvolved)
    elif method == 'Iterative':
        deconvolved = richardson_lucy(noisy_blurred,psf)
    #deconvolved = wiener(noisy_blurred, psf, balance)
    print(deconvolved.min(),deconvolved.max())
    print(method)

    # Normalize each image for better visibility
    psf_normalized = (psf - np.min(psf)) / (np.max(psf) - np.min(psf))
    noise_component_normalized = (noise_component - np.min(noisy_blurred)) / (np.max(noisy_blurred) - np.min(noisy_blurred))
    noisy_blurred_normalized = (noisy_blurred - np.min(noisy_blurred)) / (np.max(noisy_blurred) - np.min(noisy_blurred))
    deconvolved_normalized = (deconvolved - np.min(deconvolved)) / (np.max(deconvolved) - np.min(deconvolved))

    img_psf.set_data(psf_normalized)
    img_noise.set_data(noise_component_normalized)  # For noise, normalization might not be needed as we visualize the raw noise pattern
    img_blurred.set_data(noisy_blurred_normalized)
    img_deconvolved.set_data(deconvolved_normalized)
    fig.canvas.draw_idle()

# Call update function on slider value change
s_spread.on_changed(update)
s_balance.on_changed(update)
s_noise.on_changed(update)
radio.on_clicked(update)

update(None)
plt.show()
