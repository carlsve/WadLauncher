from PyQt5 import QtWidgets

from core.utils.strings import str_filesize

from app.views.widgets.IdgamesResponseWidget import *

class IdgamesDetailView():
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        root.findChild(QtWidgets.QStackedWidget, 'main_stack').currentChanged.connect(self.controller.get_data)
        
        self.mirror_button_group = QtWidgets.QButtonGroup()
        button_layout = self.root.findChild(QtWidgets.QVBoxLayout, 'idgames_detail_download_layout')
        radio_button_labels = ['Germany','Idaho','Greece','Greece (HTTP)','Texas','Germany (TLS)','New York','Virginia']
        for i, label in enumerate(radio_button_labels):
            radio_button = QtWidgets.QRadioButton(label)
            radio_button.setObjectName(label.upper())
            radio_button.setChecked(i == 0)
            button_layout.insertWidget(1 + i, radio_button)
            self.mirror_button_group.addButton(radio_button)

        data_labels = ['title', 'filename', 'size', 'date', 'author', 'description', 'credits', 'base', 'buildtime', 'editors', 'bugs','rating']
        self.idgames_response_widget = IdgamesResponseWidget(root, data_labels, 'idgames_detail', self.download, data_labels)

    def set_data(self, item):
        self.idgames_response_widget.set_data(item)
        self.textfile = self.root.findChild(QtWidgets.QPlainTextEdit, 'idgames_detail_textfile')

        if item.get('textfile'):
            self.textfile.setPlainText(item['textfile'])
            self.textfile.show()
        else:
            self.textfile.hide()


    def download(self, id, download_progress_handler, download_finished_handler):
        mirror = self.mirror_button_group.checkedButton().objectName()
        self.controller.download(mirror, download_progress_handler, download_finished_handler)
