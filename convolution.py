import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
# from scipy.signal import wiener
from skimage.restoration import wiener

# Define a simple object (e.g., a bright square in the middle)
object = np.zeros((100, 100))
object[40:60, 40:60] = 1

# Define the PSF (e.g., a Gaussian)
x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
x, y = np.meshgrid(x, y)
psf = np.exp(-(x**2 + y**2) / 2)

# Convolve object with PSF
blurred = convolve2d(object, psf, mode='same')

# Add Gaussian noise
noise = 0.5 * np.random.normal(size=blurred.shape)
noisy_blurred = blurred + noise

# Deconvolution using Wiener filter
deconvolved = wiener(noisy_blurred, psf, 0.1)

# Plotting
fig, axs = plt.subplots(1, 5, figsize=(15, 5))
axs[0].imshow(object, cmap='gray')
axs[0].set_title('Original Object')
axs[1].imshow(psf, cmap='gray')
axs[1].set_title('Point Spread Function')
axs[2].imshow(noise, cmap='gray')
axs[2].set_title('Noise')
axs[3].imshow(noisy_blurred,cmap='gray')
axs[3].set_title('Blurred and Noisy')
axs[4].imshow(deconvolved, cmap='gray')
axs[4].set_title('Deconvolved Image')
plt.show()
