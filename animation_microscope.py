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

# flag to prevent recursive activation of the update function
programatically_activated = False

# Detected intensity history
intensity_history = []
max_history_length = 50

# Create the main figure and axes
fig, (ax, ax_hist) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
plt.subplots_adjust(left=0.25, bottom=0.35)

# Set limits and plot initial points
ax.set_xlim(0, 1)
ax.set_ylim(0, 2)  # Only for visual spacing purposes
fluorophore_dot, = ax.plot([fluorophore_position], [1], 'ro', label='Fluorophore')  # ensure sequence format
excitation_dot, = ax.plot([initial_excitation_position], [1], 'go', label='Excitation Point')
detection_dot, = ax.plot([initial_detection_position], [1], 'bo', label='Detection Point')
ax.legend(loc='upper center')

# Add slider for controlling positions
axcolor = 'lightgoldenrodyellow'
ax_exc = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_det = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)

slider_exc = Slider(ax_exc, 'Excitation Position', 0, 1, valinit=initial_excitation_position)
slider_det = Slider(ax_det, 'Detection Position', 0, 1, valinit=initial_detection_position)

# Checkbox to link movements
rax = plt.axes([0.05, 0.5, 0.15, 0.15], facecolor=axcolor)
check = CheckButtons(rax, ['Link Movements'], [False])

# Setting up the intensity history plot
ax_hist.set_xlim(0, 1)
ax_hist.set_ylim(0, 1)
ax_hist.set_title("Detected Intensity History")
intensity_line, = ax_hist.plot([], [], 'm-')

def update(val):
    print(fixed_distance)
    global programatically_activated
    if programatically_activated:
        return
    exc_pos = slider_exc.val
    det_pos = slider_det.val
    # print(exc_pos)
    # print(det_pos)
    # print(val)

    if check.get_status()[0]:  # Check if the checkbox is ticked
        global p
        if val == exc_pos:  # If excitation slider moved
            print('exc')
            det_pos = exc_pos + fixed_distance
            # if det_pos > 1 or det_pos < 0:  # Ensure detection stays within bounds
            #     det_pos = np.clip(det_pos, 0, 1)
            #     exc_pos = det_pos - fixed_distance
            programatically_activated = True
            slider_det.set_val(det_pos)
            programatically_activated = False
        elif val == det_pos:  # If detection slider moved
            print('det')
            exc_pos = det_pos - fixed_distance
            # if exc_pos > 1 or exc_pos < 0:  # Ensure excitation stays within bounds
            #     exc_pos = np.clip(exc_pos, 0, 1)
            #     det_pos = exc_pos + fixed_distance
            programatically_activated = True
            slider_exc.set_val(exc_pos)
            programatically_activated = False

    # Calculate distances and intensities
    excitation_distance = abs(fluorophore_position - exc_pos)
    detection_distance = abs(fluorophore_position - det_pos)
    # fluorescence_intensity = max(0, radius_effect - excitation_distance) / radius_effect
    # detected_intensity = fluorescence_intensity * max(0, radius_effect - detection_distance) / radius_effect

    # Updated intensity calculations using Gaussian decay
    fluorescence_intensity = np.exp(-(excitation_distance**2) / (2 * sigma**2))
    detected_intensity = fluorescence_intensity * np.exp(-(detection_distance**2) / (2 * sigma**2))

    # Update plot elements
    excitation_dot.set_data([exc_pos], [1])
    detection_dot.set_data([det_pos], [1])
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
