import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider, RadioButtons
from scipy.signal import convolve2d
from skimage.restoration import wiener, unsupervised_wiener, richardson_lucy
from numpy.fft import rfft2, irfft2
from scipy.ndimage import binary_dilation
from skimage.draw import disk

class InteractiveImageProcessor:
    def __init__(self, ax, btn_ax, slider_ax, point_size=5, image_size=(100, 100)):
        self.ax = ax
        self.image_size = image_size
        self.point_size = point_size
        self.image = np.zeros(image_size)  # Create an empty image
        self.points = []
        self.cid = ax.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax.scatter([], [], s=100)  # Visual representation of points
        self.plot_created = False
        self.plot_figure = []

        # Button for processing the image
        self.btn_process = Button(btn_ax, 'Process', color='lightgoldenrodyellow', hovercolor='0.975')
        self.btn_process.on_clicked(self.process_image)

        # Slider for adjusting point radius
        self.radius_slider = Slider(slider_ax, 'Radius', 1, 20, valinit=5, valstep=1)
        self.radius_slider.on_changed(self.update_image_based_on_radius)

    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        x, y = int(event.xdata), int(event.ydata)
        self.points.append((x, y))
        self.update_image_based_on_radius(self.radius_slider.val)

    def update_image_based_on_radius(self, val):
        # Clear image
        self.image.fill(0)
        # Update image with new radius for each point
        for x, y in self.points:
            rr, cc = disk((y, x), radius=val, shape=self.image.shape)
            self.image[rr, cc] = 1
        self.update_plot()

    def update_plot(self):
        self.scatter.set_offsets(self.points)
        self.scatter.set_sizes([np.pi * self.radius_slider.val**2] * len(self.points))
        self.ax.figure.canvas.draw_idle()

    def process_image(self, event):

        if self.plot_created:
            plt.close(self.plot_figure)
        self.plot_created = True

        # Initial parameters
        initial_spread = 20
        initial_balance = 0.1
        initial_noise = 0.005

        # Define a simple object
        object = self.image

        # Setup the figure and axes
        self.plot_figure, axs = plt.subplots(2, 3, figsize=(15, 8))  # Changed to accommodate 2 rows and 3 columns
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
        self.plot_figure.delaxes(axs[1][2])

        # Add sliders for interactive control
        axcolor = 'lightgoldenrodyellow'
        ax_spread = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
        ax_balance = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axcolor)
        ax_noise = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)

        s_spread = Slider(ax_spread, 'PSF Spread', 5, 50, valinit=initial_spread)
        s_balance = Slider(ax_balance, 'Wiener Balance', 0, 0.5, valinit=initial_balance)
        s_noise = Slider(ax_noise, 'Noise Level', 0, 0.01, valinit=initial_noise)

        # Add Radio Buttons for method selection
        rax = plt.axes([0.7, 0.4, 0.15, 0.15], facecolor=axcolor)
        radio = RadioButtons(rax, ('Wiener', 'Unsupervised Wiener', 'Inverse', 'Iterative'))

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
            elif method == 'Unsupervised Wiener':
                deconvolved, chains = unsupervised_wiener(noisy_blurred,psf)
            #deconvolved = wiener(noisy_blurred, psf, balance)
            # print(deconvolved.min(),deconvolved.max())
            # print(method)

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


# Setup the figure and axes
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
ax.set_xlim(0, 99)
ax.set_ylim(0, 99)
btn_ax = plt.axes([0.1, 0.05, 0.1, 0.075])  # Adjust button position and size
slider_ax = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')  # Slider position and size
processor = InteractiveImageProcessor(ax, btn_ax, slider_ax)


plt.show()
