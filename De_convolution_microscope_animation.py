import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider, RadioButtons
from scipy.signal import convolve2d
from skimage.restoration import wiener, unsupervised_wiener, richardson_lucy
from numpy.fft import rfft2, irfft2
from scipy.ndimage import binary_dilation
from skimage.draw import disk
import matplotlib.gridspec as gridspec

class InteractiveImageProcessor:
    def __init__(self,ax_drawing,ax_original,ax_psf,ax_noise,ax_blurred,ax_deconvolved,btn,s_pointsize,s_spread,s_noise,s_balance, point_size=5, image_size=(100, 100)):
        self.ax = ax_drawing
        self.image_size = image_size
        self.point_size = point_size
        self.image = np.zeros(image_size)  # Create an empty image
        self.points = []
        self.cid = ax_drawing.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax_drawing.scatter([], [], s=100)  # Visual representation of points
        self.plot_created = False
        self.plot_figure = []

        s_pointsize.on_changed(self.update_image_based_on_radius)  
        # Call update function on slider value change
        s_spread.on_changed(self.process_image)
        s_balance.on_changed(self.process_image)
        s_noise.on_changed(self.process_image)
        btn.on_clicked(self.process_image)

        # Display initial images
        self.img_original = ax_original.imshow(self.image, cmap='gray')
        self.img_psf = ax_psf.imshow(self.image, cmap='gray')  # Placeholder for PSF
        self.img_noise = ax_noise.imshow(self.image, cmap='gray')  # Placeholder for Noise
        self.img_blurred = ax_blurred.imshow(self.image, cmap='gray')  # Placeholder for Blurred and Noisy Image
        self.img_deconvolved = ax_deconvolved.imshow(self.image, cmap='gray')  # Placeholder for Deconvolved Image


    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        x, y = int(event.xdata), int(event.ydata)
        self.points.append((x, y))
        print(len(self.points))
        self.update_image_based_on_radius(s_pointsize.val)

    def update_image_based_on_radius(self, val):
        # Clear image
        self.image.fill(0)
        # Update image with new radius for each point
        for x, y in self.points:
            rr, cc = disk((y, x), radius=val, shape=self.image.shape)
            self.image[rr, cc] = 1
        self.image = np.flipud(self.image)
        self.update_plot()

    def update_plot(self):
        self.scatter.set_offsets(self.points)
        self.scatter.set_sizes([np.pi * s_pointsize.val**2] * len(self.points))
        self.ax.figure.canvas.draw_idle()

        self.img_original = ax_original.imshow(self.image,cmap='gray')
        self.process_image([])

    def process_image(self, event):

        print('processing image')

        spread = s_spread.val
        balance = s_balance.val
        noise = s_noise.val
        method = btn.value_selected

        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        psf = np.exp(-(x**2 + y**2) / spread)
        psf /= psf.sum()  # Normalize PSF so that it sums to 1
        blurred = convolve2d(self.image, psf, mode='same')
        noise_component = noise * np.random.normal(size=blurred.shape)
        noisy_blurred = blurred + noise_component
        if method == 'Wiener':
            deconvolved = wiener(noisy_blurred, psf, balance)
        elif method == 'Inverse':
            f_psf = rfft2(psf, s=noisy_blurred.shape)
            f_blurred = rfft2(self.image)*f_psf
            f_noise = rfft2(noise_component)
            with np.errstate(divide='ignore', invalid='ignore'):
                f_deconvolved =  f_blurred / f_psf + f_noise / f_psf
            deconvolved = irfft2(f_deconvolved)
        elif method == 'Iterative':
            deconvolved = richardson_lucy(noisy_blurred,psf)
        elif method == 'Unsupervised Wiener':
            deconvolved, chains = unsupervised_wiener(noisy_blurred,psf)

        # Normalize each image for better visibility
        psf_normalized = (psf - np.min(psf)) / (np.max(psf) - np.min(psf))
        noise_component_normalized = (noise_component - np.min(noisy_blurred)) / (np.max(noisy_blurred) - np.min(noisy_blurred))
        noisy_blurred_normalized = (noisy_blurred - np.min(noisy_blurred)) / (np.max(noisy_blurred) - np.min(noisy_blurred))
        deconvolved_normalized = (deconvolved - np.min(deconvolved)) / (np.max(deconvolved) - np.min(deconvolved))

        # self.img_psf.set_data(psf_normalized)
        # self.img_noise.set_data(noise_component_normalized)  # For noise, normalization might not be needed as we visualize the raw noise pattern
        # self.img_blurred.set_data(noisy_blurred_normalized)
        # self.img_deconvolved.set_data(deconvolved_normalized)
        self.img_psf = ax_psf.imshow(psf_normalized, cmap='gray')  # Placeholder for PSF
        self.img_noise = ax_noise.imshow(noise_component_normalized, cmap='gray')  # Placeholder for Noise
        self.img_blurred = ax_blurred.imshow(noisy_blurred_normalized, cmap='gray')  # Placeholder for Blurred and Noisy Image
        self.img_deconvolved = ax_deconvolved.imshow(deconvolved_normalized, cmap='gray')  # Placeholder for Deconvolved Image
        fig.canvas.draw_idle()

        plt.show()


# Setup the figure and axes
# Setup the figure and axes
fig = plt.figure()
gs = gridspec.GridSpec(5, 3, height_ratios=[0.1, 0.1, 0.5, 1, 1])  # Define the grid layout
ax_drawing = fig.add_subplot(gs[0:3, 0])
ax_drawing.set_title('Click to add fluorophores')
ax_drawing.set_aspect('equal')
ax_drawing.set_xticks([])
ax_drawing.set_yticks([])
ax_drawing.set_xlim(0,99)
ax_drawing.set_ylim(0,99)
ax_original = fig.add_subplot(gs[3, 0])
ax_original.set_title('Object')
ax_original.set_xticks([])
ax_original.set_yticks([])
ax_psf = fig.add_subplot(gs[3, 1])
ax_psf.set_title('Point spread function')
ax_psf.set_xticks([])
ax_psf.set_yticks([])
ax_noise = fig.add_subplot(gs[3, 2])
ax_noise.set_title('Noise')
ax_noise.set_xticks([])
ax_noise.set_yticks([])
ax_blurred = fig.add_subplot(gs[4, 0])
ax_blurred.set_title('Image')
ax_blurred.set_xticks([])
ax_blurred.set_yticks([])
ax_deconvolved = fig.add_subplot(gs[4, 2])
ax_deconvolved.set_title('Deconvolved image')
ax_deconvolved.set_xticks([])
ax_deconvolved.set_yticks([])
ax_button = fig.add_subplot(gs[4, 1])
ax_button.set_title('Deconvolution method')
ax_button.axis('off')
ax_slider_pointsize = fig.add_subplot(gs[0, 1])
ax_slider_spread = fig.add_subplot(gs[0, 2])
ax_slider_noise = fig.add_subplot(gs[1, 1])
ax_slider_balance = fig.add_subplot(gs[1, 2])

# Initial parameters
initial_spread = 20
initial_balance = 0.1
initial_noise = 0.005

btn = RadioButtons(ax_button, ('Wiener', 'Unsupervised Wiener', 'Inverse', 'Iterative'))

s_pointsize = Slider(ax_slider_pointsize, 'Object size', 1, 20, valinit=5, valstep=1)
s_spread = Slider(ax_slider_spread, 'PSF spread', 5, 50, valinit=initial_spread)
s_noise = Slider(ax_slider_noise, 'Noise level', 0, 0.01, valinit=initial_noise)
s_balance = Slider(ax_slider_balance, 'Wiener balance', 0, 0.5, valinit=initial_balance)

processor = InteractiveImageProcessor(ax_drawing,ax_original,ax_psf,ax_noise,ax_blurred,ax_deconvolved,btn,s_pointsize,s_spread,s_noise,s_balance)

plt.tight_layout()
plt.show()
