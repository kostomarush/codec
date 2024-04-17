import sys
import numpy as np
import threading
import librosa as lr
import pyaudio
import wave
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
    QLabel, QSlider, QAction, QMenu, QMessageBox, QTabWidget, QFileDialog, QComboBox, 
    QLineEdit, QTextEdit
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from pydub import AudioSegment
from PyQt5 import QtWidgets, QtGui, QtCore
from pydub.playback import play
import struct
import os
import matplotlib.pyplot as plt

ico = os.path.join(sys._MEIPASS, "icon.ico") if getattr(sys, 'frozen', False) else "icon.ico"
app1 = QtWidgets.QApplication(sys.argv)
app1.setWindowIcon(QtGui.QIcon(ico))

stylesheet = """
    
    QTabWidget::pane {
                border: 2px solid orange; /* Рамка панели */
            }

    QTabBar::tab {
                background-color: #DCDCDC; /* Цвет фона кнопки */
                color: black; /* Цвет текста на кнопке */
            }
    QTabBar::tab:selected {
                background-color: orange; /* Цвет фона выбранной кнопки */
                color: black;
            }

    QWidget {
        background-color: #49423d;
        color: white;
    }

    QPushButton:disabled {
        color: black;
        background-color: white;
    }
    QPushButton:enabled {
        color: black;
        background-color: 	orange;
    }

     QMenuBar {
                background-color: #49423d; /* Цвет фона меню */
                color: white; /* Цвет текста в меню */
            }
            QMenuBar::item:selected {
                background-color: lightgrey; /* Цвет фона выбранного пункта меню */
                color: black; /* Цвет текста выбранного пункта меню */
            }
            QMenu {
                background-color: orange; /* Цвет фона подменю */
                color: black; /* Цвет текста в подменю */
            }
            QMenu::item:selected {
                background-color: lightgrey; /* Цвет фона выбранного пункта подменю */
                color: black; /* Цвет текста выбранного пункта подменю */
            }
            


"""

class LabeledSlider(QWidget):
    def __init__(self, orientation, min_val, max_val, default_val, title):
        super().__init__()
        layout = QVBoxLayout()
        self.slider = QSlider(orientation)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.label_min = QLabel(str(min_val))
        self.label_max = QLabel(str(max_val))
        self.slider.valueChanged.connect(self.update_labels)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.label_min)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.label_max)
        layout.addLayout(slider_layout)
        self.setLayout(layout)

    def update_labels(self):
        self.label_min.setText(str(self.slider.minimum()))
        self.label_max.setText(str(self.slider.maximum()))

    def value(self):
        return self.slider.value()

class DeltaCodecApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(stylesheet)
        self.thread_started = False
        self.play_thread = False
        self.stream = None
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.decodeded_signal = []
        self.file_path = ""
        self.initUI()

    def initUI(self):
        self.setObjectName("MainWindow")
        self.resize(1307, 656)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.activated.connect(self.enable_button)
        self.verticalLayout.addWidget(self.comboBox)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.level_kvantovan1 = QtWidgets.QLineEdit(self.groupBox)
        self.level_kvantovan1.setObjectName("level_kvantovan1")
        self.verticalLayout.addWidget(self.level_kvantovan1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.kolvo1 = QtWidgets.QLineEdit(self.groupBox)
        self.kolvo1.setObjectName("kolvo1")
        self.verticalLayout.addWidget(self.kolvo1)
        self.generite = QtWidgets.QPushButton(self.groupBox)
        self.generite.setObjectName("generite")
        self.generite.clicked.connect(self.generate_signal)
        self.verticalLayout.addWidget(self.generite)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.process_button = QtWidgets.QPushButton(self.groupBox)
        self.process_button.setObjectName("process_button")
        self.process_button.clicked.connect(self.process_signal)
        self.verticalLayout.addWidget(self.process_button)
        self.play_sound = QtWidgets.QPushButton(self.groupBox)
        self.play_sound.setObjectName("play_sound")
        self.play_sound.setEnabled(True)
        self.play_sound.clicked.connect(self.play_sound_thread)
        self.verticalLayout.addWidget(self.play_sound)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.level_kvantovan2 = QtWidgets.QLineEdit(self.groupBox)
        self.level_kvantovan2.setObjectName("level_kvantovan2")
        self.level_kvantovan2.setEnabled(False)
        self.verticalLayout.addWidget(self.level_kvantovan2)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.kolvo2 = QtWidgets.QLineEdit(self.groupBox)
        self.kolvo2.setObjectName("kolvo2")
        self.kolvo2.setEnabled(False)
        self.verticalLayout.addWidget(self.kolvo2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_1 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_1.setEnabled(False)
        self.pushButton_1.clicked.connect(self.start_recording)
        self.horizontalLayout_3.addWidget(self.pushButton_1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.clicked.connect(self.stop_recording)
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_99 = QtWidgets.QLabel(self.groupBox)
        self.label_99.setObjectName("label_99")
        self.verticalLayout.addWidget(self.label_99)
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        #self.comboBox.activated.connect(self.enable_button)
        self.verticalLayout.addWidget(self.comboBox_2)
        self.error_slider_2 = QtWidgets.QSlider(self.groupBox)
        self.error_slider_2.setOrientation(QtCore.Qt.Horizontal)
        self.error_slider_2.setObjectName("error_slider_2")
        self.verticalLayout.addWidget(self.error_slider_2)
        self.error_label_2 = QtWidgets.QLabel(self.groupBox)
        self.error_label_2.setObjectName("error_label_2")
        self.verticalLayout.addWidget(self.error_label_2)
        self.label_55 = QtWidgets.QLabel(self.groupBox)
        self.label_55.setObjectName("label_55")
        self.verticalLayout.addWidget(self.label_55)
        self.error_slider = QtWidgets.QSlider(self.groupBox)
        self.error_slider.setOrientation(QtCore.Qt.Horizontal)
        self.error_slider.setObjectName("error_slider")
        self.verticalLayout.addWidget(self.error_slider)
        self.error_label = QtWidgets.QLabel(self.groupBox)
        self.error_label.setObjectName("error_label")
        self.result_label = QtWidgets.QLabel(self.groupBox)
        self.result_label.setObjectName("result_label")
        self.verticalLayout.addWidget(self.error_label)
        self.verticalLayout.addWidget(self.result_label)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.show_signal_ches = QtWidgets.QTextEdit(self.groupBox)
        self.show_signal_ches.setObjectName("show_signal_ches")
        self.verticalLayout.addWidget(self.show_signal_ches)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_2.setLayout(layout)
        figure_size = (3, 4)
        self.original_figure = Figure(figsize=figure_size)
        self.original_figure.set_facecolor('#49423d')
        self.original_canvas = FigureCanvas(self.original_figure)
        self.original_nav_toolbar = NavigationToolbar2QT(self.original_canvas, self)
        layout.addWidget(self.original_canvas)
        layout.addWidget(self.original_nav_toolbar)
        self.discretnie_figure = Figure(figsize=figure_size)
        self.discretnie_figure.set_facecolor('#49423d')
        self.discretnie_canvas = FigureCanvas(self.discretnie_figure)
        self.discretnie_nav_toolbar = NavigationToolbar2QT(self.discretnie_canvas, self)
        layout.addWidget(self.discretnie_canvas)
        layout.addWidget(self.discretnie_nav_toolbar)
        self.kvant_figure = Figure(figsize=figure_size)
        self.kvant_figure.set_facecolor('#49423d')
        self.kvant_canvas = FigureCanvas(self.kvant_figure)
        self.kvant_nav_toolbar = NavigationToolbar2QT(self.kvant_canvas, self)
        layout.addWidget(self.kvant_canvas)
        layout.addWidget(self.kvant_nav_toolbar)
        self.encoded_figure = Figure(figsize=figure_size)
        self.encoded_figure.set_facecolor('#49423d')
        self.encoded_canvas = FigureCanvas(self.encoded_figure)
        self.encoded_nav_toolbar = NavigationToolbar2QT(self.encoded_canvas, self)
        layout.addWidget(self.encoded_canvas)
        layout.addWidget(self.encoded_nav_toolbar)
        self.decoded_figure = Figure(figsize=figure_size)
        self.decoded_figure.set_facecolor('#49423d')
        self.decoded_canvas = FigureCanvas(self.decoded_figure)
        self.decoded_nav_toolbar = NavigationToolbar2QT(self.decoded_canvas, self)
        layout.addWidget(self.decoded_canvas)
        layout.addWidget(self.decoded_nav_toolbar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1307, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.setMenuBar(self.menubar)
        self.action = QtWidgets.QAction(self)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(self)
        self.action_2.setObjectName("action_2")
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menubar.addAction(self.menu.menuAction())
        
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Дельта-кодек речевого сигнала"))
        self.groupBox.setTitle(_translate("MainWindow", "Входные параметры"))
        self.label.setText(_translate("MainWindow", "Выбор сигнала:"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Гармонический"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Пилообразный"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Треугольный"))
        self.comboBox.setItemText(3, _translate("MainWindow", "Случайный"))
        self.comboBox.setItemText(4, _translate("MainWindow", "Запись с микрофона"))
        self.label_2.setText(_translate("MainWindow", "Введите количество уровней квантования:"))
        self.label_3.setText(_translate("MainWindow", "Введите количество отображаемого промежутка:"))
        self.generite.setText(_translate("MainWindow", "Вид сигнала при дельта модуляции"))
        self.label_4.setText(_translate("MainWindow", "Работа с записью:"))
        self.process_button.setText(_translate("MainWindow", "Обработать"))
        self.play_sound.setText(_translate("MainWindow", "Проиграть"))
        self.label_5.setText(_translate("MainWindow", "Введите уровень квантования для сигнала записанного с микрофона:"))
        self.label_6.setText(_translate("MainWindow", "Введите количество отображаемого промежутка для сигнала записанного с микрофона:"))
        self.pushButton_1.setText(_translate("MainWindow", "Начать запись"))
        self.pushButton_2.setText(_translate("MainWindow", "Остановить запись"))
        self.label_99.setText(_translate("MainWindow", "Выбор единицы измерения для добавления шума:"))
        self.label_55.setText(_translate("MainWindow", "Добавить уровень ошибок:"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "дБ"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "мВт"))
        self.error_label.setText(_translate("MainWindow", "Уровень ошибок 0%"))
        self.error_label_2.setText(_translate("MainWindow", "Значение ошибок дБ"))
        self.result_label.setText(_translate("MainWindow", ""))
        self.label_8.setText(_translate("MainWindow", "Просмотр значений:"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Просмотр графиков"))
        self.menu.setTitle(_translate("MainWindow", "Информация"))
        self.action.setText(_translate("MainWindow", "О программе"))
        self.action_2.setText(_translate("MainWindow", "Системные требования"))

    def show_about_dialog(self):
        QMessageBox.about(self, 'О программе', "<b>Дельта-кодер речевого сигнала</b><br><br>"
    "<b>Основные функции программы:</b><br>"
    "1. <u>Запись аудиосигнала с микрофона:</u> Программа записывает звук с микрофона компьютера.<br>"
    "2. <u>Обработка и дельта-кодирование речевого сигнала:</u> Записанный аудиосигнал подвергается дельта-кодированию.<br>"
    "3. <u>Сохранение закодированного аудиосигнала:</u> Закодированный сигнал сохраняется в файл.<br>"
    "4. <u>Декодирование аудиосигнала:</u> Программа предоставляет функциональность для декодирования речевого сигнала.<br>"
    "5. <u>Графический интерфейс пользователя (GUI):</u> Для удобства использования программа включает графический интерфейс.<br>"
    "6. <u>Настройки параметров кодирования:</u> Пользователь может настраивать параметры дельта-кодирования.<br><br>"
    "<b>Технологии и библиотеки:</b><br>"
    "- PyQt5 или Tkinter для GUI.<br>"
    "- PyAudio для записи аудиосигнала.<br>"
    "- NumPy для обработки аудиоданных и реализации дельта-кодирования.<br>"
    "- Wave или другие аудио-библиотеки для сохранения и воспроизведения аудиосигнала.<br>"
    "<br>"
    "<i>Программа также может предоставлять возможности анализа звука, визуализации аудиосигнала и другие дополнительные функции в зависимости от требований пользователя.</i>")
    
    def show_harakter_dialog(self):
        QMessageBox.about(self, 'Системные требования',  "<b>Системные требования</b><br><br>"
    "<b>Минимальные требования:</b><br>"
    "- <u>Операционная система:</u> Windows 7<br>"
    "- <u>Процессор:</u> Intel Core i3 или аналогичный<br>"
    "- <u>Оперативная память:</u> 4 ГБ<br>"
    "- <u>Свободное место на жестком диске:</u> 10 ГБ<br>"
    "- <u>Звуковая карта:</u> Совместимая с DirectX 9.0c<br><br>"
    "<b>Рекомендуемые требования:</b><br>"
    "- <u>Операционная система:</u> Windows 10<br>"
    "- <u>Процессор:</u> Intel Core i5 или аналогичный<br>"
    "- <u>Оперативная память:</u> 8 ГБ<br>"
    "- <u>Свободное место на жестком диске:</u> 20 ГБ<br>"
    "- <u>Звуковая карта:</u> Совместимая с DirectX 9.0c<br><br>"
    "<i>Примечание: Требования могут изменяться в зависимости от версии программы и использованных библиотек.</i>")

    def enable_button(self):
        if self.comboBox.currentText() == 'Запись с микрофона':
            self.pushButton_1.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.process_button.setEnabled(True)
            self.level_kvantovan2.setEnabled(True)
            self.kolvo2.setEnabled(True)
            self.generite.setEnabled(False)
            self.level_kvantovan1.setEnabled(False)
            self.kolvo1.setEnabled(False)
        else:
            self.pushButton_1.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.process_button.setEnabled(False)
            self.generite.setEnabled(True)
            self.level_kvantovan1.setEnabled(True)
            self.level_kvantovan2.setEnabled(False)
            self.kolvo1.setEnabled(True)
            self.kolvo2.setEnabled(False)

    def generate_signal(self):
        if (self.level_kvantovan1.text() == '') or not ((self.level_kvantovan1.text().isdigit())):
            QMessageBox.critical(self, 'Ошибка', 'Введите уровень квантования')
        elif (self.kolvo1.text() == '') or not (self.kolvo1.text().isdigit()):
            QMessageBox.critical(self, 'Ошибка', 'Введите количество отображаемого сигнала')
        else:
            signal_type = self.comboBox.currentText()
            if signal_type == 'Гармонический':
                signal = self.generate_harmonic_signal()
                self.process_random_signal(signal)
            elif signal_type == 'Пилообразный':
                signal = self.generate_sawtooth_signal()
                self.process_random_signal(signal)
            elif signal_type == 'Треугольный':
                signal = self.generate_triangle_signal()
                self.process_random_signal(signal)
            elif signal_type == 'Случайный':
                signal = self.generate_random_signal()
                self.process_random_signal(signal)

    def generate_harmonic_signal(self):
        time = np.linspace(0, 1, 44100) 
        frequency = 440  
        amplitude = 0.5  
        harmonic_signal = amplitude * np.sin(2 * np.pi * frequency * time)
        return harmonic_signal

    def generate_sawtooth_signal(self):
        time = np.linspace(0, 1, 44100)  
        frequency = 440  
        amplitude = 0.5  
        period = 1 / frequency
        sawtooth_signal = 2 * amplitude * (time % period) / period - amplitude
        return sawtooth_signal

    def generate_triangle_signal(self):
        time = np.linspace(0, 1, 44100)  
        frequency = 440  
        amplitude = 0.5  
        period = 1 / frequency 
        triangle_signal = amplitude * (2 * np.abs(2 * (time % period) / period - 1) - 1)
        return triangle_signal

    def generate_random_signal(self):
        random_signal = np.random.uniform(-1, 1, 44100)
        return random_signal

    def set_zoom_factor(self, zoom_factor):
        for nav_toolbar, canvas in [
            (self.original_nav_toolbar, self.original_canvas),
            (self.encoded_nav_toolbar, self.encoded_canvas),
            (self.decoded_nav_toolbar, self.decoded_canvas),
        ]:
            nav_toolbar.set_xscale(1.0 / zoom_factor)
            nav_toolbar.set_yscale(1.0 / zoom_factor)
            canvas.draw()

    def toggle_zoom(self):
        if self.zoom_button.isChecked():
            self.original_nav_toolbar.pan()
            self.encoded_nav_toolbar.pan()
            self.decoded_nav_toolbar.pan()
        else:
            self.original_nav_toolbar.zoom()
            self.encoded_nav_toolbar.zoom()
            self.decoded_nav_toolbar.zoom()
            self.sync_axes_zoom()

    def sync_axes_zoom(self):
        self.zoom_factor = self.original_nav_toolbar.get_zoom_factor()
        self.set_zoom_factor(self.zoom_factor)

    def setup_figure_manager(self, figureManager):
        self.figureManager = figureManager

    def toggle_full_screen(self):
        if self.figureManager:
            self.figureManager.full_screen_toggle()

    def plot_signal(self, figure, canvas, signal, color, title):
        time = np.linspace(-1, 1, len(signal))
        figure.clear()
        figure.subplots_adjust(top=1.0, bottom=0.14, left=0.055, right=0.99, hspace=0.2, wspace=0.2)
        ax = figure.add_subplot()
        ax.plot(time, signal, label=title, color=color)
        ax.set_xlabel('Время(с)', color = 'w')
        ax.set_ylabel('Напр-ие(В)', color = 'w')
        ax.legend()
        ax.grid(True)
        canvas.draw()

    def plot_signal_code(self, figure, canvas, signal, color, title):
        figure.clear()
        figure.subplots_adjust(top=1.0, bottom=0.14, left=0.055, right=0.99, hspace=0.2, wspace=0.2)
        ax = figure.add_subplot()
        binary_signal = [1 if signal[i] > signal[i - 1] else 0 for i in range(1, len(signal))]
        binary_signal = [0] + binary_signal
        ax.step(range(len(binary_signal)), binary_signal, color=color, label=title)
        ax.set_xlabel('Время(с)', color = 'w')
        ax.set_ylabel('Напр-ие(В)', color = 'w')
        ax.legend()
        ax.grid(True)
        canvas.draw()

    def plot_discrete_signal(self, figure, canvas, signal, color, title):
        time = np.linspace(-1, 1, len(signal))
        figure.clear()
        figure.subplots_adjust(top=1.0, bottom=0.14, left=0.055, right=0.99, hspace=0.2, wspace=0.2)
        ax = figure.add_subplot()
        ax.plot(time, signal, marker='o', color=color, label=title,linestyle='-')
        ax.set_xlabel('Время (сек)', color='w')
        ax.set_ylabel('Амплитуда', color='w')
        ax.legend()
        ax.grid(True)
        canvas.draw()

    def plot_quantized_signal(self, figure, canvas, signal, quantization_levels, color, title):
        time = np.linspace(-1, 1, len(signal))
        figure.clear()
        figure.subplots_adjust(top=1.0, bottom=0.14, left=0.055, right=0.99, hspace=0.2, wspace=0.2)
        ax = figure.add_subplot()
        ax.plot(time, signal, drawstyle='steps-pre', color=color, label=title, linestyle='-')
        ax.set_xlabel('Время(с)', color='w')
        ax.set_ylabel('Ур-нь кван-ия', color='w')
        ax.set_yticks(quantization_levels)
        ax.legend()
        ax.grid(True)
        canvas.draw() 

    def update_error_level(self):
        self.error_level = self.error_slider.value()
        self.error_label.setText(f'Количество ошибок: {self.error_level}%')

    def update_error_level_2(self):
        self.error_level_2 = self.error_slider_2.value()
        izmer = "дБ"
        if self.comboBox_2.currentText() == "мВт":
            izmer = "мВт"
        self.error_label_2.setText(f'Количество ошибок: {self.error_level_2} {izmer}')
    

    def add_errors(self, signal):
        num_samples = len(signal)
        num_errors = int(num_samples * self.error_level / 10000)
        error_indices = np.random.choice(num_samples, num_errors, replace=False)
        signal_with_errors = np.copy(signal)
        signal_with_errors[error_indices] = np.random.uniform(-1, 1, num_errors)
        return signal_with_errors
    
    def add_noise(self, signal):
        if self.comboBox_2.currentText() == "мВт":
            # Преобразование значения шума из мВт в дБ
            noise_dB = 10 * np.log10(self.error_level_2)
            noise = np.random.normal(0, noise_dB, len(signal))
        else:  # По умолчанию рассматриваем дБ
            noise = np.random.normal(0, self.error_level_2, len(signal))
            
        noisy_signal = signal + noise
        return noisy_signal

    def process_signal(self):
        if (self.level_kvantovan2.text() == '') or not ((self.level_kvantovan2.text().isdigit())):
            QMessageBox.critical(self, 'Ошибка', 'Введите уровень квантования')
        elif (self.kolvo2.text() == '') or not (self.kolvo2.text().isdigit()):
            QMessageBox.critical(self, 'Ошибка', 'Введите количество отображаемого сигнала')
        else:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, 'Выберите аудиофайл', '', 'Audio files (*.mp3 *.wav)')
            if file_path:
                audio, sample_rate = lr.load(file_path, sr=None)
                self.show_signal_ches.clear()
                self.show_signal_ches.setPlainText(np.array2string(audio, threshold=sys.maxsize))
                self.original_signal = audio
                self.update_error_level()
                self.original_signal1 = self.add_errors(self.original_signal)
                self.encoded_signal = self.delta_encode(self.original_signal1)
                decoded_signal = self.delta_decode(self.encoded_signal)
                self.decodeded_signal = decoded_signal
                error_bits_per_second = self.calculate_error_bits_per_second(self.original_signal, self.decodeded_signal)
                mse_error = self.calculate_mse_error(self.original_signal, self.decodeded_signal    )
                self.result_label.setText(f'Количество ошибок за секунду: {error_bits_per_second:.20f} \nСредне квадратичная ошибка: {round(mse_error,6)}')
                gotov_orgignal_signal = self.original_signal[:int(self.kolvo2.text())]
                gotov_encoded_signal = self.encoded_signal[:int(self.kolvo2.text())]
                gotov_decoded_signal = decoded_signal[:int(self.kolvo2.text())]
                self.plot_signal(self.original_figure, self.original_canvas, gotov_orgignal_signal, 'b', 'Оригинальный сигнал')
                self.plot_signal_code(self.encoded_figure, self.encoded_canvas, gotov_encoded_signal, 'orange', 'Закодированный сигнал')
                self.plot_signal(self.decoded_figure, self.decoded_canvas, gotov_decoded_signal, 'r', 'Декодированный сигнал')
                self.plot_discrete_signal(self.discretnie_figure, self.discretnie_canvas, gotov_encoded_signal, 'green', 'Дискретный сигнал')
                self.plot_quantized_signal(self.kvant_figure, self.kvant_canvas, gotov_encoded_signal, self.auto_quantization_levels(gotov_encoded_signal, int(self.level_kvantovan2.text())), 'violet', 'Квантованный сигнал')

    def process_random_signal(self, signal):
        self.original_signal = signal
        self.show_signal_ches.clear()
        rounded_signal = np.round(signal, 3)
        self.show_signal_ches.setPlainText(np.array2string(rounded_signal, threshold=sys.maxsize))
        self.update_error_level()
        self.original_signal1 = self.add_errors(self.original_signal) 
        self.encoded_signal = self.delta_encode(self.original_signal1)
        decoded_signal = self.delta_decode(self.encoded_signal)
        self.decodeded_signal = decoded_signal
        error_bits_per_second = self.calculate_error_bits_per_second(self.original_signal, decoded_signal)
        mse_error = self.calculate_mse_error(self.original_signal, decoded_signal)
        print(mse_error)
        self.result_label.setText(f'Количество ошибок за секунду: {error_bits_per_second:.20f} \nСредне квадратичная ошибка: {round(mse_error,6)}')
        gotov_orgignal_signal = self.original_signal[:int(self.kolvo1.text())]
        gotov_encoded_signal = self.encoded_signal[:int(self.kolvo1.text())]
        gotov_decoded_signal = decoded_signal[:int(self.kolvo1.text())]
        self.plot_signal(self.original_figure, self.original_canvas, gotov_orgignal_signal, 'b', 'Оригинальный сигнал')
        self.plot_signal_code(self.encoded_figure, self.encoded_canvas, gotov_encoded_signal, 'orange', 'Закодированный сигнал')
        self.plot_signal(self.decoded_figure, self.decoded_canvas, gotov_decoded_signal, 'r', 'Декодированный сигнал')
        self.plot_discrete_signal(self.discretnie_figure, self.discretnie_canvas, gotov_encoded_signal, 'green', 'Дискретный сигнал')
        self.plot_quantized_signal(self.kvant_figure, self.kvant_canvas, gotov_encoded_signal, self.auto_quantization_levels(gotov_encoded_signal, int(self.level_kvantovan1.text())), 'violet', 'Квантованный сигнал')

    def auto_quantization_levels(self, signal, num_levels):
        hist, bins = np.histogram(signal, bins=num_levels)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        quantization_levels = bin_centers
        return quantization_levels

    def calculate_error_bits_per_second(self, original_signal, decoded_signal):
        error_bits = np.sum(original_signal != decoded_signal)
        duration_seconds = len(original_signal) / 48000
        bits_per_second = error_bits / duration_seconds
        return int(bits_per_second)

    def calculate_mse_error(self, original_signal, decoded_signal):
        mse_error = np.mean((original_signal - decoded_signal) ** 2)
        return mse_error

    def delta_encode(self, signal):
        delta_signal = [signal[0]]  
        for i in range(1, len(signal)):
            delta = signal[i] - signal[i - 1]
            delta_signal.append(delta)
        return delta_signal

    def delta_decode(self, delta_signal):
        decode_signal = [delta_signal[0]]  
        for i in range(1, len(delta_signal)):
            value = decode_signal[i - 1] + delta_signal[i]
            decode_signal.append(value)
        return decode_signal

    def delta_decode_binary(self, delta_signal):
        signal = [delta_signal[0]]
        for i in range(1, len(delta_signal)):
            value = signal[i - 1] + delta_signal[i]
            signal.append(value)
        return signal

    def start_recording(self):
        file_dialog = QFileDialog()
        self.file_path, _ = file_dialog.getSaveFileName(self, 'Выберите место сохранения', '', 'Audio files (*.mp3 *.wav)')

        if self.file_path:
            try:
                self.stream = self.audio.open(format=pyaudio.paInt16,
                                              channels=1,
                                              rate=44100,
                                              input=True,
                                              frames_per_buffer=1024)
                self.my_thread = threading.Thread(target=self.record_audio)
                self.my_thread.start()
            except:
                QMessageBox.critical(self, 'Ошибка', 'Нет устройства записи')
        

    def record_audio(self):
        self.frames = []
        while self.stream.is_active():
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            wf = wave.open(self.file_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"Аудиофайл сохранен по пути: {self.file_path}")
        
    def plays_sound(self):
        audio_bytes = b''.join(struct.pack('<h', int(sample * 32767)) for sample in self.decodeded_signal)
        sample_width = 2  
        frame_rate = 44100  
        channels = 1 
        with wave.open('temp_audio.wav', 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(frame_rate)
            wf.writeframes(audio_bytes)
        decoded_audio = AudioSegment.from_wav('./temp_audio.wav')
        play(decoded_audio)
        os.remove('./temp_audio.wav')
           
    def play_sound_thread(self):
        try:
            if self.decodeded_signal:
                self.plays_sound()
                
            else:
                QMessageBox.warning(self, 'Ошибка', 'Декодированный сигнал не найден')
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DeltaCodecApp()
    window.showMaximized() 
    sys.exit(app.exec_())
