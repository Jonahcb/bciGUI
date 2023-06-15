import os
import numpy as np

# milliseconds per line
mspl = 1.15


def get_filename_without_extension(path):
    """
    Returns the filename given a pathname

    Parameter path: the pathname for the file
    Precondition: path must be a String
    """
    basename = os.path.basename(path)
    filename, _ = os.path.splitext(basename)
    return filename


def initialize_time_series(data_sets, type=None):
    """
    Returns the time series for all the plots

    Parameter data_sets: the data to plot
    Precondition: data_sets must at least be a 3D numpy array
    """
    # initialize time series
    time_series = []

    if type == 4:
        for i in range(data_sets[0][0].size):
            time_series.append((i * mspl) / 1000.0)
    else:
        for i in range(data_sets[0].size):
            time_series.append((i * mspl) / 1000.0)

    return np.array(time_series)


def save_file(filepath, filename, figure, subdir):
    """
    Saves figure to filepath + filename

    Parameter filepath: the path of the general folder for that day of experiments
    Precondition: filepath must be a String

    Parameter filename: the name of the specific file for that figure
    Precondition: filename must be a String
    """
    # make folder
    if not os.path.exists(filepath + subdir):
        os.makedirs(filepath + subdir)

    figure.savefig(filepath + subdir + filename,
                   format='pdf', dpi=100)
