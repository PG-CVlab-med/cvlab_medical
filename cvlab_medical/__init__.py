from glob import glob

from PyQt5.QtWidgets import QMenu

from cvlab_samples import OpenExampleAction
from cvlab.diagram.elements import add_plugin_callback


def get_submenu(menu, title):
    titles = title.split("/")

    for title in titles:
        for child in menu.findChildren(QMenu):
            if child.title() == title:
                menu = child
                break
        else:
            menu = menu.addMenu(title)

    return menu


def add_samples_callback(main_window, menu_title, samples_directory):
    samples = glob(samples_directory + "/*.cvlab")
    samples.sort()

    print("Adding {} sample diagrams to {} menu".format(len(samples), menu_title))

    main_menu = main_window.menuBar()
    menu = get_submenu(main_menu, 'E&xamples/' + menu_title)

    for sample in samples:
        menu.addAction(OpenExampleAction(main_window, sample))


def add_samples(menu_title, samples_directory):
    callback = lambda main_window: add_samples_callback(main_window, menu_title, samples_directory)
    add_plugin_callback(callback)

