import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import GrapherHelper as gh
import GUIHelper as ghelper
import os

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

# pathname for folder to save charts to
filepath = '/Users/jonahbernard/Desktop/SN Lab/6.10.23 graphs/2023-06-10 B_cortex_CTZ_micro_20x_spot1_FIGURES/'


def label_plot(type, axes=None, channel_num=None, files_names=None, trial_indices=None,
               values=None, std=None):
    """
    Labels the figures that are being drawn

    Parameter type: the type of processing to do to the tiff files
    Precondition: type must be an int

    Parameter axes: the subplots of the figure
    Precondition: axes must be Matplotlib subplots

    Parameter channel_num: the number of channels being plotted
    Precondition: channel_num must be an int

    Parameter files_names: the names of the files to be used for the legend
    Precondition: files_names must be a list of Strings

    Parameter trial_indices: a list of trial #s that were plotted
    Precondition: trial_indices must be a list of ints

    Parameter values: a dict of information from the GUI event handler
    Precondition: values must be a dict

    Parameter std: a boolean to indicate whether we are plotting a graph with std or not
    Precondition: std must be a boolean
    """

    if type == 1:
        # label x and y-axis for first graph only
        axes[0, 0].set_xlabel("Time (s)")
        axes[0, 0].set_ylabel("Intensity")

        # need to create legend

    # grouping by experiment
    elif type == 2:
        plt.xlabel("Seconds")
        plt.ylabel("Intensity")
        if not std:
            plt.title(values["-GRAPH_TITLE-"] + '_avg_trials')
        else:
            plt.title(values["-GRAPH_TITLE-"] + '_std')

        # create legend
        plt.legend(labels=['C1', 'C2', 'C3', 'C4'], markerscale=20.0, frameon=False,
                   bbox_to_anchor=(1.02, 1.0), loc='upper left', labelspacing=0.65, fontsize=11)

    # grouping by channel
    elif type == 3:
        plt.xlabel("Seconds")
        plt.ylabel("Intensity")
        plt.title("Channel " + str(channel_num + 1))

        # create legend
        plt.legend(labels=files_names, markerscale=20.0, frameon=False,
                   bbox_to_anchor=(0.0, -.13), loc='lower left', labelspacing=0.65, fontsize=7)

    # singular trials
    elif type == 4:
        plt.xlabel("Seconds")
        plt.ylabel("Intensity")
        plt.title(values["-GRAPH_TITLE-"] + '_trials_' + str(trial_indices[0]) + '_through_' + str(
            trial_indices[len(trial_indices) - 1]) + '_channel ' + str(channel_num + 1))

        # create legend
        plt.legend(labels=trial_indices, markerscale=20.0, frameon=False,
                   bbox_to_anchor=(1.02, 1.0), loc='upper left', labelspacing=0.65, fontsize=7)

    # for std by channel
    elif type == 5:
        axes[0][0].set_xlabel("Seconds")
        axes[0][0].set_ylabel("Intensity")
        axes[0][1].set_xlabel("Seconds")
        axes[1][0].set_xlabel("Seconds")
        axes[1][1].set_xlabel("Seconds")
        axes[1][0].set_ylabel("Intensity")
        plt.suptitle(values["-GRAPH_TITLE-"] + '_std_by_channel')


def plot_by_channel():
    """
    Plots the selected data sets by grouping corresponding channels on same figure
    """
    # import gui file for use
    import DataGUI as dg

    # select data sets
    data_sets = ghelper.choose_datasets()

    # initialize list to hold numpy array datasets
    data_list = []

    # initialize list to hold filenames
    file_names = []

    # initialize time series
    time_series = gh.initialize_time_series(data_sets)

    # read in datasets to numpy arrays
    for pathName in data_sets:
        # slice file name out of pathname and append to filename list
        file_names.append(gh.get_filename_without_extension(pathName))
        data = np.genfromtxt(pathName, delimiter=',')
        data_list.append(data)

    # iterate through each dataset for each channel (4x4 iterations)

    for channel in range(num_channels):
        plt.figure()

        for i, data in enumerate(data_list):
            # plot data
            plt.scatter(time_series, data[channel], label=channel, s=0.1,
                        color=channel_color[i])

        # create legend
        label_plot(type=3, channel_num=channel, files_names=file_names)

    plt.show(block=False)


def plot_data(selected_sets, type, values=None):
    """
    Plots the selected data sets

    Parameter selected_sets: the data to plot
    Precondition: selected_sets must be at least 2D numpy array

    Parameter type: the type of processing to do to the tiff files
    Precondition: type must be an int

    Parameter values: a dict of information from the GUI event handler
    Precondition: values must be a dict
    """
    # initialize time series
    time_series = gh.initialize_time_series(selected_sets)

    # change figsize based on what size you want to save as (width X height)
    plt.figure(figsize=(30, 19.5))

    if type == 1:

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
                    axe.scatter(time_series, selected_sets[i * 2 + j][c], label=c, s=0.1,
                                color=channel_color[c])
                # increment label counter
                counter += 30

        # label plots
        label_plot(type, axes)

        fig.tight_layout(pad=5.0)
        plt.show(block=False)

    elif type == 2:
        # plot each channel on subplot
        for c in range(num_channels):
            plt.scatter(time_series, selected_sets[c], label=c, s=0.1,
                        color=channel_color[c])

        # label plots
        label_plot(type, values=values)

        # assign most recent figure to 'figure'
        figure = plt.gcf()

        # determine filename and add specific folder path for that type of chart
        file_name = values["-GRAPH_TITLE-"] + '_avg_trials' + '_FIGURE.pdf'

        # specific folder name
        subdir = 'experiment/'

        # save file
        gh.save_file(filepath=filepath, filename=file_name, figure=figure, subdir=subdir)

        plt.show(block=False)


def plot_single_trial(selected_sets, trials, values):
    """
    Function that plots single selected trials on same chart

    Parameter selected_sets: the datasets to be plotted
    Precondition: selected_sets must be a list of numpy arrays

    Parameter values: a dict of information from the GUI event handler
    Precondition: values must be a dict

    Parameter trials: a list of trial #s that were plotted
    Precondition: trials must be a list of ints
    """

    # assign analysis type
    type = 4

    # initialize time series
    time_series = gh.initialize_time_series(selected_sets, type)

    # convert trial_indices elements from String to int
    trials = [int(i) for i in trials]

    # iterate over one channel for all trials then repeat

    # plot each channel on graph
    for c in range(num_channels):

        # change figsize based on what size you want to save as (width X height)
        plt.figure(figsize=(30, 19.5))

        # plot each trial on graph by iterating through dataset and list of colors to graph with
        for trial, color in zip(selected_sets, mcolors.TABLEAU_COLORS):
            # reshape array to plot as line graph
            print(trial.shape)
            #trial = trial.reshape(4, 5376)

            plt.plot(time_series, trial[c], label=c,
                     color=color)

        # label plots
        label_plot(type, trial_indices=trials, channel_num=c, values=values)

        figure = plt.gcf()

        # determine filename
        file_name = values["-GRAPH_TITLE-"] + '_trials_' + str(
            trials[0]) + '_through_' + str(
            trials[len(trials) - 1]) + '_channel ' + str(c + 1) + '_FIGURE.pdf'

        # specific folder name
        subdir = 'trials/'

        # save file
        gh.save_file(filepath=filepath, filename=file_name, figure=figure, subdir=subdir)

    plt.show(block=False)


def plot_std(average_data, std_data, values):
    """
    Function that plots average of trials with standard deviation bars

    Parameter average_data: the dataset of average values to be plotted
    Precondition: average_data must be a numpy array

    Parameter std_data: the dataset of standard deviation values to be plotted
    Precondition: std_data must be a numpy array

    Parameter values: a dict of information from the GUI event handler
    Precondition: values must be a dict
    """
    # switch for plotting channels separate and together
    separate_by_channel = False

    # initialize time series
    time_series = gh.initialize_time_series(average_data)

    # flatten y and y-err
    average_data = average_data.reshape(4, 5376)
    std_data = std_data.reshape(4, 5376)

    # change figsize based on what size you want to save as (width X height)
    plt.figure(figsize=(30, 19.5))

    # create figure to hold 4 subplots
    fig, axes = plt.subplots(2, 2, sharey=True)

    # change dimensions of figure
    fig.set_figwidth(25)
    fig.set_figheight(8.8)

    # initialize label for channel #
    c = 0

    # iterate through numpy array of subplots
    for i, axis in enumerate(axes):
        # create subplots by using number of subplot as orientation index
        for j, axe in enumerate(axis):
            # create label
            label = "Channel " + str(c + 1)
            axe.set_title(label)
            # plot each channel on subplot
            axe.errorbar(time_series, average_data[c], yerr=std_data[c],
                         color=channel_color[c], ecolor="black", elinewidth=0.1, linewidth=0.3)
            c = c + 1

            label_plot(type=5, axes=axes, values=values)
            fig.tight_layout(pad=5.0)

    # determine filename
    file_name = 'std/' + values["-GRAPH_TITLE-"] + '_std_by_channel' + '_FIGURE.pdf'

    # assign most recent figure to 'figure'
    figure = plt.gcf()

    # save file
    gh.save_file(filepath=filepath, filename=file_name, figure=figure)

    # show figure
    plt.show(block=False)

    # create new figure
    plt.figure(figsize=(30, 19.5))

    # plot each channel on subplot
    for c in range(num_channels):
        plt.errorbar(time_series, average_data[c], yerr=std_data[c],
                     color=channel_color[c], ecolor="black", elinewidth=0.1, linewidth=0.3)

    # determine filename
    file_name = values["-GRAPH_TITLE-"] + '_std' + '_FIGURE.pdf'

    # specific folder name
    subdir = 'std/'

    # label plots
    label_plot(type=2, values=values, std=True)

    # assign most recent figure to 'figure'
    figure = plt.gcf()

    # save file
    gh.save_file(filepath=filepath, filename=file_name, figure=figure, subdir=subdir)

    plt.show(block=False)

