import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider, RadioButtons
from scipy.signal import convolve2d
from skimage.restoration import wiener, unsupervised_wiener, richardson_lucy
from numpy.fft import rfft2, irfft2
from scipy.ndimage import binary_dilation
from skimage.draw import disk

imsize = 500

class InteractiveImageProcessor:
    def __init__(self, ax, btn_ax, slider_ax, point_size=5, image_size=(imsize, imsize), gaussian_extent_multiplier=5):
        self.ax = ax
        self.image_size = image_size
        self.point_size = point_size
        self.image = np.zeros(image_size)  # Create an empty image
        self.points = []
        self.cid = ax.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax.scatter([], [], s=100)  # Visual representation of points
        self.plot_created = False
        self.plot_figure = []
        self.gaussian_extent_multiplier = gaussian_extent_multiplier

        # Button for processing the image
        self.btn_process = Button(btn_ax, 'Process', color='lightgoldenrodyellow', hovercolor='0.975')
        self.btn_process.on_clicked(self.process_image)

        # Slider for adjusting point radius
        self.radius_slider = Slider(slider_ax, 'Radius', 1, imsize/5, valinit=10, valstep=1)
        self.radius_slider.on_changed(self.update_image_based_on_radius)

    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        x, y = int(event.xdata), int(event.ydata)
        self.points.append((x, y))
        self.update_image_based_on_radius(self.radius_slider.val)

    def gaussian(self, x, y, x0, y0, sigma):
        return np.exp(-((x - x0)**2 + (y - y0)**2) / (2 * sigma**2))

    def update_image_based_on_radius(self, val):
        # Clear image
        self.image.fill(0)
        # Update image with new radius for each point
        for x, y in self.points:
            size = 2 * val * self.gaussian_extent_multiplier + 1
            x_grid, y_grid = np.meshgrid(np.arange(size), np.arange(size))
            gaussian = self.gaussian(x_grid, y_grid, val * self.gaussian_extent_multiplier, val * self.gaussian_extent_multiplier, val*2)
            x_start = max(0, x - val * self.gaussian_extent_multiplier)
            y_start = max(0, y - val * self.gaussian_extent_multiplier)
            x_end = min(self.image_size[1], x + val * self.gaussian_extent_multiplier + 1)
            y_end = min(self.image_size[0], y + val * self.gaussian_extent_multiplier + 1)

            patch_x_start = val * self.gaussian_extent_multiplier - x if x < val * self.gaussian_extent_multiplier else 0
            patch_y_start = val * self.gaussian_extent_multiplier - y if y < val * self.gaussian_extent_multiplier else 0
            patch_x_end = size if x + val * self.gaussian_extent_multiplier + 1 <= self.image_size[1] else size - (x + val * self.gaussian_extent_multiplier + 1 - self.image_size[1])
            patch_y_end = size if y + val * self.gaussian_extent_multiplier + 1 <= self.image_size[0] else size - (y + val * self.gaussian_extent_multiplier + 1 - self.image_size[0])

            self.image[y_start:y_end, x_start:x_end] += gaussian[patch_y_start:patch_y_end, patch_x_start:patch_x_end]
        
        self.image = np.flipud(self.image)
        self.update_plot()

    def update_plot(self):
        self.scatter.set_offsets(self.points)
        self.scatter.set_sizes([np.pi * self.radius_slider.val**2] * len(self.points))
        self.ax.figure.canvas.draw_idle()

    def process_image(self, event):

        def pixelate_image(image, pixel_size):
            if pixel_size <= 1:
                return self.image
            height, width = self.image.shape
            pixelated = np.zeros_like(self.image)
            for i in range(0, height, pixel_size):
                for j in range(0, width, pixel_size):
                    pixel_value = np.mean(image[i:i + pixel_size, j:j + pixel_size])
                    pixelated[i:i + pixel_size, j:j + pixel_size] = pixel_value
            return pixelated

        def update(val):
            pixel_size = int(slider.val)
            pixelated_image = pixelate_image(original_image, pixel_size)
            ax2.imshow(pixelated_image, cmap='gray')
            fig.canvas.draw_idle()

        # Create the original image with dots
        original_image = self.image

        # Setup the figure and axes
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        plt.subplots_adjust(bottom=0.25)

        # Display the original image
        ax1.imshow(original_image, cmap='gray')
        ax1.set_title('Original Image')
        ax1.axis('off')

        # Display the pixelated image
        pixelated_image = pixelate_image(original_image, 5)
        ax2.imshow(pixelated_image, cmap='gray')
        ax2.set_title('Pixelated Image')
        ax2.axis('off')

        # Slider for adjusting pixel size
        ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, 'Pixel Size', 1, imsize/2, valinit=10, valstep=1)
        slider.on_changed(update)

        plt.show()


# Setup the figure and axes
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
ax.set_xlim(0, imsize-1)
ax.set_ylim(0, imsize-1)
btn_ax = plt.axes([0.1, 0.05, 0.1, 0.075])  # Adjust button position and size
slider_ax = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')  # Slider position and size
processor = InteractiveImageProcessor(ax, btn_ax, slider_ax)


plt.show()
