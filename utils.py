import os
from time import sleep
from PyQt5.QtWidgets import QApplication, QProgressDialog, QMessageBox, QLabel
from PyQt5 import QtCore, QtGui
import threading


class Worker(QtCore.QObject):
    copied = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.buffer_size = 1024 * 1024
        self.is_running = False

    def copy_file(self, src_file, dst_file) -> None:
        try:
            with open(src_file, "rb") as src, open(dst_file, "wb") as dest:
                while True:
                    if not self.is_running:
                        print("TESTE NOT RUNNING!")
                        sleep(0.2)
                        os.remove(dst_file)
                        return
                    buff = src.read(self.buffer_size)
                    if not buff:
                        break
                    dest.write(buff)
                    self.copied.emit(len(buff))

            print(f"file copied from: {src_file} to {dst_file}")
        except Exception as e:
            print(e)
        self.is_running = False

    @QtCore.pyqtSlot(str, str)
    def start_copy(self, src_file, dst_file):
        self.is_running = True
        t = threading.Thread(target=self.copy_file, args=(src_file, dst_file))
        t.start()

        # loop to hold finish last thread
        while self.is_running:
            pass

        # emits finished signal
        self.finished.emit()

    @QtCore.pyqtSlot()
    def cancel_copy(self):
        self.is_running = False


def message(msg, yes_button, no_button=None):
    msg_box = QMessageBox(None)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(msg)
    msg_box.setWindowTitle("File Copier!")
    if no_button:
        msg_box.setStandardButtons(yes_button | no_button)
    else:
        msg_box.setStandardButtons(yes_button)
    print(msg)
    return msg_box.exec_() == 1024


class Copier(QProgressDialog):
    copy_request = QtCore.pyqtSignal(str, str)
    cancel_request = QtCore.pyqtSignal()

    """Class With ProgressDialog to request copy file"""

    def __init__(self, src_file, dst_file):
        super().__init__()
        print("Progress Dialog Created.")
        self.setWindowIcon(QtGui.QIcon('folder.ico'))

        # set title
        self.setWindowTitle("Copying File...")
        self.label = QLabel(parent=self)
        self.setLabel(self.label)
        self.movie = QtGui.QMovie('anim.gif')
        self.movie.setScaledSize(QtCore.QSize(100, 50))
        self.movie.setSpeed(80)
        self.label.setMovie(self.movie)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.setFixedHeight(120)
        self.setContentsMargins(11, 11, 11, 11)

        # files
        self.src_file = src_file
        self.dst_file = dst_file
        self.file_size = self.src_file.stat().st_size

        # create worker and thread attributes
        self.worker = None
        self.worker_thread = QtCore.QThread()

        # show ui
        self.show()

        # sets progressbar range
        self.setRange(0, self.file_size)

        # connect cancel button
        self.canceled.connect(self.on_cancel)

    # callbacks
    def create_worker(self):
        self.worker = Worker()
        self.worker.copied.connect(self.update_pb)
        self.worker.finished.connect(self.final_message)
        self.copy_request.connect(self.worker.start_copy)
        self.cancel_request.connect(self.worker.cancel_copy)
        # Assign the worker to the thread and start the thread
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def on_cancel(self):
        self.worker_thread.terminate()
        self.cancel_request.emit()
        self.close()

    def update_pb(self, bites):
        self.setValue(self.value() + bites)

    def start_worker(self):
        self.movie.start()
        self.create_worker()
        self.copy_request.emit(self.src_file.as_posix(), self.dst_file.as_posix())

    def final_message(self):
        print(f"File copied from {self.src_file} to {self.dst_file}")
        self.close()


# loads the interface
def load_interface(src_file, dst_file, ask_override=False):
    app = QApplication([])
    if dst_file.exists():
        if ask_override:
            ask = message("Destiny file already exists. Want to replace it?",
                          yes_button=QMessageBox.Ok,
                          no_button=QMessageBox.No)
            if not ask:
                app.quit()
                return False
        os.remove(dst_file.as_posix())
        sleep(0.2)

    d = Copier(src_file, dst_file)
    d.start_worker()
    app.exec_()
    return d
