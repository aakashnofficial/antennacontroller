import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSlider, QPushButton, QDial
from PyQt5.QtCore import Qt
from CustomDial import CustomDial
import requests


class AntennaController(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.current_azimuth = 0
        self.current_elevation = 0
        self.update_angles()

    def initUI(self):
        layout = QGridLayout()
        self.setStyleSheet("""
        AntennaController {
                background-color: #f2f1f0;
            }
        """)

        # Azimuth control
        self.azimuth_dial = CustomDial(self)
        self.azimuth_dial.setStyleSheet("""
                                    QDial {
                                        background-color: transparent;
                                        border-radius: 275px; /* Adjust to match the handle size */
                                        margin: 20px;
                                    }
                                """)

        self.azimuth_dial.valueChanged.connect(self.update_new_azimuth)

        self.azimuth_display = QWidget()
        self.azimuth_display_layout = QVBoxLayout()

        self.current_azimuth_label = QLabel()
        self.current_azimuth_label.setAlignment(Qt.AlignLeft)
        self.new_azimuth_label = QLabel()
        self.new_azimuth_label.setAlignment(Qt.AlignLeft)
        self.azimuth_title = QLabel()
        self.azimuth_title.setAlignment(Qt.AlignCenter)
        self.azimuth_title.setText("Azimuth")
        self.azimuth_title.setStyleSheet("""color: #3e3d3d; 
                                            font-size: 25px;
                                            font-weight: 1000;""")
        self.azimuth_display_layout.addWidget(self.azimuth_title)
        self.azimuth_display_layout.addWidget(self.current_azimuth_label)
        self.azimuth_display_layout.addWidget(self.new_azimuth_label)


        self.azimuth_display.setLayout(self.azimuth_display_layout)
        self.azimuth_display.setFixedSize(230, 140)
        self.azimuth_display.setStyleSheet("""
                                   background-color: #D2B48C; 
                                   border-radius: 15px; 
                                   color: #3e3d3d;
                                   font-size: 20px;
                                   font-weight: 100;
                               """)

        # Elevation control
        self.elevation_slider = QSlider(Qt.Vertical)
        self.elevation_slider.setMinimum(0)
        self.elevation_slider.setMaximum(360)
        self.elevation_slider.valueChanged.connect(self.update_new_elevation)
        self.elevation_slider.setFixedSize(116, 550)
        self.elevation_slider.setStyleSheet("""
                    QSlider::groove:vertical {
                        background: #6a8b99;
                        border-radius: 58px;
                        width: 116px;
                        margin: 1px 1px;
                    }
                    QSlider::handle:vertical {
                        background: #1d3c4e;
                        height: 40px;
                        width: 40px;
                        margin: 10px 38px;
                        border-radius: 20px;
                    }
                """)

        self.elevation_display = QWidget()
        self.elevation_display_layout = QVBoxLayout()

        self.current_elevation_label = QLabel()
        self.current_elevation_label.setAlignment(Qt.AlignLeft)
        self.new_elevation_label = QLabel()
        self.new_elevation_label.setAlignment(Qt.AlignLeft)
        self.elevation_title = QLabel()
        self.elevation_title.setAlignment(Qt.AlignCenter)
        self.elevation_title.setText("Elevation")
        self.elevation_title.setStyleSheet("""
                                            color: #3e3d3d;
                                            font-size: 25px;
                                            font-weight: 1000""")
        self.elevation_display_layout.addWidget(self.elevation_title)
        self.elevation_display_layout.addWidget(self.current_elevation_label)
        self.elevation_display_layout.addWidget(self.new_elevation_label)

        self.elevation_display.setLayout(self.elevation_display_layout)
        self.elevation_display.setFixedSize(230, 140)
        self.elevation_display.setStyleSheet("""
                    background-color: #D2B48C; 
                    color: #3e3d3d;
                    border-radius: 15px; 
                    font-size: 20px;
                    font-weight: 100;
                """)

        # Buttons
        self.refresh_button = QPushButton("Refresh Position")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedSize(350, 150)
        self.refresh_button.setStyleSheet("background-color: #72c6f4; color: #172a35; font-size: 50px; border-radius: 75px;")
        self.refresh_button.clicked.connect(self.refresh_position)

        self.send_button = QPushButton("Send to Controller")
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(350, 150)
        self.send_button.setStyleSheet("background-color: #172a35; color: #72c6f4; font-size: 50px; border-radius: 75px;")
        self.send_button.clicked.connect(self.send_to_controller)

        layout.addWidget(self.elevation_slider, 1, 2, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.azimuth_dial, 1, 0, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.azimuth_display, 0, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.elevation_display, 0, 2, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.refresh_button, 2, 0, alignment=Qt.AlignCenter)
        layout.addWidget(self.send_button, 2, 2, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.setWindowTitle('Antenna Controller')
        self.show()

    def update_new_azimuth(self, value):
        self.new_azimuth_label.setText(f"New Azimuth       : {value}°")

    def update_new_elevation(self, value):
        self.new_elevation_label.setText(f"New Elevation      : {value}°")

    def refresh_position(self):
        # Call Flask API to get the current positions
        response = requests.get('http://localhost:5000/get_current_position')
        if response.status_code == 200:
            data = response.json()
            self.current_azimuth = data['azimuth']
            self.current_elevation = data['elevation']
            self.current_azimuth_label.setText(f"Current Azimuth    : {self.current_azimuth}°")
            self.current_elevation_label.setText(f"Current Elevation: {self.current_elevation}°")

    def send_to_controller(self):
        new_azimuth = self.azimuth_dial.value()
        new_elevation = self.elevation_slider.value()
        data = {'azimuth': new_azimuth, 'elevation': new_elevation}
        response = requests.post('http://localhost:5000/set_position', json=data)
        if response.status_code == 200:
            self.refresh_position()

    def update_angles(self):
        self.current_azimuth_label.setText(f"Current Azimuth : {self.current_azimuth}°")
        self.new_azimuth_label.setText(f"New Azimuth       : {self.azimuth_dial.value()}°")
        self.current_elevation_label.setText(f"Current Elevation : {self.current_elevation}°")
        self.new_elevation_label.setText(f"New Elevation      : {self.elevation_slider.value()}°")

def runGUI():
    app = QApplication(sys.argv)
    ex = AntennaController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    runGUI()