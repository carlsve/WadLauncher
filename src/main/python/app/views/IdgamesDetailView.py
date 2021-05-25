from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QPlainTextEdit, QButtonGroup, QRadioButton

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget, WidgetIndices
from app.views.widgets.IdgamesResponseWidget import IdgamesResponseWidget

template_path = AppContext.Instance().get_resource('template/idgames_detail.ui')
Form, Base = uic.loadUiType(template_path)

class IdgamesDetailView(Base, Form):
    def __init__(self, root, controller, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        add_widget(root, self, 'IDGAMES_DETAIL')

        self.controller = controller

        self.mirror_button_group = QButtonGroup()
        self.button_layout = self.findChild(QVBoxLayout, 'idgames_detail_download_layout')
        radio_button_labels = ['Germany','Idaho','Greece','Greece (HTTP)','Texas','Germany (TLS)','New York','Virginia']
        for i, label in enumerate(radio_button_labels):
            radio_button = QRadioButton(label)
            radio_button.setObjectName(label.upper())
            radio_button.setChecked(i == 0)
            self.button_layout.insertWidget(1 + i, radio_button)
            self.mirror_button_group.addButton(radio_button)

        data_labels = ['title', 'filename', 'size', 'date', 'author', 'description', 'credits', 'base', 'buildtime', 'editors', 'bugs','rating']
        self.idgames_response_widget = IdgamesResponseWidget(self, data_labels, 'idgames_detail', self.download, data_labels)

    def set_data(self, item, already_downloaded, detail_type):
        self.detail_type = detail_type
        self.idgames_response_widget.set_data(item, already_downloaded)
        self.textfile = self.findChild(QPlainTextEdit, 'idgames_detail_textfile')

        if item.get('textfile'):
            self.textfile.setPlainText(item['textfile'])
            self.textfile.show()
        else:
            self.textfile.hide()

    def download(self, id):
        mirror = self.mirror_button_group.checkedButton().objectName()
        self.controller.download(id, mirror, self.detail_type)
