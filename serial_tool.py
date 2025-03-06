# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QTextEdit, QFileSystemModel, QTreeView)
from PyQt5.QtCore import Qt, QDir, QThread, pyqtSignal
import serial
import serial.tools.list_ports
import time

# 启用高DPI缩放
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class SerialToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial1 = None
        self.serial2 = None
        self.monitor1 = None
        self.monitor2 = None

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('串口调试工具')
        self.setFixedSize(1024, 768)  # 设置固定窗口大小为1024x768

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距

        # 创建上部三个区域的容器
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setSpacing(10)  # 设置间距

        # 区域1：文件显示区
        file_group = QWidget()
        file_layout = QVBoxLayout(file_group)
        file_label = QLabel('文件显示区')
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_tree)
        file_group.setFixedWidth(250)  # 设置固定宽度

        # 创建串口控制区域的容器
        serial_container = QWidget()
        serial_container_layout = QHBoxLayout(serial_container)
        serial_container_layout.setSpacing(10)  # 设置间距

        # 串口1区域
        serial1_group = QWidget()
        serial1_layout = QVBoxLayout(serial1_group)
        serial1_layout.setSpacing(5)  # 设置间距

        # 串口1控制区
        serial1_control = QWidget()
        serial1_control_layout = QVBoxLayout(serial1_control)
        serial1_control_layout.setSpacing(5)  # 设置间距

        # 串口1标题
        serial1_title = QLabel('串口控制区1')
        serial1_control_layout.addWidget(serial1_title)

        # 串口1选择和波特率
        port1_widget = QWidget()
        port1_layout = QVBoxLayout(port1_widget)
        port1_layout.setSpacing(5)

        # 串口选择
        port1_select = QWidget()
        port1_select_layout = QHBoxLayout(port1_select)
        port1_select_layout.setContentsMargins(0, 0, 0, 0)
        port1_label = QLabel('串口号：')
        self.port1_combo = QComboBox()
        port1_select_layout.addWidget(port1_label)
        port1_select_layout.addWidget(self.port1_combo)

        # 波特率选择
        baud1_select = QWidget()
        baud1_select_layout = QHBoxLayout(baud1_select)
        baud1_select_layout.setContentsMargins(0, 0, 0, 0)
        baud1_label = QLabel('波特率：')
        self.baud1_combo = QComboBox()
        self.baud1_combo.addItems(['9600'])
        baud1_select_layout.addWidget(baud1_label)
        baud1_select_layout.addWidget(self.baud1_combo)

        port1_layout.addWidget(port1_select)
        port1_layout.addWidget(baud1_select)

        # 打开串口按钮
        self.open1_button = QPushButton('打开串口')

        serial1_control_layout.addWidget(port1_widget)
        serial1_control_layout.addWidget(self.open1_button)
        serial1_control_layout.addStretch()

        # 串口1输出区
        self.serial1_output = QTextEdit()
        self.serial1_output.setReadOnly(True)

        serial1_layout.addWidget(serial1_control)
        serial1_layout.addWidget(self.serial1_output)

        # 串口2区域
        serial2_group = QWidget()
        serial2_layout = QVBoxLayout(serial2_group)
        serial2_layout.setSpacing(5)  # 设置间距

        # 串口2控制区
        serial2_control = QWidget()
        serial2_control_layout = QVBoxLayout(serial2_control)
        serial2_control_layout.setSpacing(5)  # 设置间距

        # 串口2标题
        serial2_title = QLabel('串口控制区2')
        serial2_control_layout.addWidget(serial2_title)

        # 串口2选择和波特率
        port2_widget = QWidget()
        port2_layout = QVBoxLayout(port2_widget)
        port2_layout.setSpacing(5)

        # 串口选择
        port2_select = QWidget()
        port2_select_layout = QHBoxLayout(port2_select)
        port2_select_layout.setContentsMargins(0, 0, 0, 0)
        port2_label = QLabel('串口号：')
        self.port2_combo = QComboBox()
        port2_select_layout.addWidget(port2_label)
        port2_select_layout.addWidget(self.port2_combo)

        # 波特率选择
        baud2_select = QWidget()
        baud2_select_layout = QHBoxLayout(baud2_select)
        baud2_select_layout.setContentsMargins(0, 0, 0, 0)
        baud2_label = QLabel('波特率：')
        self.baud2_combo = QComboBox()
        self.baud2_combo.addItems(['9600'])
        baud2_select_layout.addWidget(baud2_label)
        baud2_select_layout.addWidget(self.baud2_combo)

        port2_layout.addWidget(port2_select)
        port2_layout.addWidget(baud2_select)

        # 打开串口按钮
        self.open2_button = QPushButton('打开串口')

        serial2_control_layout.addWidget(port2_widget)
        serial2_control_layout.addWidget(self.open2_button)
        serial2_control_layout.addStretch()

        # 串口2输出区
        self.serial2_output = QTextEdit()
        self.serial2_output.setReadOnly(True)

        serial2_layout.addWidget(serial2_control)
        serial2_layout.addWidget(self.serial2_output)

        # 将串口1和串口2添加到容器
        serial_container_layout.addWidget(serial1_group)
        serial_container_layout.addWidget(serial2_group)

        # 将文件浏览器和串口容器添加到顶部布局
        top_layout.addWidget(file_group)
        top_layout.addWidget(serial_container)

        # 区域4：信息输出框
        bottom_group = QWidget()
        bottom_layout = QVBoxLayout(bottom_group)
        bottom_label = QLabel('信息输出')
        self.bottom_output = QTextEdit()
        self.bottom_output.setReadOnly(True)
        bottom_layout.addWidget(bottom_label)
        bottom_layout.addWidget(self.bottom_output)
        bottom_group.setFixedHeight(150)  # 设置固定高度

        # 将所有区域添加到主布局
        main_layout.addWidget(top_widget)
        main_layout.addWidget(bottom_group)

        # 连接信号和槽
        self.refresh_ports(1)
        self.refresh_ports(2)
        self.open1_button.clicked.connect(lambda: self.toggle_serial(1))
        self.open2_button.clicked.connect(lambda: self.toggle_serial(2))

    def refresh_ports(self, port_num):
        combo = self.port1_combo if port_num == 1 else self.port2_combo
        combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        combo.addItems(ports)

    def toggle_serial(self, port_num):
        serial_obj = self.serial1 if port_num == 1 else self.serial2
        port_combo = self.port1_combo if port_num == 1 else self.port2_combo
        baud_combo = self.baud1_combo if port_num == 1 else self.baud2_combo
        open_button = self.open1_button if port_num == 1 else self.open2_button
        serial_output = self.serial1_output if port_num == 1 else self.serial2_output

        if serial_obj is None or not serial_obj.is_open:
            try:
                port = port_combo.currentText()
                baud = int(baud_combo.currentText())
                if port_num == 1:
                    self.serial1 = serial.Serial(port, baud)
                    self.monitor1 = SerialMonitor(self.serial1)
                    self.monitor1.data_received.connect(lambda data: self.serial1_output.append(data))
                    self.monitor1.start()
                else:
                    self.serial2 = serial.Serial(port, baud)
                    self.monitor2 = SerialMonitor(self.serial2)
                    self.monitor2.data_received.connect(lambda data: self.serial2_output.append(data))
                    self.monitor2.start()
                open_button.setText('关闭串口')
                serial_output.append(f'成功打开串口{port_num} {port}')
            except Exception as e:
                serial_output.append(f'打开串口{port_num}失败：{str(e)}')
        else:
            try:
                serial_obj.close()
                if port_num == 1:
                    if self.monitor1:
                        self.monitor1.stop()
                        self.monitor1 = None
                    self.serial1 = None
                else:
                    if self.monitor2:
                        self.monitor2.stop()
                        self.monitor2 = None
                    self.serial2 = None
                open_button.setText('打开串口')
                serial_output.append(f'串口{port_num}已关闭')
            except Exception as e:
                serial_output.append(f'关闭串口{port_num}失败：{str(e)}')

class SerialMonitor(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self._running = True

    def run(self):
        while self._running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data.decode('utf-8', errors='ignore'))
            except Exception as e:
                self.data_received.emit(f'监控错误：{str(e)}')
                break
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

def main():
    app = QApplication(sys.argv)
    window = SerialToolWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()