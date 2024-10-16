import sys
import os
import pyperclip
from PyQt5 import QtWidgets, QtGui, QtCore
from openai import OpenAI
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# Install required packages: PyQt5, pyperclip

# Default OpenAI API Key (you can replace this with your actual key)
DEFAULT_OPENAI_API_KEY = "your-default-openai-api-key"

class ModernApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window properties
        self.setWindowTitle("Windows 11 Styled OpenAI Uploader")
        self.setWindowIcon(QtGui.QIcon('logo.ico'))  # Use .ico format for taskbar icon
        self.setGeometry(300, 100, 600, 450)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            QLabel {
                font-size: 14px;
                padding: 5px;
            }
        """)

        self.selected_paths = []

        # OpenAI API Key field
        self.api_key_label = QtWidgets.QLabel("OpenAI API Key:", self)
        self.api_key_label.setGeometry(20, 20, 150, 40)
        self.api_key_input = QtWidgets.QLineEdit(self)
        self.api_key_input.setGeometry(170, 20, 400, 40)
        self.api_key_input.setText(DEFAULT_OPENAI_API_KEY)

        # Custom Vector Store ID field
        self.vector_store_label = QtWidgets.QLabel("Custom Vector Store ID (Optional):", self)
        self.vector_store_label.setGeometry(20, 70, 200, 40)
        self.vector_store_input = QtWidgets.QLineEdit(self)
        self.vector_store_input.setGeometry(220, 70, 350, 40)

        # File and folder selection button
        self.file_folder_btn = QtWidgets.QPushButton("Select Files/Folders", self)
        self.file_folder_btn.setGeometry(20, 120, 150, 40)
        self.file_folder_btn.clicked.connect(self.open_file_folder_dialog)

        # Display selected files/folders
        self.selected_paths_display = QtWidgets.QLabel("No files or folders selected", self)
        self.selected_paths_display.setGeometry(20, 170, 550, 60)
        self.selected_paths_display.setWordWrap(True)

        # Upload button
        self.upload_btn = QtWidgets.QPushButton("Upload Files", self)
        self.upload_btn.setGeometry(200, 120, 150, 40)
        self.upload_btn.clicked.connect(self.upload_files)

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(20, 240, 550, 30)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Vector Store ID display and Copy button
        self.vector_store_id_display = QtWidgets.QLabel("Vector Store ID: Not available", self)
        self.vector_store_id_display.setGeometry(20, 300, 450, 40)
        self.copy_btn = QtWidgets.QPushButton("Copy", self)
        self.copy_btn.setGeometry(470, 300, 80, 40)
        self.copy_btn.setVisible(False)
        self.copy_btn.clicked.connect(self.copy_vector_store_id)

    def open_file_folder_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)")
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        self.selected_paths = list(files)
        if folder:
            self.selected_paths.append(folder)

        if self.selected_paths:
            display_paths = "\n".join([path if len(path) <= 80 else path[:40] + '...' + path[-20:] for path in self.selected_paths])
            self.selected_paths_display.setText(f"Selected Files/Folders:\n{display_paths}")
        else:
            self.selected_paths_display.setText("No files or folders selected")

    def upload_files(self):
        if not self.selected_paths:
            QMessageBox.warning(self, "Error", "Please select files or folders first.")
            return
        
        openai_key = self.api_key_input.text().strip()
        custom_vector_store_id = self.vector_store_input.text().strip() or None

        if not openai_key:
            QMessageBox.warning(self, "Error", "Please enter the OpenAI API key.")
            return
        
        self.upload_process(openai_key, custom_vector_store_id)

    def upload_process(self, openai_key, custom_vector_store_id=None):
        client = OpenAI(api_key=openai_key)
        file_ids = []
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        files = []
        for path in self.selected_paths:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    files.extend([os.path.join(root, f) for f in filenames])

        self.progress_bar.setMaximum(len(files))

        try:
            for index, file_path in enumerate(files):
                file_id = self.upload_file_to_openai(client, file_path)
                file_ids.append(file_id)
                self.progress_bar.setValue(index + 1)
                QtCore.QCoreApplication.processEvents()

            if custom_vector_store_id:
                vector_store_id = custom_vector_store_id
            else:
                vector_store_id = self.create_vector_store(client)

            self.attach_files_to_vector_store(client, vector_store_id, file_ids)
            self.vector_store_id_display.setText(f"Vector Store ID: {vector_store_id}")
            self.copy_btn.setVisible(True)
            QMessageBox.information(self, "Success", "Files uploaded and attached to vector store successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            self.progress_bar.setVisible(False)

    def upload_file_to_openai(self, client, file_path):
        with open(file_path, "rb") as f:
            response = client.files.create(file=f, purpose="assistants")
        return response.id

    def create_vector_store(self, client):
        vector_store = client.beta.vector_stores.create(name="Support FAQ")
        return vector_store.id

    def attach_files_to_vector_store(self, client, vector_store_id, file_ids):
        client.beta.vector_stores.file_batches.create(vector_store_id=vector_store_id, file_ids=file_ids)

    def copy_vector_store_id(self):
        pyperclip.copy(self.vector_store_id_display.text().replace("Vector Store ID: ", ""))
        QMessageBox.information(self, "Copied", "Vector Store ID copied to clipboard!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Set the taskbar icon globally for the application
    app.setWindowIcon(QtGui.QIcon('logo.ico'))  # Use .ico format for taskbar icon

    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
