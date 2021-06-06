import sys

from app.views.WelcomeView import WelcomeView

class WelcomeController:
    def show(self, root, models):
        self.view = WelcomeView(root)
