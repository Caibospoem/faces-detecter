import sys
import cv2
import os
import threading
from PIL import Image
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap, QImage
from qframelesswindow import FramelessWindow
from PyQt5.QtWidgets import QApplication, QWidget
from mainwindow import Main_Window
from window_1 import Window_1
from delete_window import Delete_window
from face import upload_users, detect_user

class Login(FramelessWindow, Main_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Button3.clicked.connect(self.showWindow2)
        self.Button2.clicked.connect(self.showWindow1)

        self.Button1.clicked.connect(self.on_button1_click)
        self.Button4.clicked.connect(self.on_button2_click)
        self.stop_detection = threading.Event()
        # self.camera = cv2.VideoCapture(0)
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_frame)

    def on_button1_click(self):
        self.stop_detection.clear()
        self.detect_user_and_display()

    def on_button2_click(self):
        upload_users()

    def stopCamera(self):
        self.stop_detection.set()
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None

    def detect_user_and_display(self):
        def run_detection():
            self.cap = cv2.VideoCapture(0)
            for frame in detect_user():
                if self.stop_detection.is_set():
                    break
                self.update_label(frame)

        threading.Thread(target=run_detection).start()

    def update_label(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.Image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.stop_detection.set()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    def showWindow1(self):

        w_1 = window_1()
        w_1.show()

    def showWindow2(self):

        w_2 = delete_window()
        w_2.show()

class window_1(FramelessWindow, Window_1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_4.clicked.connect(self.Close)
        self.pushButton_2.clicked.connect(self.start_camera)
        self.pushButton_1.clicked.connect(self.take_photo)
        self.pushButton_3.clicked.connect(self.change_name)

        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)


    def Close(self):
        self.close()
    def Open(self): 
        self.show()

    def change_name(self):

        test_1 = self.lineEdit_1.text()
        test_2 = self.lineEdit_2.text()

        # 指定要修改文件名称的目录路径
        directory = './users/'
        # 指定要修改的文件名
        old_filename = 'photo.jpg'
        # 指定新的文件名
        new_filename = test_1+'_'+test_2+'.jpg'
        # 获取原始文件路径
        original_path = os.path.join(directory, old_filename)
        # 获取新的文件路径
        new_path = os.path.join(directory, new_filename)
        # 重命名文件
        os.rename(original_path, new_path)
        self.label_1.setText("录入成功！")

    def start_camera(self):
        self.timer.start(20)  # 以大约50fps的速度更新画面

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(image)
            self.Image_label.setPixmap(pix)

    def take_photo(self):
        ret, frame = self.camera.read()
        if ret:
            photo_path = './users/photo.jpg'
            cv2.imwrite(photo_path, frame)
            print(f'Photo saved to {photo_path}')
        self.label_1.setText("拍照成功！")

    def closeEvent(self, event):
        self.timer.stop()
        self.camera.release()
        super().closeEvent(event)


class delete_window(FramelessWindow, Delete_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_3.clicked.connect(self.delete)
        self.pushButton_4.clicked.connect(self.close)

    def Close(self):
        self.close()
    def Open(self):
        self.show()

    def delete(self):
        test_1 = self.lineEdit_1.text()
        test_2 = self.lineEdit_2.text()
        # 指定要删除文件所在的目录路径
        directory = './users/'
        # 指定要删除的文件名
        filename = test_1+'_'+test_2+'.jpg'

        # 获取文件路径
        file_path = os.path.join(directory, filename)

        # 检查文件是否存在
        if os.path.exists(file_path):
            # 删除文件
            os.remove(file_path)
            self.label_1.setText("成功删除"+test_2)
        else:
            self.label_1.setText("用户不存在")

if __name__ == "__main__":

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    m = Login()
    w_1 = window_1()
    w_2 = delete_window()

    m.show()

    app.exec_()