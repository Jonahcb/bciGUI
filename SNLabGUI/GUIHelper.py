import PySimpleGUI as sg


def choose_datasets():
    """
    Returns the datasets to plot when plotting by channel
    """
    layout_choose_datasets = [[sg.Text("csv file 1:")],
                              [sg.Input(key="-1_FOLDER_PATH-"), sg.FileBrowse()],
                              [sg.Text("csv file 2:")],
                              [sg.Input(key="-2_FOLDER_PATH-"), sg.FileBrowse()],
                              [sg.Text("csv file 3:")],
                              [sg.Input(key="-3_FOLDER_PATH-"), sg.FileBrowse()],
                              [sg.Text("csv file 4:")],
                              [sg.Input(key="-4_FOLDER_PATH-"), sg.FileBrowse()],
                              [sg.Button('Finish', size=(10, 1))]]

    window_choose_datasets = sg.Window("Select datasets", layout_choose_datasets, modal=True)

    while True:
        event_choose_datasets, values_choose_datasets = window_choose_datasets.read()
        if event_choose_datasets == "Exit" or event_choose_datasets == sg.WIN_CLOSED:
            break
        # returns a list with indexes of trials to plot
        elif event_choose_datasets == "Finish":
            dataset_list = []
            for value in values_choose_datasets.values():
                # filter out empty values when the user does not provide all 4 file names
                if not value == "":
                    dataset_list.append(value)

            # remove duplicates before returning
            return list(set(dataset_list))  # has 2 of every value for some reason

    window_choose_datasets.close()


def choose_trial():
    """
    Creates window that allows the user to select which trial(s) to plot
    """
    layout = [[sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(1, 10)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(10, 20)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(20, 30)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(30, 40)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(40, 50)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(50, 60)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(60, 70)],
              [sg.Checkbox(f'{i}. ', key=f'{i}') for i in range(70, 79)],
              [sg.Button('Select', size=(10, 1))]]

    window = sg.Window("Select Trial", layout, modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # returns a list with indexes of trials to plot
        elif event == "Select":
            trial_list = []
            for key in values:
                if values[key] is True:
                    trial_list.append(int(key))
            break
    return trial_list

    window.close()
