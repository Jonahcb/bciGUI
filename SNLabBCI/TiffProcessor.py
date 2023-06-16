import os
import numpy as np
from PIL import Image
import MetadataReader as mr
import matplotlib.pyplot as plt

# constants
pixelps = 3.4 / 65536.0

# frames per second
fps = 3.4

# seconds per frame
spf = 0.294

# milliseconds per line
mspl = 1.15


def filter_channel(tif):
    """
    Returns: 4D numpy array with an element for each channel

    Parameter tif: the data to separate into channels
    Precondition: tif must be 3D nested numpy array
    """
    # separate channels
    CH1 = tif[::4]
    CH2 = tif[1::4]
    CH3 = tif[2::4]
    CH4 = tif[3::4]

    return np.array([CH1, CH2, CH3, CH4])


def average_line(data):
    """
    Returns: 3D numpy array averaged across each line

    Parameter data: the data to average across each line
    Precondition: data must be 4D nested numpy array
    """
    return np.mean(data, axis=-1)


def average_trials(files, metadata_dir):
    """
    Returns: 4D numpy array averaged across each trial that has the same orientation

    Parameter data: the data to average across each orientation
    Precondition: files must be 4D nested numpy array

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """

    # list of lists grouped by angle: [file #, angle]
    meta_data, temp = mr.read_metadata(metadata_dir)

    # determine where to split array by cumulating orientations
    temp = np.array(temp).cumsum()

    # get rid of last element to split
    sum_orientations = temp[:-1]
    print(sum_orientations)
    # reorder array so it is grouped by angle
    print(meta_data)
    arr_reordered = np.take(files, meta_data, axis=0)

    # split by orientation
    arr_reordered = np.split(arr_reordered, sum_orientations)

    temp = []
    for array in arr_reordered:
        temp.append(np.mean(array, axis=0))
    avgResult = np.array(temp)

    # return averaged numpy array
    return avgResult


def average_all_orientations(trials):
    """
    Averages the data across all trials regardless of orientation.

    Returns: 3D numpy array that is averaged across trials

    Parameter trials: a 4D numpy array with trials in axis 0.
    Precondition: must be a numpy array
    """
    return np.mean(trials, axis=0)


def tif_processor_run(tiff_dir, metadata_dir):
    """
    Stores pixel values from a directory of tiff file into a numpy array.

    Returns: 4D numpy array with pixel values separated into channels

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # initialize array to hold raw data from each frame
    processed_tiffs = []
    # loop through every tif file in folder
    for tiff in os.listdir(tiff_dir):
        # make sure it is a tif file
        if ('.tif' in tiff):
            # open tif file using PIL Image
            with Image.open(tiff_dir + '/' + tiff) as img:
                # initialize list to hold frames
                frames = []
                # loop through every frame
                for i in range(img.n_frames):
                    # go to right frame
                    img.seek(i)
                    # make frame data into array of floats
                    frame = np.array(img).astype(float)

                    # correct for zig-zag recording pattern by flipping every other line
                    frame[1::2, :] = frame[1::2, ::-1]

                    # append frame data array to frames list
                    frames.append(frame)

                # append frames array to processed tif files list
                processed_tiffs.append(np.array(frames))

    np.array(processed_tiffs)

    temp = []
    for tif in processed_tiffs:
        # for each tif: separate into 4 channels
        temp.append(filter_channel(tif))

    x = np.array(temp)

    # normalize over each channel
    x_min, x_max = x.min(axis=1, keepdims=True), x.max(axis=1, keepdims=True)

    normalized_data = (x - x_min) / (x_max - x_min)

    return normalized_data


def average(tiff_dir, metadata_dir):
    """
    Returns: 4D numpy array with intensity data averaged within orientations

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """

    # process tiffs and separate them into 4 channels
    tiff_by_channel = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(tiff_by_channel)

    # averages within orientations
    averages = average_trials(averaged_by_line, metadata_dir)

    return averages


def baseline(tiff_dir, metadata_dir):
    """
    Returns: 3D numpy array with intensity data averaged across all orientations

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # process tiffs and separate them into 4 channels
    tiff_by_channel = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(tiff_by_channel)

    # averages across all trials
    averages = average_all_orientations(averaged_by_line)

    return averages


def single_trial(trials, tiff_dir, metadata_dir):
    """
    Returns: 4D numpy array with selected trials

    Parameter trials: the trial indices to plot
    Precondition: files must be 4D nested numpy array

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """

    # process tiffs and separate them into 4 channels
    all_trials = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(all_trials)

    # select trials we need from list of indices
    selected_trials = np.take(averaged_by_line, trials, axis=0)

    return selected_trials


def trial_against_experiment(tiff_dir, metadata_dir):
    """
    Returns: 3D numpy array containing the average value of each trial

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # processes tiffs and separates them into 4 channels
    tiff_by_channel = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(tiff_by_channel)

    # flatten each channel (new shape should be (# trials, # channels, # data points))
    tiff_by_channel = averaged_by_line.reshape(np.size(tiff_by_channel, 0), 4, 5376)

    # average each trial for each channel
    average = np.mean(tiff_by_channel, axis=2)

    return average


def standard_deviation(tiff_dir, metadata_dir):
    """
    Returns: 3D numpy array with standard deviation of all trials

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """

    # processes tiffs and separates them into 4 channels
    tiff_by_channel = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(tiff_by_channel)

    # averages across all trials
    average_across_trials = average_all_orientations(averaged_by_line)

    # calculate standard deviation of each line
    std_across_trials = np.std(averaged_by_line, axis=0)

    # return average, std arrays
    return average_across_trials, std_across_trials


def separate_trials(tiff_dir, metadata_dir):
    """
    Returns: 3D numpy array containing the average value of each trial for plotting all
    the trials separately

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # processes tiffs and separates them into 4 channels
    tiff_by_channel = tif_processor_run(tiff_dir, metadata_dir)

    # average across each line
    averaged_by_line = average_line(tiff_by_channel)

    # return the data separated into trials
    return averaged_by_line


def run_all(tiff_dir, metadata_dir):
    """
    Returns: Four 3D numpy arrays containing data to plot separate trials, standard deviations, and
    experiment averages

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # process and unpack std data
    data_avg, std_data = standard_deviation(tiff_dir, metadata_dir)

    # trial-by-trial, std, baseline
    return separate_trials(tiff_dir, metadata_dir), data_avg, std_data, baseline(tiff_dir,
                                                                                 metadata_dir)


def photon_count(tiff_dir, metadata_dir):
    """
    Returns: 2D numpy array that is filtered for only above threshold events and smoothed to ~100ms

    Parameter tiff_dir: filepath name for folder with tiff files
    Precondition: tiff_dir must be a String

    Parameter metadata_dir: filepath name for folder with metadata
    Precondition: metadata_dir must be a String
    """
    # process data
    data = tif_processor_run(tiff_dir, metadata_dir)

    # reshape array to calculate mean of each channel
    new_data = data.reshape(np.size(data, axis=0), np.size(data, axis=1),
                            np.size(data, axis=2) * np.size(data, axis=3) * np.size(data, axis=4))

    # calculate mean and standard deviation of each channel
    mean = np.mean(new_data, axis=2)
    std = np.std(new_data, axis=2)

    # calculate threshold (3.8 std right now)
    threshold = mean + 3.8 * std

    # only keep data above the threshold
    data = np.where(data > threshold[0][0], data, 0)

    # count the number of points above the threshold for each line
    data = np.count_nonzero(data, axis=4)

    # reshape
    data = data.reshape(np.size(data, axis=0), np.size(data, axis=1),
                        np.size(data, axis=2) * np.size(data, axis=3))

    # initialize list to hold processed data
    avg = []

    # iterate through each trial and calculate the moving avg for each channel
    for trial in data:
        # calculate moving average
        CH1 = moving_average(trial[0], 100)
        CH2 = moving_average(trial[1], 100)
        CH3 = moving_average(trial[2], 100)
        CH4 = moving_average(trial[3], 100)
        avg.append(np.array([CH1, CH2, CH3, CH4]))

    return np.array(avg)


def moving_average(x, w):
    """
    Returns: a numpy array that is calculated using the moving average

    Parameter x: the numpy array of data to calculate the moving average from
    Precondition: x must be a numpy array of ints, floats, or doubles

    Parameter w: the window size to smooth across
    Precondition: w must be an int
    """
    return np.convolve(x, np.ones(w), 'valid') / w


def pca(tiff_dir, metadata_dir):
    # process data
    data = tif_processor_run(tiff_dir, metadata_dir)

    # reshape
    data = data.reshape(np.size(data, axis=0), np.size(data, axis=1),
                        np.size(data, axis=2) * np.size(data, axis=3) * np.size(data, axis=4))

    return data


def histogramFrame(tiff_dir, metadata_dir):
    # process data
    data = tif_processor_run(tiff_dir, metadata_dir)

    plt.hist(data[0][0][0])

    plt.show()
