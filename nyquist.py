import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from skimage.draw import disk

class InteractivePixelationProcessor:
    def __init__(self, ax, btn_ax, slider_ax, point_size=5, image_size=(100, 100)):
        self.ax = ax
        self.image_size = image_size
        self.point_size = point_size
        self.image = np.zeros(image_size)  # Create an empty image
        self.points = []
        self.pixelated_image = self.image.copy()
        self.cid = ax.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax.scatter([], [], s=100)  # Visual representation of points

        # Button for processing the image
        self.btn_process = Button(btn_ax, 'Process', color='lightgoldenrodyellow', hovercolor='0.975')
        self.btn_process.on_clicked(self.process_image)

        # Slider for adjusting pixel size
        self.pixel_size_slider = Slider(slider_ax, 'Pixel Size', 1, 20, valinit=5, valstep=1)

    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        x, y = int(event.xdata), int(event.ydata)
        self.points.append((x, y))
        self.update_image_with_points()

    def update_image_with_points(self):
        # Clear image
        self.image.fill(0)
        # Update image with new points
        for x, y in self.points:
            rr, cc = disk((y, x), radius=self.point_size, shape=self.image.shape)
            self.image[rr, cc] = 1
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.imshow(self.image, cmap='gray')
        self.scatter.set_offsets(self.points)
        self.scatter.set_sizes([np.pi * self.point_size**2] * len(self.points))
        self.ax.set_xlim(0, self.image_size[1])
        self.ax.set_ylim(self.image_size[0], 0)
        self.ax.figure.canvas.draw_idle()

    def process_image(self, event):
        pixel_size = int(self.pixel_size_slider.val)
        self.pixelated_image = self.pixelate_image(self.image, pixel_size)
        self.show_results()

    def pixelate_image(self, image, pixel_size):
        height, width = image.shape
        pixelated = np.zeros_like(image)
        for i in range(0, height, pixel_size):
            for j in range(0, width, pixel_size):
                pixel_value = np.mean(image[i:i + pixel_size, j:j + pixel_size])
                pixelated[i:i + pixel_size, j:j + pixel_size] = pixel_value
        return pixelated

    def show_results(self):
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        axs[0].imshow(self.image, cmap='gray')
        axs[0].set_title('Original Image')
        axs[1].imshow(self.pixelated_image, cmap='gray')
        axs[1].set_title('Pixelated Image')
        plt.show()

# Setup the figure and axes
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
ax.set_xlim(0, 99)
ax.set_ylim(0, 99)
btn_ax = plt.axes([0.1, 0.05, 0.1, 0.075])  # Adjust button position and size
slider_ax = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')  # Slider position and size
processor = InteractivePixelationProcessor(ax, btn_ax, slider_ax)

plt.show()
