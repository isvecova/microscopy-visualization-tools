import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from scipy.fft import fft2, ifft2, fftshift

# Define a simple object (e.g., a bright square in the middle)
object = np.zeros((100, 100))
object[40:60, 40:60] = 1

# Define the PSF (e.g., a Gaussian)
x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
x, y = np.meshgrid(x, y)
psf = np.exp(-(x**2 + y**2) / 20)

# Convolve object with PSF
blurred = convolve2d(object, psf, mode='same')

# Fourier transform of the blurred image and the PSF
F_blurred = fft2(blurred)
F_psf = fft2(psf, s=blurred.shape)

# Avoid division by zero or very small numbers in the Fourier domain
epsilon = 1e-5
inverse_filter = F_psf / (F_psf**2 + epsilon)

# Applying the inverse filter
recovered = ifft2(F_blurred * inverse_filter)
recovered = np.abs(recovered)

# Plotting
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
axs[0].imshow(blurred, cmap='gray')
axs[0].set_title('Blurred Image')
axs[1].imshow(np.abs(inverse_filter), cmap='gray')
axs[1].set_title('Inverse Filter')
axs[2].imshow(recovered, cmap='gray')
axs[2].set_title('Recovered Image using Inverse Filter')
plt.show()
