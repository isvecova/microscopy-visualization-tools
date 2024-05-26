import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons

# Parameters
fluorophore_position = 0.5  # Fixed position of the fluorophore along a line (1D)
initial_excitation_position = 0.1
initial_detection_position = 0.9
fixed_distance = initial_detection_position - initial_excitation_position  # Maintain this distance
radius_effect = 0.5  # Radius of effective excitation and detection
sigma = 0.05
plot_heigth = 0.5

# flag to prevent recursive activation of the update function
programatically_activated = False

# Detected intensity history
intensity_history = []
max_history_length = 50

# Create the main figure and axes
fig, (ax, ax_hist) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]})
plt.tight_layout()
plt.subplots_adjust(right=0.75, bottom=0.20)

# Set limits and plot initial points
ax.set_xlim(0, 1)
ax.set_ylim(0, plot_heigth)  # Only for visual spacing purposes
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("System positioning")
fluorophore_dot, = ax.plot([fluorophore_position], [plot_heigth/2], 'r*', markersize=13, label='Fluorophore')  # ensure sequence format
excitation_dot, = ax.plot([initial_excitation_position], [plot_heigth/2], 'go', label='Excitation point')
detection_dot, = ax.plot([initial_detection_position], [plot_heigth/2], 'bs', label='Detection point')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# Add slider for controlling positions
axcolor = 'lightgoldenrodyellow'
ax_exc = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_det = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)

slider_exc = Slider(ax_exc, 'Excitation position', 0, 1, valinit=initial_excitation_position)
slider_det = Slider(ax_det, 'Detection position', 0, 1, valinit=initial_detection_position)

# Checkbox to link movements
rax = plt.axes([0.77, 0.5, 0.15, 0.15], facecolor=axcolor)
check = CheckButtons(rax, ['Link positions'], [False])

# Setting up the intensity history plot
ax_hist.set_xlim(0, 1)
ax_hist.set_ylim(0, 1)
ax_hist.set_xticks([])
ax_hist.set_yticks([])
ax_hist.set_title("Detected intensity history")
intensity_line, = ax_hist.plot([], [], 'm-')

def update(val):
    global programatically_activated
    if programatically_activated:
        return
    exc_pos = slider_exc.val
    det_pos = slider_det.val

    if check.get_status()[0]:  # Check if the checkbox is ticked
        global p
        if val == exc_pos:  # If excitation slider moved
            det_pos = exc_pos + fixed_distance
            programatically_activated = True
            slider_det.set_val(det_pos)
            programatically_activated = False
        elif val == det_pos:  # If detection slider moved
            exc_pos = det_pos - fixed_distance
            programatically_activated = True
            slider_exc.set_val(exc_pos)
            programatically_activated = False

    # Calculate distances and intensities
    excitation_distance = abs(fluorophore_position - exc_pos)
    detection_distance = abs(fluorophore_position - det_pos)

    # Updated intensity calculations using Gaussian decay
    fluorescence_intensity = np.exp(-(excitation_distance**2) / (2 * sigma**2))
    detected_intensity = fluorescence_intensity * np.exp(-(detection_distance**2) / (2 * sigma**2))

    # Update plot elements
    excitation_dot.set_data([exc_pos], [plot_heigth/2])
    detection_dot.set_data([det_pos], [plot_heigth/2])
    fluorophore_dot.set_color((1.0, 0, 0, fluorescence_intensity))  # Opacity based on emission intensity

    # Update intensity history plot
    # intensity_history.append(detected_intensity)
    # Add new intensity value to the history and ensure the list does not exceed the maximum length
    intensity_history.append(detected_intensity)
    if len(intensity_history) > max_history_length:
        intensity_history.pop(0)  # Remove the oldest element to maintain size
    x_data = np.linspace(0, 1, len(intensity_history))
    intensity_line.set_data(x_data, intensity_history)
    ax_hist.set_xlim(0, 1)
    
    fig.canvas.draw_idle()

def tie_sliders(val):
    global fixed_distance
    exc_pos = slider_exc.val
    det_pos = slider_det.val
    fixed_distance = det_pos - exc_pos

# Call update function when sliders or checkbox is changed
slider_exc.on_changed(update)
slider_det.on_changed(update)
check.on_clicked(tie_sliders)

plt.show()
