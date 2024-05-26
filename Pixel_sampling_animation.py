import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec

imsize = 500

class InteractiveImageProcessor:
    def __init__(self, ax_drawing, ax_original, ax_pixelated, slider_size, slider_pix, point_size=5, image_size=(imsize, imsize), gaussian_extent_multiplier=5):
        self.ax = ax_drawing
        self.image_size = image_size
        self.point_size = point_size
        self.image = np.zeros(image_size)  # Create an empty image
        self.points = []
        self.cid = ax_drawing.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax_drawing.scatter([], [], s=100)  # Visual representation of points
        self.plot_created = False
        self.plot_figure = []
        self.gaussian_extent_multiplier = gaussian_extent_multiplier

        # Slider for adjusting point radius
        self.radius_slider = slider_size
        self.radius_slider.on_changed(self.update_image_based_on_radius)
        self.pixel_slider = slider_pix
        self.pixel_slider.on_changed(self.update_plot)

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
        self.update_plot([])

    def pixelate_image(self, image, pixel_size):
        if pixel_size <= 1:
            return self.image
        height, width = self.image.shape
        pixelated = np.zeros_like(self.image)
        for i in range(0, height, pixel_size):
            for j in range(0, width, pixel_size):
                pixel_value = np.mean(image[i:i + pixel_size, j:j + pixel_size])
                pixelated[i:i + pixel_size, j:j + pixel_size] = pixel_value
        return pixelated

    def update_plot(self,event):
        self.scatter.set_offsets(self.points)
        self.scatter.set_sizes([np.pi * (self.radius_slider.val**2)/10] * len(self.points))
        self.ax.figure.canvas.draw_idle()

        ax_original.imshow(self.image, cmap='gray')
        pixelated_image = self.pixelate_image(self.image, int(slider_pix.val))
        ax_pixelated.imshow(pixelated_image, cmap='gray')

        fig.canvas.draw_idle()

    plt.show()

# Function to find divisors
def find_divisors(n):
    divisors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return sorted(divisors)
        
# Setup the figure and axes
fig = plt.figure()
gs = gridspec.GridSpec(4, 2, height_ratios=[1, 1, 0.05, 0.05])  # Define the grid layout
ax_drawing = fig.add_subplot(gs[0, :])
ax_original = fig.add_subplot(gs[1, 0])
ax_pixelated = fig.add_subplot(gs[1, 1])
ax_slider_size = fig.add_subplot(gs[2, :])
ax_slider_pix = fig.add_subplot(gs[3, :])

#plt.subplots_adjust(left=0.25, bottom=0.25)
ax_drawing.set_xlim(0, imsize-1)
ax_drawing.set_ylim(0, imsize-1)
ax_drawing.set_xticks([])
ax_drawing.set_yticks([])
ax_drawing.set_aspect('equal')
ax_drawing.set_title('Add fluorophores by clicking')

ax_original.set_title('Original image')
ax_original.set_xticks([])
ax_original.set_yticks([])

ax_pixelated.set_title('Pixelated image')
ax_pixelated.set_xticks([])
ax_pixelated.set_yticks([])

# Slider for adjusting pixel size
slider_size = Slider(ax_slider_size, 'Point size', 1, imsize/5, valinit=10, valstep=1)
slider_pix = Slider(ax_slider_pix, 'Pixel size', 1, imsize/2, valinit=1, valstep=find_divisors(imsize))
processor = InteractiveImageProcessor(ax_drawing, ax_original, ax_pixelated, slider_size, slider_pix)

plt.tight_layout()
plt.show()
