import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer, Signal


class NexusUI(QWidget):
    command_signal = Signal(str)
    response_signal = Signal(str)
    listening_signal = Signal()
    activity_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NEXUS — Neural Execution & Unified System")
        self.resize(1100, 700)
        self.pulse = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_core)
        self.timer.start(50)

        self.setStyleSheet("""
            QWidget {
                background-color: #05070a;
                color: #d8e7ff;
                font-family: Segoe UI;
            }

            QLabel#title {
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 4px;
            }

            QLabel#subtitle {
                font-size: 13px;
                color: #7f91a8;
                letter-spacing: 2px;
            }

            QLabel#status {
                font-size: 16px;
                font-weight: bold;
            }

            QFrame#panel {
                background-color: #0b1017;
                border: 1px solid #1d2a3a;
                border-radius: 14px;
            }

            QLabel#panelTitle {
                font-size: 13px;
                font-weight: bold;
                color: #8da4bf;
            }
            QLabel#activityStatus {
                font-size: 14px;
                font-weight: bold;
                color: #64b5ff;
            }
            QLabel#activityLog {
                font-size: 12px;
                color: #7f91a8;
                line-height: 1.5;
            }
            QLabel#core {
                font-size: 72px;
                font-weight: bold;
                color: #64b5ff;
            }
        """)

        # Header
        title = QLabel("N E X U S")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "NEURAL EXECUTION & UNIFIED SYSTEM"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        status = QLabel("●  SYSTEM ONLINE")
        self.status = status
        status.setObjectName("status")
        status.setAlignment(Qt.AlignCenter)

        # Central core
        core = QLabel("◉")
        self.core = core
        core.setObjectName("core")
        core.setAlignment(Qt.AlignCenter)

        core_text = QLabel("NEXUS CORE")
        core_text.setAlignment(Qt.AlignCenter)

        # Left panel
        activity_title = QLabel("ACTIVITY")
        activity_title.setObjectName("panelTitle")

        self.activity_status = QLabel("● SYSTEM READY")
        self.activity_status.setObjectName("activityStatus")

        self.activity_log = QLabel()
        self.activity_log.setObjectName("activityLog")
        self.activity_log.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.activity_history = []

        activity = QLabel(
            "System initialized\n"
            "Voice interface ready\n"
            "Gemini connection ready\n"
            "PC control ready\n"
            "Memory system ready"
        )
        activity.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        command = QLabel("Waiting for command...")
        self.command = command
        command.setObjectName("command")
        command.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        left_panel = QFrame()
        left_panel.setObjectName("panel")

        left_layout = QVBoxLayout()
        left_layout.addWidget(activity_title)
        left_layout.addWidget(self.activity_status)
        left_layout.addWidget(self.activity_log)
        left_layout.addWidget(activity)
        left_layout.addWidget(command)
        left_panel.setLayout(left_layout)

        # Right panel
        system_title = QLabel("SYSTEM")
        system_title.setObjectName("panelTitle")

        system = QLabel(
            "VOICE       READY\n"
            "MEMORY      READY\n"
            "PC CONTROL  READY\n"
            "BROWSER     READY"
        )
        system.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        right_panel = QFrame()
        right_panel.setObjectName("panel")

        right_layout = QVBoxLayout()
        right_layout.addWidget(system_title)
        right_layout.addWidget(system)
        right_panel.setLayout(right_layout)

        # Side panels
        panels = QHBoxLayout()
        panels.addWidget(left_panel)
        panels.addWidget(right_panel)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(15)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(core)
        layout.addWidget(core_text)
        layout.addStretch()
        layout.addLayout(panels)

        self.setLayout(layout)

        self.command_signal.connect(self.update_command)
        self.response_signal.connect(self.set_response)
        self.listening_signal.connect(self.set_listening)
        self.activity_signal.connect(self.set_activity)

    def set_listening(self):
        self.status.setText("●  LISTENING")

    def set_activity(self, text):
        self.activity_status.setText("● " + text)

        current = self.activity_log.text()
        if current:
            current += "\n"
        current += "✓ " + text

        self.activity_log.setText(current)

    def update_command(self, text):
        self.activity_history.clear()
        self.activity_log.clear()

        self.command.setText("YOU: " + text)


    def set_response(self, text):
        self.command.setText(self.command.text() + "\nNEXUS: " + text)

    def set_command(self, text):
        self.command.setText("YOU: " + text)

    def set_response(self, text):
        self.command.setText("NEXUS: " + text)

        self.core.setStyleSheet("font-size: 76px; font-weight: bold;")

    def animate_core(self):
        self.pulse += 1

        size = 68 + int(8 * abs(__import__("math").sin(self.pulse * 0.08)))

        self.core.setStyleSheet(
            f"font-size: {size}px; font-weight: bold;"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NexusUI()
    window.show()

    sys.exit(app.exec())