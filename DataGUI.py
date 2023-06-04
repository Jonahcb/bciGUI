import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
import TifProcessor as tp

# constants
pixelps = 3.4 / 65536.0
fps = 3.4
spf = 0.294
mspl = 1.15

num_channels = 4
channel_color = {0: 'Green', 1: 'Blue', 2: 'Yellow', 3: 'Red'}

# Define the layout of the GUI
layout = [
    [sg.Checkbox('Channel 1', key='channel1'), sg.Checkbox('Channel 2', key='channel2'),
     sg.Checkbox('Channel 3', key='channel3'), sg.Checkbox('Channel 4', key='channel4')],
    [sg.Button('Average Across Trials', size=(10, 1))],
    [sg.Button('Single Trial', size=(10, 1))],
    [sg.Button('Plot', size=(10, 1)),
     sg.Button('Clear', size=(10, 1)), sg.Exit()]
]

# Create the PySimpleGUI window
sg.theme('DarkBlue3')
window = sg.Window('Data Plotter', layout)


# Define a function to plot the selected datasets
def plot_data(selected_sets, type, channels):
    # initialize time series for averaging across line
    time_series = []
    for i in range(selected_sets[0][0].size):
        time_series.append((i * mspl) / 1000.0)

    time_series = np.array(time_series)

    # create figure to hold 13 plots
    fig, axes = plt.subplots(2, 6)

    # change dimensions of figure
    fig.set_figwidth(25)
    fig.set_figheight(5)

    # orientation label counter
    counter = 0

    # iterate through numpy array of subplots
    for i, axis in enumerate(axes):

        # create subplots by using number of subplot as orientation index
        for j, axe in enumerate(axis):

            # generate label
            label = counter

            axe.set_title(label)
            # plot each channel on subplot
            for c in range(num_channels):

                # only plot selected channels
                if (c in channels):
                    axe.scatter(time_series, selected_sets[i * 2 + j][c], label=c, s=0.1,
                                color=channel_color[c])
            # increment label counter
            counter += 30

    # label x and y axis for first graph only
    axes[0, 0].set_xlabel("Time (s)")
    axes[0, 0].set_ylabel("Intensity")

    fig.tight_layout(pad=5.0)
    plt.show()


# define function to plot single selected trials
def plot_single_trial(selected_sets):
    # initialize time series for averaging across line
    time_series = []
    for i in range(selected_sets[0][0].size):
        time_series.append((i * mspl) / 1000.0)

    time_series = np.array(time_series)

    # calculate row, col for subplots NEED TO FINISH
    np.size(selected_sets, axis=0)

    # create figure to hold correct # plots
    fig, axes = plt.subplots(2, 6)

    # change dimensions of figure
    fig.set_figwidth(25)
    fig.set_figheight(5)

    # orientation label counter
    counter = 0

    # iterate through numpy array of subplots
    for i, axis in enumerate(axes):

        # create subplots by using number of subplot as orientation index
        for j, axe in enumerate(axis):

            # generate label
            label = counter

            axe.set_title(label)
            # plot each channel on subplot
            for c in range(num_channels):
                axe.scatter(time_series, selected_sets[i * 2 + j][c], label=c, s=0.1,
                            color=channel_color[c])
            # increment label counter
            counter += 30

    # label x and y axis for first graph only
    axes[0, 0].set_xlabel("Time (s)")
    axes[0, 0].set_ylabel("Intensity")

    fig.tight_layout(pad=5.0)
    plt.show()


# function to choose which trial to plot
def choose_trial():
    layout = [[sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(1, 10)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(10, 20)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(20, 30)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(30, 40)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(50, 60)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(60, 70)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(70, 79)],
              [sg.Button('Select', size=(10, 1))]]

    window = sg.Window("Select Trial", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # returns a list with indexes of trials to plot
        elif event == "Select":
            list = []
            for key in values:
                if values[key] is True:
                    list.append(key)
            return list
            break

    window.close()


# Create an event loop for the PySimpleGUI window
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break

    # plot data that is average across trials
    if event == 'Average Across Trials':
        type = 1

        # process data
        data = tp.average()

    # plot data from single trial
    elif event == 'Single Trial':
        type = 0

        # list of which trials to plot
        trials = choose_trial()

        # process data and select the trials we want
        data = tp.single_trial(trials)

    # choose which channels to plot
    elif event == 'Plot':

        # create list with channels to plot
        channels = []

        # create count to keep track of which channel we are checking
        channelCount = 0

        for key in values:
            if values[key] == True:
                channels.append(channelCount)

                # increment count to check next channel
                channelCount = channelCount + 1

        # Plot the selected datasets and channels
        plot_data(data, type, channels)

# Close the PySimpleGUI window
window.close()
