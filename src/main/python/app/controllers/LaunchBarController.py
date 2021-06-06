import sys

from app.views.LaunchBarView import LaunchBarView
from app.utils import Launcher

class LaunchBarController:
    def __init__(self):
        pass

    def show(self, root, models):
        self.models = models
        self.selected_iwad = None
        self.selected_source_port = None
        self.view = LaunchBarView(root, self)

        models.wads.subscribe(self.subscription)
        models.iwads.subscribe(self.subscription)
        models.source_ports.subscribe(self.subscription)

    def subscription(self, message):
        action, data = message

        if action == self.models.wads.SELECTED:
            self.view.update_selected_wad(data)
        elif action == self.models.iwads.LOADED:
            self.view.append_iwad(data)
        elif action == self.models.iwads.LOADED_ALL:
            pass
        elif action == self.models.source_ports.LOADED:
            self.view.append_source_port(data)
        elif action == self.models.source_ports.LOADED_ALL:
            pass

    def select_iwad(self, id):
        self.selected_iwad = self.models.iwads.find(id)

    def select_source_port(self, id):
        self.selected_source_port = self.models.source_ports.find(id)

    def launch_wad_press(self):
        if self.selected_iwad and self.selected_source_port:
            Launcher.launch(
                self.models.wads.load_ordered_files,
                self.selected_iwad,
                self.selected_source_port
            )
