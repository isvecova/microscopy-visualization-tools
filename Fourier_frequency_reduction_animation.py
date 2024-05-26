import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.color import rgb2gray
from skimage import color, exposure, transform
from skimage import exposure

import os

from matplotlib.widgets import Button, Slider

import tkinter as tk
from tkinter import filedialog

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Function to load and preprocess the image
def load_image(filepath):
    image = imread(filepath)
    if image.shape[2] == 3:
        image = rgb2gray(image)
    image = exposure.rescale_intensity(image, out_range='float64')
    return image

def visualize_image(image, percentage):
    global fig, ax, fo, fa, io, ia

    fourier_orig, fourier_masked, image_filtered = process_images(image, percentage)

    io = ax[0].imshow(image, cmap = 'gray')
    ax[0].set_title('Greyscale Image', fontsize = f_size)
    fo = ax[1].imshow(np.log(abs(fourier_orig)), cmap='gray')
    ax[1].set_title('Original Fourier', fontsize = f_size)
    fa = ax[2].imshow(np.log(abs(fourier_masked)), cmap='gray')
    ax[2].set_title('Masked Fourier', fontsize = f_size)
    ia = ax[3].imshow(abs(image_filtered), cmap='gray')
    ax[3].set_title('Transformed Greyscale Image', fontsize = f_size)
    for i in range(0,4):
        ax[i].set_xticks([])
        ax[i].set_yticks([])

def change_image(event):
    global image, fig, ax, fo, fa, io, ia
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    if file_path:
        image = load_image(file_path)

        # Clear the current axes
        for a in ax:
            a.clear()

        visualize_image(image, freq_slider.val)

        fig.canvas.draw_idle()


# Load the initial image
initial_image_file_name = "fourier_testing_images/wave.jpg"
initial_image_path = os.path.join(script_directory, initial_image_file_name)
image = load_image(initial_image_path)
percentage = 10
f_size = 15

def mask_circle(image, percentage):
    """
    Keep only a circle in the center of the image and make the rest of the image black.

    Parameters:
    image (numpy array): The input image.
    percentage (float): The percentage of the radius of the circle compared to the image size.

    Returns:
    numpy array: The masked image.
    """
    # Get the dimensions of the image
    x, y = image.shape[:2]

    # Calculate the center and radius of the circle
    center_x, center_y = x // 2, y // 2
    radius = int(min(center_x, center_y) * (percentage / 100))

    # Create a mask with a circle
    Y, X = np.ogrid[:x, :y]
    dist_from_center = np.sqrt((X - center_y)**2 + (Y - center_x)**2)
    mask = dist_from_center <= radius

    # Create an output image and apply the mask
    masked_image = np.ones_like(image)
    masked_image[mask] = image[mask]

    return masked_image

def process_images(image, percentage):

    fourier_orig = np.fft.fftshift(np.fft.fft2(image))
    fourier_masked = mask_circle(fourier_orig,percentage)
    image_filtered = np.fft.ifft2(fourier_masked)

    return fourier_orig,fourier_masked,image_filtered

fig, ax = plt.subplots(1,4,figsize=(15,5))

visualize_image(image, percentage)

# adjust the main plot to make room for the sliders
fig.subplots_adjust(left=0.05)

# Make a horizontal slider to control the frequency.
axfreq = fig.add_axes([0.02, 0.1, 0.01, 0.8])
freq_slider = Slider(
    ax=axfreq,
    label='Reduction',
    valmin=0.1,
    valmax=100,
    valinit=percentage,
    orientation="vertical"
)

# Button to change the image
axchange = fig.add_axes([0.45, 0.05, 0.1, 0.075])
change_button = Button(axchange, 'Change Image')

# The function to be called anytime a slider's value changes
def update(val):
    
    fourier_orig,fourier_masked,image_filtered = process_images(image,freq_slider.val)
    fo.set_data(np.log(abs(fourier_orig)))
    fa.set_data(np.log(abs(fourier_masked)))
    ia.set_data(abs(image_filtered))
    fig.canvas.draw_idle()


# register the update function with the slider
freq_slider.on_changed(update)

# Register the change image function with the button
change_button.on_clicked(change_image)

plt.show()
