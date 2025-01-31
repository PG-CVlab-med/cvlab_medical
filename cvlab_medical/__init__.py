from glob import glob

from cvlab.diagram.elements import add_plugin_callback
from cvlab_medical.med_visualisation_utils.med_visualisation_classes import *
from cvlab_samples import OpenExampleAction, get_menu
from .med_image_io import *
from .med_visualisation import *
from .med_visualisation_utils.windows_manager_extend import extend_windows_manager

# extending windows manager class to support visualisation
extend_windows_manager()


def add_samples_callback(main_window, menu_title, samples_directory):
    samples = glob(samples_directory + "/*.cvlab")
    samples.sort()

    print("Adding {} sample diagrams to {} menu".format(len(samples), menu_title))

    menu = get_menu(main_window, 'Examples/' + menu_title)

    for sample in samples:
        menu.addAction(OpenExampleAction(main_window, sample))


def add_samples(menu_title, samples_directory):
    callback = lambda main_window: add_samples_callback(main_window, menu_title, samples_directory)
    add_plugin_callback(callback)
