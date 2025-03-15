# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QTextEdit, QFileSystemModel, QTreeView, QCheckBox,
                             QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, QDir, QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
import serial
import serial.tools.list_ports
import time
import numpy as np

# 启用高DPI缩放
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class SerialToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.max_data_points = 100
        self.initUI()
        self.serial1 = None
        self.serial2 = None
        self.monitor1 = None
        self.monitor2 = None
        self.chart_data = []
        self.max_data_points = 100

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('串口调试助手 + TCP/UDP')
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

        # 串口1参数设置
        port1_params = QWidget()
        port1_params_layout = QVBoxLayout(port1_params)
        port1_params_layout.setSpacing(5)

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
        self.baud1_combo.addItems(['9600', '115200', '57600', '38400', '19200', '4800', '2400', '1200'])
        baud1_select_layout.addWidget(baud1_label)
        baud1_select_layout.addWidget(self.baud1_combo)

        # 数据位选择
        data1_select = QWidget()
        data1_select_layout = QHBoxLayout(data1_select)
        data1_select_layout.setContentsMargins(0, 0, 0, 0)
        data1_label = QLabel('数据位：')
        self.data1_combo = QComboBox()
        self.data1_combo.addItems(['8', '7', '6', '5'])
        data1_select_layout.addWidget(data1_label)
        data1_select_layout.addWidget(self.data1_combo)

        # 校验位选择
        parity1_select = QWidget()
        parity1_select_layout = QHBoxLayout(parity1_select)
        parity1_select_layout.setContentsMargins(0, 0, 0, 0)
        parity1_label = QLabel('校验位：')
        self.parity1_combo = QComboBox()
        self.parity1_combo.addItems(['None', 'Odd', 'Even', 'Mark', 'Space'])
        parity1_select_layout.addWidget(parity1_label)
        parity1_select_layout.addWidget(self.parity1_combo)

        # 停止位选择
        stop1_select = QWidget()
        stop1_select_layout = QHBoxLayout(stop1_select)
        stop1_select_layout.setContentsMargins(0, 0, 0, 0)
        stop1_label = QLabel('停止位：')
        self.stop1_combo = QComboBox()
        self.stop1_combo.addItems(['1', '1.5', '2'])
        stop1_select_layout.addWidget(stop1_label)
        stop1_select_layout.addWidget(self.stop1_combo)

        # 流控制选项
        flow1_control = QWidget()
        flow1_control_layout = QHBoxLayout(flow1_control)
        flow1_control_layout.setContentsMargins(0, 0, 0, 0)
        self.rts1_check = QCheckBox('RTS')
        self.dsr1_check = QCheckBox('DSR')
        self.cts1_check = QCheckBox('CTS')
        self.dtr1_check = QCheckBox('DTR')
        flow1_control_layout.addWidget(self.rts1_check)
        flow1_control_layout.addWidget(self.dsr1_check)
        flow1_control_layout.addWidget(self.cts1_check)
        flow1_control_layout.addWidget(self.dtr1_check)

        port1_params_layout.addWidget(port1_select)
        port1_params_layout.addWidget(baud1_select)
        port1_params_layout.addWidget(data1_select)
        port1_params_layout.addWidget(parity1_select)
        port1_params_layout.addWidget(stop1_select)
        port1_params_layout.addWidget(flow1_control)

        # 打开串口按钮
        self.open1_button = QPushButton('打开')

        # 接收设置
        receive1_group = QGroupBox('接收设置')
        receive1_layout = QVBoxLayout(receive1_group)
        self.save_to_file1 = QCheckBox('将接收保存到文件')
        self.hex_display1 = QCheckBox('十六进制显示')
        self.auto_linefeed1 = QCheckBox('自动换行')
        self.linefeed_ms1 = QSpinBox()
        self.linefeed_ms1.setRange(0, 1000)
        self.linefeed_ms1.setValue(20)
        self.linefeed_ms1.setSuffix(' ms')
        receive1_layout.addWidget(self.save_to_file1)
        receive1_layout.addWidget(self.hex_display1)
        receive1_layout.addWidget(self.auto_linefeed1)
        receive1_layout.addWidget(self.linefeed_ms1)

        # 发送设置
        send1_group = QGroupBox('发送设置')
        send1_layout = QVBoxLayout(send1_group)
        self.send_file1 = QCheckBox('发送文件')
        self.hex_send1 = QCheckBox('十六进制发送')
        self.timing_send1 = QCheckBox('定时发送')
        self.timing_ms1 = QSpinBox()
        self.timing_ms1.setRange(0, 10000)
        self.timing_ms1.setValue(1000)
        self.timing_ms1.setSuffix(' ms')
        send1_layout.addWidget(self.send_file1)
        send1_layout.addWidget(self.hex_send1)
        send1_layout.addWidget(self.timing_send1)
        send1_layout.addWidget(self.timing_ms1)

        serial1_control_layout.addWidget(port1_params)
        serial1_control_layout.addWidget(self.open1_button)
        serial1_control_layout.addWidget(receive1_group)
        serial1_control_layout.addWidget(send1_group)
        serial1_control_layout.addStretch()

        # 串口1输出区
        self.serial1_output = QTextEdit()
        self.serial1_output.setReadOnly(True)

        serial1_layout.addWidget(serial1_control)
        serial1_layout.addWidget(self.serial1_output)

        # 波形显示区
        wave_group = QWidget()
        wave_layout = QVBoxLayout(wave_group)
        wave_layout.setSpacing(5)

        # 波形显示标题
        wave_title = QLabel('波形显示区')
        wave_layout.addWidget(wave_title)

        # 创建图表
        self.chart = QChart()
        self.chart.setTitle('实时数据波形')
        self.chart.legend().hide()

        # 创建折线系列
        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        # 创建X轴和Y轴
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, self.max_data_points)
        self.axis_x.setTitleText('采样点')

        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 255)
        self.axis_y.setTitleText('数值')

        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        wave_layout.addWidget(self.chart_view)

        # 将串口1和串口2添加到容器
        serial_container_layout.addWidget(serial1_group)
        serial_container_layout.addWidget(wave_group)

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
        self.open1_button.clicked.connect(lambda: self.toggle_serial(1))

    def refresh_ports(self, port_num):
        combo = self.port1_combo
        combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        combo.addItems(ports)

    def handle_received_data(self, port_num, data):
        if port_num == 1:
            try:
                # 将接收到的数据转换为数值并添加到图表数据中
                values = [ord(c) for c in data]
                self.chart_data.extend(values)
                
                # 保持数据点数量在最大值以内
                if len(self.chart_data) > self.max_data_points:
                    self.chart_data = self.chart_data[-self.max_data_points:]
                
                # 更新图表数据
                self.series.clear()
                for i, value in enumerate(self.chart_data):
                    self.series.append(i, value)
                
                # 更新Y轴范围
                if self.chart_data:
                    min_val = min(self.chart_data)
                    max_val = max(self.chart_data)
                    margin = (max_val - min_val) * 0.1
                    self.axis_y.setRange(min_val - margin, max_val + margin)
            except Exception as e:
                self.bottom_output.append(f'波形显示错误：{str(e)}')
        
        # 更新输出框
        self.serial1_output.append(data)

    def toggle_serial(self, port_num):
        serial_obj = self.serial1
        port_combo = self.port1_combo
        baud_combo = self.baud1_combo
        data_combo = self.data1_combo
        parity_combo = self.parity1_combo
        stop_combo = self.stop1_combo
        open_button = self.open1_button
        serial_output = self.serial1_output

        if serial_obj is None or not serial_obj.is_open:
            try:
                port = port_combo.currentText()
                baud = int(baud_combo.currentText())
                data_bits = int(data_combo.currentText())
                parity = parity_combo.currentText()[0].upper()
                stop_bits = float(stop_combo.currentText())

                self.serial1 = serial.Serial(
                    port=port,
                    baudrate=baud,
                    bytesize=data_bits,
                    parity=parity,
                    stopbits=stop_bits
                )
                self.monitor1 = SerialMonitor(self.serial1)
                self.monitor1.data_received.connect(lambda data: self.handle_received_data(1, data))
                self.monitor1.start()
                open_button.setText('关闭')
                serial_output.append(f'成功打开串口{port_num} {port}')
            except Exception as e:
                serial_output.append(f'打开串口{port_num}失败：{str(e)}')
        else:
            try:
                serial_obj.close()
                if self.monitor1:
                    self.monitor1.stop()
                    self.monitor1 = None
                self.serial1 = None
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