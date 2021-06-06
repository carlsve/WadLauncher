import sys

from app.views.WelcomeView import WelcomeView

class WelcomeController:
    def __init__(self, root, models):
        self.view = WelcomeView(root)
