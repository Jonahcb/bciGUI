import PySimpleGUI as sg
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import PCA
from SNLabBCI import TiffProcessor as tp, Grapher as g
import GUIHelper as ghelper

# constants
pixelps = 3.4 / 65536.0

# frames per second
fps = 3.4

# seconds per frame
spf = 0.294

# milliseconds per line
mspl = 1.15

# seconds per trial
spt = 6.174

# num of channels used
num_channels = 4

# dict with channel numbers and corresponding colors
channel_color = {0: 'Green', 1: 'Blue', 2: 'Gold', 3: 'Red'}

# filepath to save all csv files to
csv_path = '/Users/jonahbernard/Desktop/SN Lab/6.03.23/CSV Data'

# change from MacOS backend to Tkinter
matplotlib.use('TkAgg')

# Define the layout of the GUI
layout = [
    [sg.Text("Tiff Folder Path:")],
    [sg.Input(key="-TIFF_FOLDER_PATH-"), sg.FolderBrowse()],
    [sg.Text("Metadata Folder Path:")],
    [sg.Input(key="-METADATA_FOLDER_PATH-"), sg.FileBrowse()],
    [sg.Text("Graph Title:")],
    [sg.Input(key="-GRAPH_TITLE-", size=(80, 1))],
    [(sg.Button('Average By Orientation', size=(50, 1))),
     (sg.Button('Plot ', size=(20, 1)))],  # 1 space
    [(sg.Button('Record Noise Baseline', size=(50, 1)))],
    [(sg.Button('Average Across All Trials', size=(50, 1))),
     (sg.Button('Plot  ', size=(20, 1)))],  # 2 spaces
    [(sg.Button('Choose Trials', size=(50, 1))),
     (sg.Button('Plot   ', size=(20, 1)))],  # 3 spaces
    [(sg.Button('Subtract Noise From Dataset', size=(50, 1))),
     (sg.Button('Plot    ', size=(20, 1)))],  # 4 spaces
    [(sg.Button('Trial vs. Experiment', size=(50, 1))),
     (sg.Button('Plot     ', size=(20, 1)))],  # 5 spaces
    [(sg.Button('Standard Deviation', size=(50, 1))),
     (sg.Button('Plot      ', size=(20, 1)))],  # 6 spaces
    [(sg.Button('10 Trials Per Chart', size=(50, 1))),
     (sg.Button('Plot       ', size=(20, 1)))],  # 7 spaces
    [(sg.Button('Plot By Channel', size=(80, 1)))],
    [(sg.Button('Run All', size=(80, 1)))],
    [(sg.Button('Photon Count', size=(80, 1)))]
]

# Create the PySimpleGUI window
sg.theme('DarkBlue3')
window = sg.Window('Data Plotter', layout)

# Create an event loop for the PySimpleGUI window
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break

    # plot data that is average across trials
    if event == 'Average By Orientation':
        type = 1

        # process data
        data = tp.average(values["-TIFF_FOLDER_PATH-"], values["-METADATA_FOLDER_PATH-"])

    elif event == 'Plot ':
        # Plot the selected datasets and channels
        g.plot_data(data, type)

    elif event == 'Average Across All Trials':
        type = 2

        # process data
        data = tp.baseline(values["-TIFF_FOLDER_PATH-"], values["-METADATA_FOLDER_PATH-"])

        # reshape data from 3D to 2D numpy array for saving
        data = data.reshape(4, 5376)

        # save processed data
        np.savetxt(values["-GRAPH_TITLE-"] + ".csv", data, delimiter=",")

    elif event == 'Plot  ':
        # read in csv file with filename that matches graph title
        data = np.genfromtxt(values["-GRAPH_TITLE-"] + ".csv", delimiter=',')

        # Plot the selected datasets and channels
        g.plot_data(data, type, values=values)

    # plot data from single trial
    elif event == 'Choose Trials':
        type = 0

        # list of which trials to plot and subtract one from each to make it zero-based
        trials = np.array(ghelper.choose_trial()) - 1
        trials = trials.tolist()

        # process data and select the trials we want
        data = tp.single_trial(trials, values["-TIFF_FOLDER_PATH-"],
                               values["-METADATA_FOLDER_PATH-"])

        # add one back for labeling
        trials = np.array(trials) + 1
        trials = trials.tolist()

        # save processed data
        # np.savetxt(values["-GRAPH_TITLE-"] + ".csv", data, delimiter=",")

        # plot by trial
    elif event == 'Plot   ':
        g.plot_single_trial(data, trials)

    elif event == 'Record Noise Baseline':
        type = 2

        # process data
        data = tp.baseline(values["-TIFF_FOLDER_PATH-"], values["-METADATA_FOLDER_PATH-"])

        # save baseline
        data = data.reshape(4, 5376)
        np.savetxt("baseline.csv", data, delimiter=",")

    elif event == 'Subtract Noise From Dataset':
        # set type
        type = 2

        # read in csv file with baseline data
        baseline = np.genfromtxt('../baseline.csv', delimiter=',')

        # read in csv file with new data
        data = np.genfromtxt(values["-GRAPH_TITLE-"] + ".csv", delimiter=',')

        # subtract baseline from new data
        data = data - baseline

        # save noise adjusted data
        np.savetxt(values["-GRAPH_TITLE-"] + "_Noise_Adjusted.csv", data, delimiter=",")

    elif event == 'Plot    ':
        # read in csv file with filename that matches graph title
        data = np.genfromtxt(values["-GRAPH_TITLE-"] + ".csv", delimiter=',')

        # Plot the selected datasets and channels
        g.plot_data(data, type, values)

    elif event == 'Trial vs. Experiment':
        # process data
        data = tp.average_trials(values["-TIFF_FOLDER_PATH-"], values["-METADATA_FOLDER_PATH-"])

    elif event == 'Plot     ':
        # plot data
        g.plot_trial_vs_experiment(data)

    elif event == 'Standard Deviation':
        # process data
        data_average, data_std = tp.standard_deviation(values["-TIFF_FOLDER_PATH-"],
                                                       values["-METADATA_FOLDER_PATH-"])

        # plot standard deviation
    elif event == "Plot      ":
        # plot data
        g.plot_std(data_average, data_std, values=values)

    elif event == "10 Trials Per Chart":
        # process data
        data = tp.separate_trials(values["-TIFF_FOLDER_PATH-"],
                                  values["-METADATA_FOLDER_PATH-"])

        # plot and automatically save files
    elif event == 'Plot       ':
        # determine how many charts to create for the dataset (only works for multiples of 10)
        num_charts = np.size(data, axis=0) // 10

        # iterate through all trials
        for i in range(num_charts):
            # create trial index list for legend
            trials = list(range(((i * 10) + 1), ((i + 1) * 10) + 1))
            g.plot_single_trial(data[(i * 10):((i + 1) * 10)], trials, values=values)

    elif event == 'Plot By Channel':
        #g.plot_by_channel()
         data = tp.histogramFrame(values["-TIFF_FOLDER_PATH-"],
                                  values[
                                      "-METADATA_FOLDER_PATH-"])

    elif event == 'Run All':
        trial_data, data_average, std_data, baseline_data = tp.run_all(values["-TIFF_FOLDER_PATH-"],
                                                                       values[
                                                                           "-METADATA_FOLDER_PATH-"])
        # plot data
        g.plot_std(data_average, std_data, values=values)
        g.plot_data(baseline_data, values=values, type=2)

        # determine how many charts to create for the dataset (only works for multiples of 10)
        num_charts = np.size(trial_data, axis=0) // 10

        # iterate through all trials
        for i in range(num_charts):
            # create trial index list for legend
            trials = list(range(((i * 10) + 1), ((i + 1) * 10) + 1))
            g.plot_single_trial(trial_data[(i * 10):((i + 1) * 10)], trials, values=values)

    elif event == 'Photon Count':
        # process data
        data = tp.photon_count(values["-TIFF_FOLDER_PATH-"],
                          values[
                              "-METADATA_FOLDER_PATH-"])


        # plot data
        #g.plot_data(data, 2, values=values)

    elif event == 'PCA':
        # process data
        data = tp.pca(values["-TIFF_FOLDER_PATH-"],
                      values[
                          "-METADATA_FOLDER_PATH-"])

        PCA.my_pca(data[0])


    elif event == 'Close':
        plt.close('all')

# Close the PySimpleGUI window
window.close()
