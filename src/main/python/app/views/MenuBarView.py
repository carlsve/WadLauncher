from PyQt5.QtWidgets import QAction, QFileDialog, QDialog

class MenuBarView:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.import_zip_action = root.findChild(QAction, 'action_file_import_zip')
        self.import_zip_action.triggered.connect(self.file_dialog_opener)

    def file_dialog_opener(self):
        dialog = QFileDialog(self.root, 'Select zip file(s) to import')
        dialog.setFileMode(QFileDialog.ExistingFiles)
        if dialog.exec_() == QDialog.Accepted:
            for selected_file in dialog.selectedFiles():
                self.controller.select_unzip_file(selected_file)