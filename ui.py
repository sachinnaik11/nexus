# ============================================================
# NEXUS V1 — FUTURISTIC JARVIS-STYLE USER INTERFACE
# ============================================================

import sys
import os
import math
import threading
import webbrowser
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QScrollArea,
    QTextBrowser,
    QSizePolicy,
    QTabWidget,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtCore import Qt, QTimer, Signal, QMetaObject, Q_ARG
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QRadialGradient,
    QFont,
    QIcon,
    QPixmap,
)

# Optional system monitoring
try:
    import psutil
except ImportError:
    psutil = None


# ============================================================
# JARVIS ANIMATED CORE WIDGET
# ============================================================

class JarvisCoreWidget(QWidget):
    """
    Futuristic circular AI core visualizer.
    Renders dynamic concentric rings, glowing cyber-arcs, and
    pulsing state waves (IDLE, LISTENING, THINKING, SPEAKING, ERROR).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "IDLE"  # IDLE, LISTENING, THINKING, SPEAKING, ERROR
        self.angle = 0
        self.pulse = 0
        self.setMinimumSize(220, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # High-performance non-blocking animation timer (~30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_step)
        self.timer.start(33)

    def set_state(self, new_state: str):
        valid_states = ("IDLE", "LISTENING", "THINKING", "SPEAKING", "ERROR")
        if new_state.upper() in valid_states:
            self.state = new_state.upper()
            self.update()

    def _animate_step(self):
        self.pulse += 1

        # Angular rotation speed depends on state
        if self.state == "THINKING":
            self.angle = (self.angle + 4) % 360
        elif self.state == "LISTENING":
            self.angle = (self.angle + 2) % 360
        elif self.state == "SPEAKING":
            self.angle = (self.angle + 3) % 360
        else:
            self.angle = (self.angle + 1) % 360

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        radius = min(cx, cy) - 15

        if radius <= 10:
            painter.end()
            return

        # ----------------------------------------------------
        # COLOR THEMES BASED ON STATE
        # ----------------------------------------------------
        if self.state == "LISTENING":
            base_color = QColor(0, 255, 230)       # Electric Neon Cyan
            glow_color = QColor(0, 255, 230, 90)
            inner_color = QColor(0, 210, 255)
            status_text = "LISTENING"
        elif self.state == "THINKING":
            base_color = QColor(147, 51, 234)      # Electric Violet / Blue
            glow_color = QColor(59, 130, 246, 120)
            inner_color = QColor(99, 102, 241)
            status_text = "THINKING"
        elif self.state == "SPEAKING":
            base_color = QColor(56, 189, 248)      # Harmonic Sky Blue
            glow_color = QColor(14, 165, 233, 110)
            inner_color = QColor(2, 132, 199)
            status_text = "SPEAKING"
        elif self.state == "ERROR":
            base_color = QColor(239, 68, 68)       # Crimson Warning
            glow_color = QColor(220, 38, 38, 100)
            inner_color = QColor(185, 28, 28)
            status_text = "ALERT"
        else:  # IDLE
            base_color = QColor(0, 212, 255)       # Calm JARVIS Cyan
            glow_color = QColor(0, 150, 255, 55)
            inner_color = QColor(0, 119, 182)
            status_text = "NEXUS ONLINE"

        # Dynamic pulse calculation
        pulse_factor = 0.5 + 0.5 * math.sin(self.pulse * 0.08)
        current_glow = radius * (0.85 + 0.12 * pulse_factor)

        # ----------------------------------------------------
        # 1. OUTER AMBIENT GLOW
        # ----------------------------------------------------
        radial = QRadialGradient(cx, cy, current_glow)
        radial.setColorAt(0.0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 100))
        radial.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 30))
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - current_glow), int(cy - current_glow), int(current_glow * 2), int(current_glow * 2))

        # ----------------------------------------------------
        # 2. OUTER CYBERNETIC RING WITH ROTATING TICKS
        # ----------------------------------------------------
        r_outer = radius * 0.95
        painter.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 45), 1.5))
        painter.drawEllipse(int(cx - r_outer), int(cy - r_outer), int(r_outer * 2), int(r_outer * 2))

        # HUD ticks around outer ring
        num_ticks = 36
        tick_len = 5
        painter.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 120), 1.5))
        for i in range(num_ticks):
            deg = (i * (360 / num_ticks) + self.angle) * math.pi / 180
            x1 = cx + (r_outer - tick_len) * math.cos(deg)
            y1 = cy + (r_outer - tick_len) * math.sin(deg)
            x2 = cx + r_outer * math.cos(deg)
            y2 = cy + r_outer * math.sin(deg)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # ----------------------------------------------------
        # 3. ROTATING ARC SEGMENTS
        # ----------------------------------------------------
        r_arcs = radius * 0.78
        pen_arc1 = QPen(base_color, 2.5)
        painter.setPen(pen_arc1)
        painter.drawArc(
            int(cx - r_arcs), int(cy - r_arcs), int(r_arcs * 2), int(r_arcs * 2),
            int(self.angle * 16), int(70 * 16)
        )
        painter.drawArc(
            int(cx - r_arcs), int(cy - r_arcs), int(r_arcs * 2), int(r_arcs * 2),
            int((self.angle + 120) * 16), int(70 * 16)
        )
        painter.drawArc(
            int(cx - r_arcs), int(cy - r_arcs), int(r_arcs * 2), int(r_arcs * 2),
            int((self.angle + 240) * 16), int(70 * 16)
        )

        # Counter-rotating inner ring
        r_inner_arc = radius * 0.62
        pen_arc2 = QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 180), 2.0)
        painter.setPen(pen_arc2)
        counter_angle = (-self.angle * 1.5) % 360
        painter.drawArc(
            int(cx - r_inner_arc), int(cy - r_inner_arc), int(r_inner_arc * 2), int(r_inner_arc * 2),
            int(counter_angle * 16), int(100 * 16)
        )
        painter.drawArc(
            int(cx - r_inner_arc), int(cy - r_inner_arc), int(r_inner_arc * 2), int(r_inner_arc * 2),
            int((counter_angle + 180) * 16), int(100 * 16)
        )

        # ----------------------------------------------------
        # 4. CENTRAL GLOWING CORE SPHERE
        # ----------------------------------------------------
        r_core = radius * (0.35 + 0.05 * pulse_factor)
        core_grad = QRadialGradient(cx, cy, r_core)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 230))
        core_grad.setColorAt(0.4, base_color)
        core_grad.setColorAt(0.85, inner_color)
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - r_core), int(cy - r_core), int(r_core * 2), int(r_core * 2))

        # ----------------------------------------------------
        # 5. CORE STATUS LABEL
        # ----------------------------------------------------
        painter.setPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 230))
        font = QFont("Segoe UI", 8, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(font)
        painter.drawText(int(cx - 80), int(cy + radius * 0.95 + 8), 160, 20, Qt.AlignCenter, status_text)

        painter.end()


# ============================================================
# MAIN NEXUS UI WINDOW
# ============================================================

class NexusUI(QWidget):
    # Signals for inter-thread communication
    command_signal = Signal(str)
    response_signal = Signal(str)
    listening_signal = Signal()
    activity_signal = Signal(str)

    # New interactive signals for user text & controls
    text_input_signal = Signal(str)
    mic_toggle_signal = Signal(bool)
    stop_speaking_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NEXUS V1 — Neural Execution & Unified System")
        self.resize(1180, 760)
        self.setMinimumSize(950, 620)

        self.mic_active = True
        self.pulse = 0

        self._setup_styling()
        self._build_layout()
        self._connect_signals()

        # System telemetry timer (refreshes every 2 seconds without UI lag)
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self._refresh_system_stats)
        self.sys_timer.start(2000)

        # 24/7 Background System Tray setup
        self._setup_tray_icon()

    def _setup_tray_icon(self):
        """Setup Windows system tray icon so NEXUS can run 24/7 when closed."""
        try:
            if not QSystemTrayIcon.isSystemTrayAvailable():
                return
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor("#00e5ff"))
            self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self)
            self.tray_icon.setToolTip("NEXUS V1 — Autonomous AI Channel Manager (Active)")

            tray_menu = QMenu()
            show_action = tray_menu.addAction("🖥️ Open NEXUS")
            show_action.triggered.connect(self._show_window)

            tray_menu.addSeparator()
            exit_action = tray_menu.addAction("❌ Exit Completely")
            exit_action.triggered.connect(self._force_quit)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.show()
        except Exception:
            pass

    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._show_window()

    def _force_quit(self):
        QApplication.quit()

    def closeEvent(self, event):
        """Minimize to system tray instead of closing so background services stay on."""
        if hasattr(self, "tray_icon") and self.tray_icon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "NEXUS AI (24/7 Active)",
                "NEXUS is running silently in the background tray. Auto-Details is active!",
                QSystemTrayIcon.Information,
                2500
            )
        else:
            event.accept()

    # --------------------------------------------------------
    # STYLING (DARK HUD WITH NEON CYAN HIGHLIGHTS)
    # --------------------------------------------------------
    def _setup_styling(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #06090e;
                color: #dce7f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            /* SIDEBAR NAVIGATION */
            QFrame#sidebar {
                background-color: #090e17;
                border-right: 1px solid #132030;
            }
            QLabel#logoTitle {
                font-size: 24px;
                font-weight: 900;
                letter-spacing: 5px;
                color: #00e5ff;
            }
            QLabel#logoSubtitle {
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 2px;
                color: #637b99;
            }
            QPushButton.navButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 600;
                color: #8da4bf;
                text-align: left;
            }
            QPushButton.navButton:hover {
                background-color: #0f1826;
                color: #00e5ff;
                border: 1px solid #1a2f4a;
            }
            QPushButton.navButton:checked, QPushButton.navButton.active {
                background-color: #112238;
                color: #00e5ff;
                border: 1px solid #00e5ff;
            }

            /* TOP HUD BAR */
            QFrame#topBar {
                background-color: #090e17;
                border-bottom: 1px solid #132030;
                padding: 6px 16px;
            }
            QLabel#hudStatus {
                font-size: 12px;
                font-weight: 700;
                color: #00e5ff;
                letter-spacing: 1px;
            }
            QLabel#hudModelBadge {
                background-color: #0f1a29;
                border: 1px solid #1c324e;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
                color: #7dd3fc;
            }

            /* CONTENT PANELS */
            QFrame.hudPanel {
                background-color: #0a101a;
                border: 1px solid #142336;
                border-radius: 12px;
            }
            QLabel.panelHeader {
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 1.5px;
                color: #6da2db;
            }

            /* CHAT TRANSCRIPT */
            QTextBrowser#chatBrowser {
                background-color: #090e17;
                border: 1px solid #132030;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.6;
                color: #e2edff;
            }

            /* TIMELINE TICKER */
            QLabel#activityTicker {
                font-size: 12px;
                font-weight: 600;
                color: #00e5ff;
                background-color: #0a111c;
                border: 1px solid #15253b;
                border-radius: 6px;
                padding: 6px 12px;
            }

            /* INPUT DOCK */
            QLineEdit#textInput {
                background-color: #0a111c;
                border: 1px solid #182c44;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #ffffff;
            }
            QLineEdit#textInput:focus {
                border: 1px solid #00e5ff;
            }
            QPushButton#sendBtn {
                background-color: #0077b6;
                border: 1px solid #00b4d8;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: 700;
                color: #ffffff;
            }
            QPushButton#sendBtn:hover {
                background-color: #0096c7;
                border: 1px solid #00e5ff;
            }
            QPushButton.dockControlBtn {
                background-color: #0d1522;
                border: 1px solid #1d334e;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
                font-weight: 600;
                color: #8da4bf;
            }
            QPushButton.dockControlBtn:hover {
                border-color: #00e5ff;
                color: #00e5ff;
            }
            QPushButton.hudButton {
                background-color: #0f1929;
                border: 1px solid #1f3654;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 600;
                color: #94a3b8;
            }
            QPushButton.hudButton:hover {
                border-color: #00e5ff;
                color: #00e5ff;
                background-color: #132238;
            }
            QPushButton.hudButtonPrimary {
                background-color: #0077b6;
                border: 1px solid #00b4d8;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 700;
                color: #ffffff;
            }
            QPushButton.hudButtonPrimary:hover {
                background-color: #0096c7;
                border-color: #00e5ff;
            }

            /* TAB WIDGETS & TABLES */
            QTabWidget::pane {
                border: 1px solid #142336;
                background-color: #080d17;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #0b1320;
                color: #8da4bf;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #142336;
                font-weight: 600;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #112238;
                color: #00e5ff;
                border-bottom: 2px solid #00e5ff;
            }
            QTabBar::tab:hover {
                color: #e2edff;
            }
            QTableWidget {
                background-color: #090e17;
                border: 1px solid #132030;
                border-radius: 8px;
                gridline-color: #132030;
                color: #e2edff;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #132b47;
                color: #00e5ff;
            }
            QHeaderView::section {
                background-color: #0f1929;
                color: #7dd3fc;
                padding: 6px;
                font-weight: 700;
                font-size: 11px;
                border: 1px solid #132030;
            }
        """)

    # --------------------------------------------------------
    # BUILD LAYOUT & VIEWS
    # --------------------------------------------------------
    def _build_layout(self):
        main_h_layout = QHBoxLayout(self)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # 1. LEFT SIDEBAR
        sidebar = self._build_sidebar()
        main_h_layout.addWidget(sidebar)

        # 2. RIGHT WORKSPACE
        workspace = QWidget()
        ws_layout = QVBoxLayout(workspace)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        # Top HUD Bar
        top_bar = self._build_top_bar()
        ws_layout.addWidget(top_bar)

        # Center Stacked Views
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_chat_view())           # Index 0
        self.stack.addWidget(self._build_creator_studio_view()) # Index 1
        self.stack.addWidget(self._build_phone_view())          # Index 2
        self.stack.addWidget(self._build_cloud_view())          # Index 3
        self.stack.addWidget(self._build_missions_view())       # Index 4
        self.stack.addWidget(self._build_memory_view())         # Index 5
        self.stack.addWidget(self._build_research_view())       # Index 6
        self.stack.addWidget(self._build_system_view())         # Index 7
        self.stack.addWidget(self._build_settings_view())       # Index 8

        ws_layout.addWidget(self.stack)
        main_h_layout.addWidget(workspace)

    # --------------------------------------------------------
    # SIDEBAR COMPONENT
    # --------------------------------------------------------
    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(10)

        # Logo
        logo_title = QLabel("N E X U S")
        logo_title.setObjectName("logoTitle")
        logo_sub = QLabel("JARVIS SYSTEM V1")
        logo_sub.setObjectName("logoSubtitle")

        layout.addWidget(logo_title)
        layout.addWidget(logo_sub)
        layout.addSpacing(20)

        # Navigation Buttons
        self.nav_buttons = []
        nav_items = [
            ("💬  Chat", 0),
            ("🎬  Studio", 1),
            ("📱  Phone", 2),
            ("☁️  Cloud", 3),
            ("🎯  Missions", 4),
            ("🧠  Memory", 5),
            ("🌐  Research", 6),
            ("⚡  System", 7),
            ("⚙️  Settings", 8),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "navButton")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, idx=index: self._switch_nav(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom Status
        self.mic_badge = QLabel("● MIC ACTIVE")
        self.mic_badge.setStyleSheet("color: #00e5ff; font-size: 11px; font-weight: bold;")
        ver_label = QLabel("RELEASE: V1.0-STABLE")
        ver_label.setStyleSheet("color: #4b6382; font-size: 10px;")

        layout.addWidget(self.mic_badge)
        layout.addWidget(ver_label)

        return sidebar

    def _switch_nav(self, target_index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == target_index)
        self.stack.setCurrentIndex(target_index)
        if target_index == 2:
            self._refresh_phone_status()
        elif target_index == 3:
            self._refresh_cloud_status()
        elif target_index == 5:
            self._refresh_memory_view()
        elif target_index == 7:
            self._refresh_system_stats()

    # --------------------------------------------------------
    # TOP HUD BAR
    # --------------------------------------------------------
    def _build_top_bar(self):
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(50)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(14)

        self.status = QLabel("●  SYSTEM ONLINE")
        self.status.setObjectName("hudStatus")

        self.telemetry_badge = QLabel("CPU: --% | RAM: --% | GPU: RTX 4050")
        self.telemetry_badge.setStyleSheet(
            "color: #38bdf8; font-family: 'Consolas', monospace; font-size: 11px; "
            "background: rgba(15, 23, 42, 0.7); padding: 4px 10px; border-radius: 6px; "
            "border: 1px solid rgba(56, 189, 248, 0.25);"
        )

        model_badge = QLabel("HYBRID AI: GEMINI 3.8 + RTX 4050")
        model_badge.setObjectName("hudModelBadge")

        layout.addWidget(self.status)
        layout.addWidget(self.telemetry_badge)
        layout.addStretch()
        layout.addWidget(model_badge)

        return bar

    # --------------------------------------------------------
    # VIEW 0: CHAT & CORE (DEFAULT)
    # --------------------------------------------------------
    def _build_chat_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Center Container: Core on Left, Chat on Right
        center_row = QHBoxLayout()
        center_row.setSpacing(16)

        # Left Column: JARVIS Animated Core & Status
        core_panel = QFrame()
        core_panel.setProperty("class", "hudPanel")
        core_panel.setFixedWidth(280)

        core_layout = QVBoxLayout(core_panel)
        core_layout.setContentsMargins(14, 16, 14, 16)

        core_title = QLabel("AI NEURAL CORE")
        core_title.setProperty("class", "panelHeader")
        core_title.setAlignment(Qt.AlignCenter)

        self.core = JarvisCoreWidget(self)

        self.activity_status = QLabel("● IDLE / READY")
        self.activity_status.setStyleSheet("color: #00e5ff; font-weight: bold; font-size: 12px;")
        self.activity_status.setAlignment(Qt.AlignCenter)

        core_layout.addWidget(core_title)
        core_layout.addWidget(self.core, 1)
        core_layout.addWidget(self.activity_status)

        # JARVIS HUD COMPUTER CONTROL & VISION DOCK
        ctrl_box = QFrame()
        ctrl_box.setStyleSheet("background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 6px;")
        ctrl_layout = QVBoxLayout(ctrl_box)
        ctrl_layout.setContentsMargins(6, 6, 6, 6)
        ctrl_layout.setSpacing(6)

        ctrl_label = QLabel("JARVIS HUD CONTROLS")
        ctrl_label.setStyleSheet("color: #38bdf8; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        ctrl_label.setAlignment(Qt.AlignCenter)
        ctrl_layout.addWidget(ctrl_label)

        btn_see = QPushButton("👁️ WHAT DO YOU SEE?")
        btn_see.setProperty("class", "dockControlBtn")
        btn_see.setToolTip("Jarvis screen vision — observes active screen and summarizes")
        btn_see.clicked.connect(lambda: self._send_quick_command("what do you see"))

        btn_cam = QPushButton("📷 OPEN CAMERA")
        btn_cam.setProperty("class", "dockControlBtn")
        btn_cam.setToolTip("Opens camera feed with optical HUD reticle")
        btn_cam.clicked.connect(lambda: self._send_quick_command("open camera"))

        btn_ad = QPushButton("🎬 CREATE CINEMATIC AD")
        btn_ad.setProperty("class", "dockControlBtn")
        btn_ad.setToolTip("Generates Hollywood-grade commercial & AI video prompts from camera snapshot")
        btn_ad.clicked.connect(lambda: self._send_quick_command("create a cinematic ad"))

        btn_work = QPushButton("💼 SET EVERYTHING UP")
        btn_work.setProperty("class", "dockControlBtn")
        btn_work.setToolTip("One-click autonomous workspace macro: opens tabs, folders, and workspace")
        btn_work.clicked.connect(lambda: self._send_quick_command("set everything up"))

        ctrl_layout.addWidget(btn_see)
        ctrl_layout.addWidget(btn_cam)
        ctrl_layout.addWidget(btn_ad)
        ctrl_layout.addWidget(btn_work)

        core_layout.addWidget(ctrl_box)
        center_row.addWidget(core_panel)

        # Right Column: Chat Transcript & Feed
        chat_panel = QFrame()
        chat_panel.setProperty("class", "hudPanel")
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(14, 14, 14, 14)
        chat_layout.setSpacing(8)

        feed_title = QLabel("COMMUNICATIONS FEED")
        feed_title.setProperty("class", "panelHeader")

        self.chat_browser = QTextBrowser()
        self.chat_browser.setObjectName("chatBrowser")
        self.chat_browser.setHtml(
            "<div style='color: #637b99; font-size: 12px; margin-bottom: 8px;'>[SYSTEM INITIALIZED - AWAITING AUDIO OR TEXT COMMAND]</div>"
            "<div style='color: #38bdf8; font-size: 13px;'><b>NEXUS:</b> Systems are online, Sachin. Ready for your command.</div>"
        )

        chat_layout.addWidget(feed_title)
        chat_layout.addWidget(self.chat_browser, 1)
        center_row.addWidget(chat_panel, 1)

        # Rightmost Sidebar: JARVIS Cognitive Matrix & Live Telemetry (as seen in @dhaibuilds)
        right_panel = QFrame()
        right_panel.setProperty("class", "hudPanel")
        right_panel.setFixedWidth(230)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 14, 12, 14)
        right_layout.setSpacing(10)

        right_title = QLabel("COGNITIVE MATRIX")
        right_title.setProperty("class", "panelHeader")
        right_layout.addWidget(right_title)

        matrix_items = [
            ("UNDERSTAND", "● ACTIVE", "#00e5ff"),
            ("REASON", "● 60 FPS", "#38bdf8"),
            ("EXECUTE", "● AUTONOMOUS", "#10b981"),
            ("ADAPT", "● SELF-HEAL", "#a855f7"),
        ]
        for name, status, col in matrix_items:
            row = QHBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
            lbl_val = QLabel(status)
            lbl_val.setStyleSheet(f"color: {col}; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace;")
            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_val)
            right_layout.addLayout(row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(56, 189, 248, 0.2);")
        right_layout.addWidget(sep)

        telemetry_title = QLabel("HARDWARE GAUGES")
        telemetry_title.setProperty("class", "panelHeader")
        right_layout.addWidget(telemetry_title)

        self.gauge_cpu = QLabel("CPU: --")
        self.gauge_cpu.setStyleSheet("color: #7dd3fc; font-size: 11px; font-family: 'Consolas', monospace;")
        self.gauge_ram = QLabel("RAM: --")
        self.gauge_ram.setStyleSheet("color: #7dd3fc; font-size: 11px; font-family: 'Consolas', monospace;")
        self.gauge_gpu = QLabel("GPU: RTX 4050")
        self.gauge_gpu.setStyleSheet("color: #00e5ff; font-size: 11px; font-family: 'Consolas', monospace;")

        right_layout.addWidget(self.gauge_cpu)
        right_layout.addWidget(self.gauge_ram)
        right_layout.addWidget(self.gauge_gpu)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: rgba(56, 189, 248, 0.2);")
        right_layout.addWidget(sep2)

        cloud_head = QLabel("24/7 CLOUD & PWA")
        cloud_head.setProperty("class", "panelHeader")
        right_layout.addWidget(cloud_head)

        lbl_cloud_status = QLabel("● CLOUD NODE: ONLINE")
        lbl_cloud_status.setStyleSheet("color: #10b981; font-size: 10px; font-weight: bold;")
        lbl_pwa_link = QLabel("<a href='https://sachinnaik11.github.io/nexus/' style='color:#38bdf8; text-decoration:none;'>📱 Mobile PWA Live</a>")
        lbl_pwa_link.setOpenExternalLinks(True)
        lbl_pwa_link.setStyleSheet("font-size: 11px;")

        right_layout.addWidget(lbl_cloud_status)
        right_layout.addWidget(lbl_pwa_link)
        right_layout.addStretch()

        center_row.addWidget(right_panel)

        layout.addLayout(center_row, 1)

        # Activity Timeline Ticker
        self.activity_ticker = QLabel("● TIMELINE: SYSTEM ONLINE")
        self.activity_ticker.setObjectName("activityTicker")
        layout.addWidget(self.activity_ticker)

        # Hidden labels for 100% backward-compatibility with main.py references
        self.activity_log = QLabel()
        self.activity_log.setVisible(False)
        self.command = QLabel()
        self.command.setVisible(False)
        layout.addWidget(self.activity_log)
        layout.addWidget(self.command)

        # Bottom Input Dock
        dock = QHBoxLayout()
        dock.setSpacing(8)

        self.text_input = QLineEdit()
        self.text_input.setObjectName("textInput")
        self.text_input.setPlaceholderText("Ask or command NEXUS (e.g. 'open notepad', 'what time is it', 'remember I love Python')...")
        self.text_input.returnPressed.connect(self._handle_send_text)

        send_btn = QPushButton("SEND ↵")
        send_btn.setObjectName("sendBtn")
        send_btn.clicked.connect(self._handle_send_text)

        self.mic_btn = QPushButton("🎙️ MIC ON")
        self.mic_btn.setProperty("class", "dockControlBtn")
        self.mic_btn.clicked.connect(self._toggle_mic)

        stop_btn = QPushButton("⏹️ STOP")
        stop_btn.setProperty("class", "dockControlBtn")
        stop_btn.setToolTip("Stop speech output")
        stop_btn.clicked.connect(self._handle_stop_speech)

        dock.addWidget(self.text_input, 1)
        dock.addWidget(send_btn)
        dock.addWidget(self.mic_btn)
        dock.addWidget(stop_btn)

        layout.addLayout(dock)
        return page

    # --------------------------------------------------------
    # VIEW 1: MISSIONS VIEW
    # --------------------------------------------------------
    def _build_missions_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)

        header = QLabel("MISSION PLANNING & TASK EXECUTION")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        self.mission_browser = QTextBrowser()
        self.mission_browser.setObjectName("chatBrowser")
        self.mission_browser.setHtml(
            "<div style='color: #637b99;'>No active multi-step mission currently executing.</div>"
            "<p style='color: #7dd3fc;'>Try saying or typing: <i>'open notepad and then type hello world'</i> to start a mission.</p>"
        )
        layout.addWidget(self.mission_browser, 1)
        return page

    # --------------------------------------------------------
    # VIEW 2: MEMORY VIEW
    # --------------------------------------------------------
    def _build_memory_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)

        header = QLabel("PERMANENT KNOWLEDGE & FACT STORAGE")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        self.memory_browser = QTextBrowser()
        self.memory_browser.setObjectName("chatBrowser")
        self._refresh_memory_view()
        layout.addWidget(self.memory_browser, 1)
        return page

    def _refresh_memory_view(self):
        mem_file = os.path.join("memory", "memory.json")
        items_html = ""
        if os.path.exists(mem_file):
            try:
                import json
                with open(mem_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        for idx, item in enumerate(data, 1):
                            items_html += f"<div style='margin-bottom: 6px;'><span style='color:#00e5ff;'>[{idx}]</span> {item}</div>"
            except Exception:
                pass

        if not items_html:
            items_html = "<div style='color: #637b99;'>No memories stored yet. Tell NEXUS: <i>'remember that my name is Sachin'</i>.</div>"

        self.memory_browser.setHtml(
            f"<div style='font-size: 14px; font-weight: bold; color: #38bdf8; margin-bottom: 12px;'>SAVED KNOWLEDGE BASE</div>{items_html}"
        )

    # --------------------------------------------------------
    # VIEW 3: RESEARCH VIEW
    # --------------------------------------------------------
    def _build_research_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)

        header = QLabel("LIVE WEB RESEARCH & SOURCE ANALYSIS")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        self.research_browser = QTextBrowser()
        self.research_browser.setObjectName("chatBrowser")
        self.research_browser.setHtml(
            "<div style='color: #637b99;'>Web research logs will appear here when you request external facts or news.</div>"
            "<p style='color: #7dd3fc;'>Try asking: <i>'latest news on space exploration'</i> or <i>'who is the CEO of Google'</i>.</p>"
        )
        layout.addWidget(self.research_browser, 1)
        return page

    # --------------------------------------------------------
    # VIEW 4: SYSTEM MONITORING VIEW
    # --------------------------------------------------------
    def _build_system_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("SYSTEM STATUS & HARDWARE TELEMETRY")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        self.sys_info_browser = QTextBrowser()
        self.sys_info_browser.setObjectName("chatBrowser")
        self._refresh_system_stats()
        layout.addWidget(self.sys_info_browser, 1)
        return page

    def _refresh_system_stats(self):
        def worker():
            cpu_val = psutil.cpu_percent() if psutil else 0
            cpu_str = f"{cpu_val}%"
            ram_val = 0
            ram_str = "N/A"
            if psutil:
                try:
                    ram = psutil.virtual_memory()
                    ram_val = ram.percent
                    ram_str = f"{ram.percent}% ({round(ram.used / (1024**3), 1)}GB / {round(ram.total / (1024**3), 1)}GB)"
                except Exception:
                    pass

            gpu_str = "RTX 4050: Ready"
            try:
                import subprocess
                out = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
                    creationflags=0x08000000 if os.name == 'nt' else 0,
                    timeout=1.0
                ).decode().strip()
                parts = [p.strip() for p in out.split(",")]
                if len(parts) >= 2:
                    gpu_str = f"RTX 4050: {parts[0]}% ({parts[1]}°C)"
            except Exception:
                pass

            top_text = f"CPU: {cpu_str} | RAM: {ram_val}% | GPU: {gpu_str}"

            if hasattr(self, "telemetry_badge"):
                QMetaObject.invokeMethod(self.telemetry_badge, "setText", Qt.QueuedConnection, Q_ARG(str, top_text))
            if hasattr(self, "gauge_cpu"):
                QMetaObject.invokeMethod(self.gauge_cpu, "setText", Qt.QueuedConnection, Q_ARG(str, f"CPU: {cpu_str}"))
            if hasattr(self, "gauge_ram"):
                QMetaObject.invokeMethod(self.gauge_ram, "setText", Qt.QueuedConnection, Q_ARG(str, f"RAM: {ram_val}%"))
            if hasattr(self, "gauge_gpu"):
                QMetaObject.invokeMethod(self.gauge_gpu, "setText", Qt.QueuedConnection, Q_ARG(str, f"GPU: {gpu_str}"))

            if hasattr(self, "sys_info_browser"):
                html = f"""
                <div style='font-size: 14px; font-weight: bold; color: #38bdf8; margin-bottom: 12px;'>TELEMETRY READINGS</div>
                <table style='width: 100%; font-size: 13px; line-height: 2;'>
                    <tr><td style='color:#7dd3fc; width: 180px;'>CPU UTILIZATION:</td><td><b>{cpu_str}</b></td></tr>
                    <tr><td style='color:#7dd3fc;'>RAM UTILIZATION:</td><td><b>{ram_str}</b></td></tr>
                    <tr><td style='color:#7dd3fc;'>DEDICATED GPU:</td><td><b>{gpu_str} (6GB VRAM)</b></td></tr>
                    <tr><td style='color:#7dd3fc;'>HOST OS:</td><td>Windows 11 Native</td></tr>
                    <tr><td style='color:#7dd3fc;'>PYTHON RUNTIME:</td><td>{sys.version.split()[0]}</td></tr>
                    <tr><td style='color:#7dd3fc;'>GEMINI CLOUD AI:</td><td>Connected (gemini-3.8-flash)</td></tr>
                    <tr><td style='color:#7dd3fc;'>LOCAL OLLAMA AI:</td><td>Ready (qwen3:8b on RTX 4050)</td></tr>
                    <tr><td style='color:#7dd3fc;'>NEURAL SPEECH:</td><td>Microsoft Edge Neural TTS (en-GB-RyanNeural)</td></tr>
                </table>
                """
                QMetaObject.invokeMethod(self.sys_info_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))

        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------------------------------
    # VIEW 5: SETTINGS VIEW
    # --------------------------------------------------------
    def _build_settings_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)

        header = QLabel("SYSTEM CONFIGURATION & PREFERENCES")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        settings_browser = QTextBrowser()
        settings_browser.setObjectName("chatBrowser")
        settings_browser.setHtml("""
        <div style='font-size: 14px; font-weight: bold; color: #38bdf8; margin-bottom: 12px;'>CONFIGURED MODULES</div>
        <p><b>Primary AI Model:</b> Google Gemini 3.5 Flash Lite</p>
        <p><b>Local Fallback Model:</b> Ollama Qwen3:8b</p>
        <p><b>Default Language:</b> English (with native Indian multi-language detection)</p>
        <p><b>Voice Output:</b> System TTS (pyttsx3)</p>
        <p><b>Allowed PC Actions:</b> Application Launcher, Web Service Opener, Screenshot, Media Controls, Safe Typing</p>
        """)
        layout.addWidget(settings_browser, 1)
        return page

    # --------------------------------------------------------
    # VIEW 1: YOUTUBE CREATOR STUDIO — MEME CHANNEL WORKSPACE
    # --------------------------------------------------------
    def _build_creator_studio_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # 1. CHANNEL HEADER HUD
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        chan_title = QLabel("📺 MEMESWORLD21 // VIRAL COMEDY & SHORTS WORKSPACE")
        chan_title.setProperty("class", "panelHeader")
        chan_sub = QLabel("Target Audience: Young Adults (18–35) | Schedule: Daily @ 19:00 | Category: 23 Comedy")
        chan_sub.setStyleSheet("color: #64748b; font-size: 11px;")
        title_col.addWidget(chan_title)
        title_col.addWidget(chan_sub)
        header_row.addLayout(title_col)

        header_row.addStretch()

        btn_open_studio = QPushButton("🚀 YouTube Studio")
        btn_open_studio.setProperty("class", "hudButton")
        btn_open_studio.clicked.connect(lambda: self._execute_and_display("open youtube studio"))
        header_row.addWidget(btn_open_studio)

        btn_open_capcut = QPushButton("✂️ CapCut")
        btn_open_capcut.setProperty("class", "hudButton")
        btn_open_capcut.clicked.connect(lambda: self._execute_and_display("open capcut"))
        header_row.addWidget(btn_open_capcut)

        layout.addLayout(header_row)

        # 2. WORKSPACE TABBED INTERFACE
        self.studio_tabs = QTabWidget()
        self.studio_tabs.addTab(self._build_meme_dashboard_tab(), "📊 Dashboard")
        self.studio_tabs.addTab(self._build_meme_ideas_tab(), "💡 Research & Ideas")
        self.studio_tabs.addTab(self._build_meme_production_tab(), "🎬 Production Suite")
        self.studio_tabs.addTab(self._build_meme_calendar_tab(), "📅 Upload Calendar")
        self.studio_tabs.addTab(self._build_meme_analytics_tab(), "📈 Analytics & Review")
        self.studio_tabs.addTab(self._build_meme_settings_tab(), "⚙️ Channel Settings")

        layout.addWidget(self.studio_tabs, 1)
        return page

    # --------------------------------------------------------
    # SUB-TAB 1: MEME DASHBOARD
    # --------------------------------------------------------
    def _build_meme_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # KPI Cards Row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)

        from tools.meme_channel_db import meme_db
        summary = meme_db.get_dashboard_summary()
        pipeline = summary.get("pipeline", {})

        self.kpi_ideas = QLabel(f"💡 Ideas Stored: {summary.get('total_ideas', 0)}")
        self.kpi_ideas.setStyleSheet("background:#0f1929; border:1px solid #1e293b; border-radius:6px; padding:8px 12px; color:#38bdf8; font-weight:bold;")
        kpi_row.addWidget(self.kpi_ideas)

        self.kpi_pipeline = QLabel(f"🎬 Active: {pipeline.get('Scripting', 0)} Scripting | {pipeline.get('Editing', 0)} Editing | {pipeline.get('Ready', 0)} Ready")
        self.kpi_pipeline.setStyleSheet("background:#0f1929; border:1px solid #1e293b; border-radius:6px; padding:8px 12px; color:#00e5ff; font-weight:bold;")
        kpi_row.addWidget(self.kpi_pipeline)

        self.kpi_cadence = QLabel(f"⏰ Schedule: {summary.get('schedule', 'Daily')} @ 19:00")
        self.kpi_cadence.setStyleSheet("background:#0f1929; border:1px solid #1e293b; border-radius:6px; padding:8px 12px; color:#a78bfa; font-weight:bold;")
        kpi_row.addWidget(self.kpi_cadence)

        is_auto_on = meme_db.is_auto_details_enabled()
        self.kpi_auto = QLabel("🟢 Auto-Details: ACTIVE (24/7)" if is_auto_on else "⏸️ Auto-Details: PAUSED")
        self.kpi_auto.setStyleSheet(
            "background:#0f1929; border:1px solid #10b981; border-radius:6px; padding:8px 12px; color:#10b981; font-weight:bold;"
            if is_auto_on else
            "background:#0f1929; border:1px solid #64748b; border-radius:6px; padding:8px 12px; color:#94a3b8; font-weight:bold;"
        )
        kpi_row.addWidget(self.kpi_auto)

        kpi_row.addStretch()
        layout.addLayout(kpi_row)

        # Quick Actions Toolbar
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        btn_auto_opt = QPushButton("✍️ Add Details to Uploaded Video")
        btn_auto_opt.setProperty("class", "hudButtonPrimary")
        btn_auto_opt.setToolTip("Upload your edited video in YouTube Studio, then click here: NEXUS automatically adds the viral title, description, tags, and pinned comment!")
        btn_auto_opt.clicked.connect(self._handle_ui_auto_optimize)
        actions_row.addWidget(btn_auto_opt)

        btn_autofill = QPushButton("📋 Copy Details to Clipboard")
        btn_autofill.setProperty("class", "hudButton")
        btn_autofill.setToolTip("Primes clipboard with viral meme title, description, tags, and pinned comment for instant Ctrl+V into YouTube Studio")
        actions_row.addWidget(btn_autofill)
        btn_autofill.clicked.connect(self._handle_ui_studio_autofill)

        self.btn_watcher = QPushButton("🟢 Auto-Details: ON (24/7)" if is_auto_on else "🔄 Turn ON Auto-Details")
        self.btn_watcher.setProperty("class", "hudButton")
        if is_auto_on:
            self.btn_watcher.setStyleSheet("color: #10b981; border-color: #10b981; font-weight:bold;")
        self.btn_watcher.setToolTip("When ON, NEXUS monitors your YouTube channel 24/7 and automatically adds details to any newly uploaded video without you having to remember")
        self.btn_watcher.clicked.connect(self._handle_ui_toggle_watcher)
        actions_row.addWidget(self.btn_watcher)

        btn_render_and_upload = QPushButton("🚀 Full Auto: Render & Upload MP4")
        btn_render_and_upload.setProperty("class", "hudButton")
        btn_render_and_upload.setToolTip("Generates script, renders 1080x1920 MP4 with voiceover, and uploads to YouTube!")
        btn_render_and_upload.clicked.connect(self._handle_ui_auto_generate_and_upload)
        actions_row.addWidget(btn_render_and_upload)

        actions_row.addStretch()
        layout.addLayout(actions_row)

        # Topic entry row
        topic_row = QHBoxLayout()
        topic_row.setSpacing(8)

        self.yt_topic_input = QLineEdit()
        self.yt_topic_input.setObjectName("textInput")
        self.yt_topic_input.setPlaceholderText("Quick topic or angle (e.g. 'POV: You woke up thinking it was Sunday', 'Group chat drama')...")
        topic_row.addWidget(self.yt_topic_input, 1)

        btn_seo = QPushButton("🔥 Quick Viral SEO")
        btn_seo.setProperty("class", "hudButton")
        btn_seo.clicked.connect(self._handle_ui_viral_seo)
        topic_row.addWidget(btn_seo)

        layout.addLayout(topic_row)

        # Main Output Console Browser
        self.studio_browser = QTextBrowser()
        self.studio_browser.setObjectName("chatBrowser")
        self.studio_browser.setHtml(
            "<div style='color: #64748b; font-size: 13px;'>"
            "<b style='color:#00e5ff;'>Welcome to MemesWorld21 Personal Channel Manager</b><br><br>"
            "• <b>💡 Research & Ideas:</b> Discover verified internet trends, trending audio concepts, and track your ideas across the pipeline.<br>"
            "• <b>🎬 Production Suite:</b> Generate 3-second visual hooks, scene-by-scene storyboard, and CapCut editing instructions for any meme.<br>"
            "• <b>📅 Upload Calendar:</b> Plan upcoming uploads and configure your daily schedule.<br>"
            "• <b>📈 Analytics & Review:</b> View real API metrics, log verified manual stats (no fake data), and diagnose drop-offs."
            "</div>"
        )
        layout.addWidget(self.studio_browser, 1)
        return tab

    # --------------------------------------------------------
    # SUB-TAB 2: RESEARCH & IDEA PIPELINE (KANBAN TRACKER)
    # --------------------------------------------------------
    def _build_meme_ideas_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Trend Search Bar
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.research_theme_input = QLineEdit()
        self.research_theme_input.setObjectName("textInput")
        self.research_theme_input.setPlaceholderText("Search meme trends or sub-theme (e.g. 'Monday morning', 'Exams', 'Office struggles')...")
        search_row.addWidget(self.research_theme_input, 1)

        btn_search_trends = QPushButton("🔍 Research Viral Trends")
        btn_search_trends.setProperty("class", "hudButtonPrimary")
        btn_search_trends.clicked.connect(self._handle_ui_research_memes)
        search_row.addWidget(btn_search_trends)

        layout.addLayout(search_row)

        # Idea Board Table
        ideas_header = QLabel("SAVED MEME IDEAS & PIPELINE TRACKER")
        ideas_header.setProperty("class", "panelHeader")
        layout.addWidget(ideas_header)

        self.ideas_table = QTableWidget()
        self.ideas_table.setColumnCount(5)
        self.ideas_table.setHorizontalHeaderLabels(["ID", "Meme Concept / Title", "Format", "Priority", "Status"])
        self.ideas_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ideas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ideas_table.setSelectionMode(QTableWidget.SingleSelection)
        self.ideas_table.setFixedHeight(160)
        layout.addWidget(self.ideas_table)

        # Idea Add & Action Controls
        idea_ctrl_row = QHBoxLayout()
        idea_ctrl_row.setSpacing(8)

        self.new_idea_title_input = QLineEdit()
        self.new_idea_title_input.setObjectName("textInput")
        self.new_idea_title_input.setPlaceholderText("New meme idea title...")
        idea_ctrl_row.addWidget(self.new_idea_title_input, 1)

        self.new_idea_priority = QComboBox()
        self.new_idea_priority.addItems(["High", "Medium", "Low"])
        self.new_idea_priority.setStyleSheet("background:#0f1929; color:#e2edff; border:1px solid #1e293b; padding:6px; border-radius:6px;")
        idea_ctrl_row.addWidget(self.new_idea_priority)

        btn_add_idea = QPushButton("➕ Save Idea")
        btn_add_idea.setProperty("class", "hudButton")
        btn_add_idea.clicked.connect(self._handle_ui_add_idea)
        idea_ctrl_row.addWidget(btn_add_idea)

        btn_send_prod = QPushButton("🎬 Send to Production")
        btn_send_prod.setProperty("class", "hudButtonPrimary")
        btn_send_prod.clicked.connect(self._handle_ui_send_to_production)
        idea_ctrl_row.addWidget(btn_send_prod)

        btn_del_idea = QPushButton("🗑️ Delete")
        btn_del_idea.setProperty("class", "hudButton")
        btn_del_idea.clicked.connect(self._handle_ui_delete_idea)
        idea_ctrl_row.addWidget(btn_del_idea)

        layout.addLayout(idea_ctrl_row)

        # Output Browser for Research Findings
        self.research_browser = QTextBrowser()
        self.research_browser.setObjectName("chatBrowser")
        self.research_browser.setHtml("<div style='color:#64748b;'>Enter a theme above and click <b>Research Viral Trends</b> to analyze trending formats with Gemini 3.5.</div>")
        layout.addWidget(self.research_browser, 1)

        self._refresh_ideas_table()
        return tab

    def _refresh_ideas_table(self):
        from tools.meme_channel_db import meme_db
        ideas = meme_db.get_ideas()
        self.ideas_table.setRowCount(len(ideas))
        for row, idea in enumerate(ideas):
            self.ideas_table.setItem(row, 0, QTableWidgetItem(idea.get("id", "")))
            self.ideas_table.setItem(row, 1, QTableWidgetItem(idea.get("title", "")))
            self.ideas_table.setItem(row, 2, QTableWidgetItem(idea.get("format", "Shorts")))
            self.ideas_table.setItem(row, 3, QTableWidgetItem(idea.get("priority", "Medium")))
            self.ideas_table.setItem(row, 4, QTableWidgetItem(idea.get("status", "Planned")))

    def _handle_ui_research_memes(self):
        theme = self.research_theme_input.text().strip() or None
        self.research_browser.setHtml("<div style='color:#00e5ff;'><b>🔍 Scouring live web and analyzing meme trends with Gemini 3.5...</b></div>")

        def worker():
            from tools.meme_researcher import meme_researcher
            res = meme_researcher.research_trending_memes(theme)
            report = res.get("report_markdown", "No report generated.")
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>MEME TREND RESEARCH: {res.get('theme', '').upper()}</div><pre style='color:#e2edff; font-family:Consolas, monospace; white-space:pre-wrap;'>{report}</pre>"
            QMetaObject.invokeMethod(self.research_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_add_idea(self):
        title = self.new_idea_title_input.text().strip()
        if not title:
            return
        priority = self.new_idea_priority.currentText()
        from tools.meme_channel_db import meme_db
        meme_db.add_idea(title=title, priority=priority, status="Planned")
        self.new_idea_title_input.clear()
        self._refresh_ideas_table()
        self._refresh_dashboard_kpis()

    def _handle_ui_delete_idea(self):
        row = self.ideas_table.currentRow()
        if row >= 0:
            idea_id = self.ideas_table.item(row, 0).text()
            from tools.meme_channel_db import meme_db
            meme_db.delete_idea(idea_id)
            self._refresh_ideas_table()
            self._refresh_dashboard_kpis()

    def _handle_ui_send_to_production(self):
        row = self.ideas_table.currentRow()
        if row >= 0:
            idea_title = self.ideas_table.item(row, 1).text()
            self.prod_concept_input.setText(idea_title)
            self.studio_tabs.setCurrentIndex(2) # Switch to Production Suite tab
            self._handle_ui_generate_production()

    # --------------------------------------------------------
    # SUB-TAB 3: VIDEO PRODUCTION SUITE
    # --------------------------------------------------------
    def _build_meme_production_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Concept inputs
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.prod_concept_input = QLineEdit()
        self.prod_concept_input.setObjectName("textInput")
        self.prod_concept_input.setPlaceholderText("Enter meme concept or select an idea from Idea Board...")
        input_row.addWidget(self.prod_concept_input, 1)

        self.prod_notes_input = QLineEdit()
        self.prod_notes_input.setObjectName("textInput")
        self.prod_notes_input.setPlaceholderText("Optional creator notes (e.g. 'Use Vine boom at punchline')...")
        input_row.addWidget(self.prod_notes_input, 1)

        layout.addLayout(input_row)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_gen_package = QPushButton("🪄 Generate Full Production Package")
        btn_gen_package.setProperty("class", "hudButtonPrimary")
        btn_gen_package.setToolTip("Creates 3-second hook, scene-by-scene storyboard, CapCut editing instructions, titles, and checklist")
        btn_gen_package.clicked.connect(self._handle_ui_generate_production)
        btn_row.addWidget(btn_gen_package)

        btn_render_mp4 = QPushButton("🎬 Render 1080x1920 MP4 Video")
        btn_render_mp4.setProperty("class", "hudButton")
        btn_render_mp4.setToolTip("Synthesizes real MP4 Shorts video with voiceover using FFMPEG")
        btn_render_mp4.clicked.connect(self._handle_ui_render_production_video)
        btn_row.addWidget(btn_render_mp4)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Production Output Browser
        self.production_browser = QTextBrowser()
        self.production_browser.setObjectName("chatBrowser")
        self.production_browser.setHtml(
            "<div style='color:#64748b;'>"
            "Select an idea or enter a concept above and click <b>Generate Full Production Package</b>.<br><br>"
            "NEXUS will generate the complete 3-second retention hook, timestamped storyboard, CapCut editing guide, titles, and upload checklist."
            "</div>"
        )
        layout.addWidget(self.production_browser, 1)
        return tab

    def _handle_ui_generate_production(self):
        concept = self.prod_concept_input.text().strip() or "POV: When you wake up thinking it's Sunday but it's Monday 7:55 AM"
        notes = self.prod_notes_input.text().strip() or None
        self.production_browser.setHtml(f"<div style='color:#00e5ff;'><b>🪄 Drafting full production blueprint for '{concept}' with Gemini 3.5...</b></div>")

        def worker():
            from tools.meme_production import meme_production
            res = meme_production.generate_full_production_package(concept, notes)
            pkg = res.get("production_package", "No package generated.")
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>PRODUCTION BLUEPRINT: {concept.upper()}</div><pre style='color:#e2edff; font-family:Consolas, monospace; white-space:pre-wrap;'>{pkg}</pre>"
            QMetaObject.invokeMethod(self.production_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_render_production_video(self):
        concept = self.prod_concept_input.text().strip() or "Relatable Moment"
        self.production_browser.setHtml(f"<div style='color:#00e5ff;'><b>🎬 Synthesizing voiceover & compiling 1080x1920 MP4 video for '{concept}'...</b></div>")

        def worker():
            from tools.meme_production import meme_production
            res = meme_production.render_video_for_concept(concept)
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>RENDER RESULT</div><pre style='color:#e2edff; font-family:Consolas, monospace; white-space:pre-wrap;'>{res}</pre>"
            QMetaObject.invokeMethod(self.production_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------------------------------
    # SUB-TAB 4: UPLOAD CALENDAR & REMINDERS
    # --------------------------------------------------------
    def _build_meme_calendar_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header info
        sched_banner = QLabel("TARGET CADENCE: DAILY AT 19:00 (7:00 PM IST) // MEMESWORLD21")
        sched_banner.setStyleSheet("color:#38bdf8; font-weight:bold; font-size:12px; background:#0f1929; border:1px solid #1e293b; padding:8px 12px; border-radius:6px;")
        layout.addWidget(sched_banner)

        # Schedule new upload form
        form_row = QHBoxLayout()
        form_row.setSpacing(8)

        self.cal_date_input = QLineEdit()
        self.cal_date_input.setObjectName("textInput")
        self.cal_date_input.setPlaceholderText("Date (YYYY-MM-DD)...")
        self.cal_date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        self.cal_date_input.setFixedWidth(130)
        form_row.addWidget(self.cal_date_input)

        self.cal_time_input = QLineEdit()
        self.cal_time_input.setObjectName("textInput")
        self.cal_time_input.setText("19:00")
        self.cal_time_input.setFixedWidth(80)
        form_row.addWidget(self.cal_time_input)

        self.cal_title_input = QLineEdit()
        self.cal_title_input.setObjectName("textInput")
        self.cal_title_input.setPlaceholderText("Scheduled meme video title...")
        form_row.addWidget(self.cal_title_input, 1)

        btn_add_cal = QPushButton("📅 Schedule Upload")
        btn_add_cal.setProperty("class", "hudButtonPrimary")
        btn_add_cal.clicked.connect(self._handle_ui_schedule_upload)
        form_row.addWidget(btn_add_cal)

        btn_reminder = QPushButton("⏰ Check Reminder")
        btn_reminder.setProperty("class", "hudButton")
        btn_reminder.clicked.connect(lambda: self._execute_and_display("check upload reminder"))
        form_row.addWidget(btn_reminder)

        layout.addLayout(form_row)

        # Calendar Output Browser
        self.calendar_browser = QTextBrowser()
        self.calendar_browser.setObjectName("chatBrowser")
        layout.addWidget(self.calendar_browser, 1)

        self._refresh_calendar_browser()
        return tab

    def _refresh_calendar_browser(self):
        from tools.meme_channel_db import meme_db
        cal = meme_db.get_calendar()
        html = "<div style='font-size:14px; font-weight:bold; color:#38bdf8; margin-bottom:10px;'>UPCOMING & SCHEDULED UPLOADS</div>"
        if cal:
            for item in cal:
                html += f"<div style='margin-bottom:8px; background:#0b1320; padding:8px 12px; border-radius:6px; border:1px solid #1e293b;'>"
                html += f"<span style='color:#00e5ff; font-weight:bold;'>[{item.get('date')} @ {item.get('time')}]</span> "
                html += f"<span style='color:#e2edff;'>{item.get('title')}</span> "
                html += f"<span style='color:#94a3b8; font-size:11px;'>({item.get('status', 'Scheduled')})</span>"
                html += "</div>"
        else:
            html += "<div style='color:#64748b;'>No upcoming uploads scheduled. Add one above!</div>"
        self.calendar_browser.setHtml(html)

    def _handle_ui_schedule_upload(self):
        date_str = self.cal_date_input.text().strip()
        time_str = self.cal_time_input.text().strip() or "19:00"
        title = self.cal_title_input.text().strip()
        if not title:
            return
        from tools.meme_channel_db import meme_db
        meme_db.schedule_upload(date_str, time_str, title)
        self.cal_title_input.clear()
        self._refresh_calendar_browser()
        self._refresh_dashboard_kpis()

    # --------------------------------------------------------
    # SUB-TAB 5: ANALYTICS & REVIEW
    # --------------------------------------------------------
    def _build_meme_analytics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Live API bar
        api_row = QHBoxLayout()
        api_row.setSpacing(8)

        btn_live_api = QPushButton("🔄 Query Live YouTube API Stats")
        btn_live_api.setProperty("class", "hudButtonPrimary")
        btn_live_api.clicked.connect(self._handle_ui_fetch_live_stats)
        api_row.addWidget(btn_live_api)

        api_row.addStretch()
        layout.addLayout(api_row)

        # Manual Entry Form
        entry_header = QLabel("LOG VERIFIED VIDEO PERFORMANCE (ZERO FAKE DATA)")
        entry_header.setProperty("class", "panelHeader")
        layout.addWidget(entry_header)

        form_grid = QHBoxLayout()
        form_grid.setSpacing(8)

        self.metric_title_input = QLineEdit()
        self.metric_title_input.setObjectName("textInput")
        self.metric_title_input.setPlaceholderText("Video title...")
        form_grid.addWidget(self.metric_title_input, 2)

        self.metric_views_input = QLineEdit()
        self.metric_views_input.setObjectName("textInput")
        self.metric_views_input.setPlaceholderText("Views...")
        self.metric_views_input.setFixedWidth(80)
        form_grid.addWidget(self.metric_views_input)

        self.metric_likes_input = QLineEdit()
        self.metric_likes_input.setObjectName("textInput")
        self.metric_likes_input.setPlaceholderText("Likes...")
        self.metric_likes_input.setFixedWidth(80)
        form_grid.addWidget(self.metric_likes_input)

        self.metric_comments_input = QLineEdit()
        self.metric_comments_input.setObjectName("textInput")
        self.metric_comments_input.setPlaceholderText("Comments...")
        self.metric_comments_input.setFixedWidth(80)
        form_grid.addWidget(self.metric_comments_input)

        self.metric_retention_input = QLineEdit()
        self.metric_retention_input.setObjectName("textInput")
        self.metric_retention_input.setPlaceholderText("Retention % (e.g. 105)...")
        self.metric_retention_input.setFixedWidth(130)
        form_grid.addWidget(self.metric_retention_input)

        layout.addLayout(form_grid)

        # Review action buttons
        review_btn_row = QHBoxLayout()
        review_btn_row.setSpacing(8)

        btn_save_metrics = QPushButton("💾 Save Verified Metrics")
        btn_save_metrics.setProperty("class", "hudButton")
        btn_save_metrics.clicked.connect(self._handle_ui_save_metrics)
        review_btn_row.addWidget(btn_save_metrics)

        btn_run_audit = QPushButton("🔬 Run AI Performance Audit & A/B Test")
        btn_run_audit.setProperty("class", "hudButtonPrimary")
        btn_run_audit.clicked.connect(self._handle_ui_run_audit)
        review_btn_row.addWidget(btn_run_audit)

        review_btn_row.addStretch()
        layout.addLayout(review_btn_row)

        # Analytics Browser
        self.analytics_browser = QTextBrowser()
        self.analytics_browser.setObjectName("chatBrowser")
        layout.addWidget(self.analytics_browser, 1)

        self._refresh_analytics_browser()
        return tab

    def _refresh_analytics_browser(self):
        from tools.meme_channel_db import meme_db
        history = meme_db.get_analytics_logs()
        html = "<div style='font-size:14px; font-weight:bold; color:#38bdf8; margin-bottom:10px;'>VERIFIED PERFORMANCE LOGS</div>"
        if history:
            for item in history:
                html += f"<div style='margin-bottom:8px; background:#0b1320; padding:8px 12px; border-radius:6px; border:1px solid #1e293b;'>"
                html += f"<b style='color:#e2edff;'>{item.get('title')}</b><br>"
                html += f"<span style='color:#00e5ff;'>👁️ Views: {item.get('views', 0):,}</span> | "
                html += f"<span style='color:#ec4899;'>❤️ Likes: {item.get('likes', 0):,}</span> | "
                html += f"<span style='color:#a78bfa;'>💬 Comments: {item.get('comments', 0):,}</span> | "
                html += f"<span style='color:#10b981;'>📈 Retention: {item.get('retention_percent', 0)}%</span> "
                html += f"<span style='color:#64748b; font-size:11px;'>({item.get('source')})</span>"
                html += "</div>"
        else:
            html += "<div style='color:#64748b;'>No performance logs recorded yet. Query YouTube API or log your metrics above.</div>"
        self.analytics_browser.setHtml(html)

    def _handle_ui_fetch_live_stats(self):
        self.analytics_browser.setHtml("<div style='color:#00e5ff;'><b>🔄 Querying official YouTube Data API v3...</b></div>")

        def worker():
            from tools.meme_analytics import meme_analytics
            stats = meme_analytics.fetch_live_channel_stats()
            if stats.get("connected"):
                html = (
                    f"<div style='color:#38bdf8; font-weight:bold; font-size:14px;'>OFFICIAL YOUTUBE CHANNEL METRICS</div>"
                    f"<p>Channel: <b>{stats.get('title')}</b></p>"
                    f"<p>Subscribers: <b style='color:#00e5ff;'>{stats.get('subscribers', 0):,}</b></p>"
                    f"<p>Total Views: <b>{stats.get('views', 0):,}</b></p>"
                    f"<p>Public Videos: <b>{stats.get('video_count', 0):,}</b></p>"
                )
            else:
                html = f"<div style='color:#f59e0b;'><b>API Status:</b> {stats.get('message')}</div>"
            QMetaObject.invokeMethod(self.analytics_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_save_metrics(self):
        title = self.metric_title_input.text().strip()
        views = int(self.metric_views_input.text().strip() or "0")
        likes = int(self.metric_likes_input.text().strip() or "0")
        comments = int(self.metric_comments_input.text().strip() or "0")
        retention = float(self.metric_retention_input.text().strip() or "0.0")
        if not title:
            return
        from tools.meme_analytics import meme_analytics
        meme_analytics.record_manual_metrics(title, views, likes, comments, retention)
        self._refresh_analytics_browser()
        self._refresh_dashboard_kpis()

    def _handle_ui_run_audit(self):
        title = self.metric_title_input.text().strip() or "Sample Meme Video"
        views = int(self.metric_views_input.text().strip() or "1000")
        likes = int(self.metric_likes_input.text().strip() or "80")
        comments = int(self.metric_comments_input.text().strip() or "10")
        retention = float(self.metric_retention_input.text().strip() or "95.0")
        self.analytics_browser.setHtml("<div style='color:#00e5ff;'><b>🔬 Running AI Performance Diagnostic & A/B Test Formulation...</b></div>")

        def worker():
            from tools.meme_analytics import meme_analytics
            audit = meme_analytics.diagnose_video_performance(title, views, likes, comments, retention)
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>DIAGNOSTIC AUDIT: {title.upper()}</div><pre style='color:#e2edff; font-family:Consolas, monospace; white-space:pre-wrap;'>{audit}</pre>"
            QMetaObject.invokeMethod(self.analytics_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------------------------------
    # SUB-TAB 6: CHANNEL SETTINGS & AUTH
    # --------------------------------------------------------
    def _build_meme_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("CHANNEL PROFILE & YOUTUBE CONNECTION (MEMESWORLD21)")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        settings_text = QTextBrowser()
        settings_text.setObjectName("chatBrowser")
        settings_text.setHtml("""
        <div style='color: #e2edff; line-height: 1.6;'>
        <b style='color:#38bdf8; font-size:14px;'>CHANNEL PROFILE:</b>
        <p>• <b>Channel Name:</b> MemesWorld21<br>
        • <b>Handle:</b> @MemesWorld21<br>
        • <b>Niche:</b> Viral Memes & Relatable Comedy<br>
        • <b>Target Audience:</b> Young adults (18–35), college students, desk workers<br>
        • <b>Content Format:</b> Fast-cut POV Shorts (8–15s), situational comedy<br>
        • <b>Upload Cadence:</b> Daily at 19:00 (7:00 PM IST)</p>

        <b style='color:#38bdf8; font-size:14px;'>GOOGLE OAUTH2 & API CONNECTION:</b>
        <p>To enable direct 1-click video publishing without opening browser tabs:<br>
        1. Open your <code>.env</code> file.<br>
        2. Set <code>YOUTUBE_ACCESS_TOKEN="ya29.a0..."</code>.<br>
        3. NEXUS uses official Google OAuth2 tokens only — never enter your account password.</p>

        <b style='color:#38bdf8; font-size:14px;'>HUMAN-IN-THE-LOOP SAFETY:</b>
        <p>• All publishing actions require your explicit permission.<br>
        • NEXUS will never delete videos or modify public channel settings without your authorization.</p>
        </div>
        """)
        layout.addWidget(settings_text, 1)
        return tab

    def _refresh_dashboard_kpis(self):
        from tools.meme_channel_db import meme_db
        summary = meme_db.get_dashboard_summary()
        pipeline = summary.get("pipeline", {})
        self.kpi_ideas.setText(f"💡 Ideas Stored: {summary.get('total_ideas', 0)}")
        self.kpi_pipeline.setText(f"🎬 Active: {pipeline.get('Scripting', 0)} Scripting | {pipeline.get('Editing', 0)} Editing | {pipeline.get('Ready', 0)} Ready")
        self.kpi_cadence.setText(f"⏰ Schedule: {summary.get('schedule', 'Daily')} @ 19:00")
        is_auto_on = meme_db.is_auto_details_enabled()
        if hasattr(self, "kpi_auto"):
            self.kpi_auto.setText("🟢 Auto-Details: ACTIVE (24/7)" if is_auto_on else "⏸️ Auto-Details: PAUSED")
            self.kpi_auto.setStyleSheet(
                "background:#0f1929; border:1px solid #10b981; border-radius:6px; padding:8px 12px; color:#10b981; font-weight:bold;"
                if is_auto_on else
                "background:#0f1929; border:1px solid #64748b; border-radius:6px; padding:8px 12px; color:#94a3b8; font-weight:bold;"
            )

    # --------------------------------------------------------
    # LEGACY / BACKWARD-COMPATIBLE ACTION HANDLERS
    # --------------------------------------------------------
    def _handle_ui_auto_generate_and_upload(self):
        topic = self.yt_topic_input.text().strip() or None
        self.studio_browser.setHtml(
            "<div style='color: #00e5ff;'><b>🚀 AUTONOMOUS MEME PIPELINE ACTIVATED!</b><br><br>"
            "1. 🧠 Gemini 3.5 is crafting a viral relatable meme script...<br>"
            "2. 🎙️ pyttsx3 is synthesizing comedic audio voiceover...<br>"
            "3. 🎨 Rendering 1080x1920 vertical 9:16 Shorts visual frame...<br>"
            "4. 🎬 FFMPEG is encoding high-definition MP4 video...<br>"
            "5. 📺 Uploading video to your YouTube channel...<br>"
            "<span style='color: #94a3b8; font-size: 11px;'>Please wait ~5-10 seconds while the pipeline executes...</span></div>"
        )
        self.set_activity("CREATING & UPLOADING MEME VIDEO...")

        def worker():
            from tools.meme_generator import meme_uploader
            res = meme_uploader.auto_generate_and_upload(topic)
            html = (
                f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>"
                f"AUTONOMOUS GENERATION & UPLOAD RESULT</div>"
                f"<pre style='color:#e2edff; font-family: Consolas, monospace; white-space: pre-wrap;'>{res}</pre>"
            )
            QMetaObject.invokeMethod(self.studio_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
            self.set_activity("MEME VIDEO PIPELINE COMPLETE")

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_auto_optimize(self):
        topic = self.yt_topic_input.text().strip() or None
        self.studio_browser.setHtml(
            "<div style='color: #00e5ff;'><b>✍️ NEXUS is fetching your latest uploaded video and adding viral details...</b><br>"
            "<span style='color: #94a3b8;'>Querying YouTube API, applying viral meme algorithms, drafting high-CTR title, description, tags, and pinned comment...</span></div>"
        )
        self.set_activity("ADDING DETAILS TO VIDEO...")

        def worker():
            from tools.youtube_automation import youtube_automator
            res = youtube_automator.auto_optimize_latest_video(topic)
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>AUTONOMOUS VIDEO DETAILS ADDED</div><pre style='color:#e2edff; font-family: Consolas, monospace; white-space: pre-wrap;'>{res}</pre>"
            QMetaObject.invokeMethod(self.studio_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
            self.set_activity("VIDEO DETAILS READY")

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_studio_autofill(self):
        topic = self.yt_topic_input.text().strip() or None
        self.studio_browser.setHtml(
            "<div style='color: #00e5ff;'><b>⚡ Generating viral meme metadata & preparing clipboard auto-fill...</b></div>"
        )
        self.set_activity("PREPARING STUDIO AUTO-FILL...")

        def worker():
            from tools.youtube_automation import youtube_automator
            res = youtube_automator.autofill_studio_browser(topic)
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>STUDIO BROWSER AUTO-FILL</div><pre style='color:#e2edff; font-family: Consolas, monospace; white-space: pre-wrap;'>{res}</pre>"
            QMetaObject.invokeMethod(self.studio_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
            self.set_activity("AUTO-FILL READY IN CLIPBOARD")

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_toggle_watcher(self):
        from tools.youtube_automation import youtube_automator
        from tools.meme_channel_db import meme_db
        if not youtube_automator.watcher_running:
            res = youtube_automator.start_channel_watcher()
            self.btn_watcher.setText("🟢 Auto-Details: ON (24/7)")
            self.btn_watcher.setStyleSheet("color: #10b981; border-color: #10b981; font-weight:bold;")
            if hasattr(self, "kpi_auto"):
                self.kpi_auto.setText("🟢 Auto-Details: ACTIVE (24/7)")
                self.kpi_auto.setStyleSheet("background:#0f1929; border:1px solid #10b981; border-radius:6px; padding:8px 12px; color:#10b981; font-weight:bold;")
        else:
            res = youtube_automator.stop_channel_watcher()
            self.btn_watcher.setText("🔄 Turn ON Auto-Details")
            self.btn_watcher.setStyleSheet("")
            if hasattr(self, "kpi_auto"):
                self.kpi_auto.setText("⏸️ Auto-Details: PAUSED")
                self.kpi_auto.setStyleSheet("background:#0f1929; border:1px solid #64748b; border-radius:6px; padding:8px 12px; color:#94a3b8; font-weight:bold;")
        self.studio_browser.append(f"<p style='color:#00e5ff;'><b>Auto-Details Status:</b> {res}</p>")

    def _handle_ui_viral_seo(self):
        topic = self.yt_topic_input.text().strip() or "trending viral memes"
        self.studio_browser.setHtml(f"<div style='color: #00e5ff;'><b>⚡ NEXUS is generating viral meme SEO package for '{topic}' using Gemini 3.5...</b></div>")

        def worker():
            from tools.youtube_manager import generate_viral_seo
            res = generate_viral_seo(topic)
            pkg = res.get("seo_package", "No output generated.")
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>VIRAL MEME SEO: {topic.upper()}</div><pre style='color:#e2edff; font-family: Consolas, monospace; white-space: pre-wrap;'>{pkg}</pre>"
            QMetaObject.invokeMethod(self.studio_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_meme_short(self):
        self.studio_browser.setHtml("<div style='color: #00e5ff;'><b>🎭 Generating autonomous niche meme short plan & vertical visual card...</b></div>")

        def worker():
            from tools.youtube_manager import generate_niche_meme_short
            res = generate_niche_meme_short()
            plan = res.get("meme_plan", "No plan generated.")
            asset = res.get("image_asset")
            html = f"<div style='color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:8px;'>MEME SHORT PLAN ({res.get('niche', 'Viral Memes & Relatable Comedy')})</div><pre style='color:#e2edff; font-family: Consolas, monospace; white-space: pre-wrap;'>{plan}</pre>"
            if asset:
                html += f"<p style='color:#00e5ff;'><b>Visual Card Created:</b> {asset}</p>"
            QMetaObject.invokeMethod(self.studio_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))

        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------------------------------
    # VIEW 2: ANDROID PHONE CONTROLLER VIEW
    # --------------------------------------------------------
    def _build_phone_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QLabel("ANDROID PHONE HARDWARE & SYSTEM CONTROL (ADB)")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        # Status & Wi-Fi row
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self.phone_status_label = QLabel("● PHONE STATUS: CHECKING...")
        self.phone_status_label.setStyleSheet("color: #00e5ff; font-weight: bold; font-size: 13px;")
        status_row.addWidget(self.phone_status_label)

        status_row.addStretch()

        self.wifi_ip_input = QLineEdit()
        self.wifi_ip_input.setObjectName("textInput")
        self.wifi_ip_input.setPlaceholderText("Phone IP (e.g. 192.168.1.5)")
        self.wifi_ip_input.setFixedWidth(180)
        status_row.addWidget(self.wifi_ip_input)

        btn_connect = QPushButton("📶 Connect Wi-Fi")
        btn_connect.setProperty("class", "hudButton")
        btn_connect.clicked.connect(self._handle_ui_connect_phone_wifi)
        status_row.addWidget(btn_connect)

        layout.addLayout(status_row)

        # Hardware action buttons row
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(8)

        btn_battery = QPushButton("🔋 Battery Status")
        btn_battery.setProperty("class", "hudButton")
        btn_battery.clicked.connect(lambda: self._execute_and_display("phone battery"))
        btn_row1.addWidget(btn_battery)

        btn_shot = QPushButton("📸 Take Screenshot")
        btn_shot.setProperty("class", "hudButton")
        btn_shot.clicked.connect(lambda: self._execute_and_display("phone screenshot"))
        btn_row1.addWidget(btn_shot)

        btn_lock = QPushButton("🔒 Lock Screen")
        btn_lock.setProperty("class", "hudButton")
        btn_lock.clicked.connect(lambda: self._execute_and_display("lock phone"))
        btn_row1.addWidget(btn_lock)

        btn_vol_up = QPushButton("🔊 Vol +")
        btn_vol_up.setProperty("class", "hudButton")
        btn_vol_up.clicked.connect(lambda: self._execute_and_display("phone volume up"))
        btn_row1.addWidget(btn_vol_up)

        btn_vol_dn = QPushButton("🔉 Vol -")
        btn_vol_dn.setProperty("class", "hudButton")
        btn_vol_dn.clicked.connect(lambda: self._execute_and_display("phone volume down"))
        btn_row1.addWidget(btn_vol_dn)

        btn_row1.addStretch()
        layout.addLayout(btn_row1)

        # App Launch Row
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(8)

        btn_yt = QPushButton("▶️ YouTube")
        btn_yt.setProperty("class", "hudButton")
        btn_yt.clicked.connect(lambda: self._execute_and_display("open on phone youtube"))
        btn_row2.addWidget(btn_yt)

        btn_wa = QPushButton("💬 WhatsApp")
        btn_wa.setProperty("class", "hudButton")
        btn_wa.clicked.connect(lambda: self._execute_and_display("open on phone whatsapp"))
        btn_row2.addWidget(btn_wa)

        btn_chrome = QPushButton("🌐 Chrome")
        btn_chrome.setProperty("class", "hudButton")
        btn_chrome.clicked.connect(lambda: self._execute_and_display("open on phone chrome"))
        btn_row2.addWidget(btn_chrome)

        btn_cam = QPushButton("📷 Camera")
        btn_cam.setProperty("class", "hudButton")
        btn_cam.clicked.connect(lambda: self._execute_and_display("open on phone camera"))
        btn_row2.addWidget(btn_cam)

        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.setProperty("class", "hudButton")
        btn_settings.clicked.connect(lambda: self._execute_and_display("open on phone settings"))
        btn_row2.addWidget(btn_settings)

        btn_row2.addStretch()
        layout.addLayout(btn_row2)

        # Phone Feed Browser
        self.phone_browser = QTextBrowser()
        self.phone_browser.setObjectName("chatBrowser")
        self.phone_browser.setHtml(
            "<div style='color: #637b99; font-size: 13px;'>"
            "NEXUS Android Bridge is ready. Connect your phone via USB with USB Debugging enabled, or enter your phone's Wi-Fi IP above to control wirelessly without cables!"
            "</div>"
        )
        layout.addWidget(self.phone_browser, 1)
        return page

    def _refresh_phone_status(self):
        def worker():
            from android.phone_controller import phone
            info = phone.get_phone_info()
            connected = phone.is_connected()
            label_text = "● PHONE: CONNECTED" if connected else "○ PHONE: DISCONNECTED"
            QMetaObject.invokeMethod(self.phone_status_label, "setText", Qt.QueuedConnection, Q_ARG(str, label_text))
            html = f"<div style='font-size:14px; font-weight:bold; color:#38bdf8; margin-bottom:8px;'>ANDROID DEVICE STATUS</div><pre style='color:#e2edff;'>{info}</pre>"
            QMetaObject.invokeMethod(self.phone_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_connect_phone_wifi(self):
        ip = self.wifi_ip_input.text().strip()
        if not ip:
            return
        def worker():
            from android.phone_controller import phone
            res = phone.connect_wireless(ip)
            html = f"<p style='color:#00e5ff;'><b>Wireless Connect Result:</b> {res}</p>"
            QMetaObject.invokeMethod(self.phone_browser, "append", Qt.QueuedConnection, Q_ARG(str, html))
            self._refresh_phone_status()
        threading.Thread(target=worker, daemon=True).start()

    # --------------------------------------------------------
    # VIEW 3: 24/7 CLOUD NODE VIEW
    # --------------------------------------------------------
    def _build_cloud_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QLabel("NEXUS 24/7 CLOUD NODE & AUTOPILOT ENGINE")
        header.setProperty("class", "panelHeader")
        layout.addWidget(header)

        # Status & Action row
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        btn_start = QPushButton("▶️ Start Cloud Node")
        btn_start.setProperty("class", "hudButton")
        btn_start.clicked.connect(self._handle_ui_start_cloud)
        action_row.addWidget(btn_start)

        btn_sync = QPushButton("🔄 Sync With 24/7 Cloud")
        btn_sync.setProperty("class", "hudButtonPrimary")
        btn_sync.clicked.connect(self._handle_ui_cloud_sync)
        action_row.addWidget(btn_sync)

        btn_check = QPushButton("⚡ Check Status")
        btn_check.setProperty("class", "hudButton")
        btn_check.clicked.connect(lambda: self._execute_and_display("cloud status"))
        action_row.addWidget(btn_check)

        btn_pwa = QPushButton("📱 Open Mobile PWA")
        btn_pwa.setProperty("class", "hudButton")
        btn_pwa.clicked.connect(lambda: webbrowser.open("https://sachinnaik11.github.io/nexus/"))
        action_row.addWidget(btn_pwa)

        btn_open_health = QPushButton("🌐 Health Endpoint")
        btn_open_health.setProperty("class", "hudButton")
        btn_open_health.clicked.connect(lambda: webbrowser.open("http://localhost:8000/health"))
        action_row.addWidget(btn_open_health)

        action_row.addStretch()
        layout.addLayout(action_row)

        self.cloud_browser = QTextBrowser()
        self.cloud_browser.setObjectName("chatBrowser")
        self.cloud_browser.setHtml(
            "<div style='color: #637b99; font-size: 13px;'>"
            "<b>NEXUS 24/7 Cloud Architecture</b><br><br>"
            "• Keeps your assistant alive in the cloud even when your laptop and phone are switched off.<br>"
            "• Autonomously drafts viral YouTube titles and Shorts memes according to your niche.<br>"
            "• Dispatches alerts with [Approve] buttons to your Telegram bot.<br>"
            "• Click <b>Sync With 24/7 Cloud</b> to pull all approved drafts into your desktop assistant."
            "</div>"
        )
        layout.addWidget(self.cloud_browser, 1)
        return page

    def _refresh_cloud_status(self):
        def worker():
            from cloud.sync_client import cloud_sync
            connected = cloud_sync.check_connection()
            if not connected:
                # Attempt automatic launch of cloud node in background
                from cloud.nexus_cloud_server import start_cloud_server_background
                connected = start_cloud_server_background()

            status_text = "ONLINE" if connected else "OFFLINE / UNREACHABLE"
            color = "#00e5ff" if connected else "#ef4444"
            html = (
                f"<div style='font-size:14px; font-weight:bold; color:#38bdf8; margin-bottom:8px;'>24/7 CLOUD NODE STATUS</div>"
                f"<p>Node Address: <code>{cloud_sync.cloud_url}</code></p>"
                f"<p>Connection: <b style='color:{color};'>{status_text}</b></p>"
            )
            if connected:
                res = cloud_sync.sync()
                html += f"<p>Channel Niche: <b>{res.get('niche')}</b></p>"
                html += f"<p>Pending Drafts: <b>{res.get('pending_count')}</b></p>"
                html += f"<p>Approved Drafts: <b>{res.get('approved_count')}</b></p>"
                html += "<p style='color:#38bdf8;'>✅ Cloud Server is running and actively processing background tasks.</p>"
            else:
                html += (
                    "<p style='color:#ef4444;'>⚠️ Could not bind to port 8000 automatically.</p>"
                    "<p>Click <b>▶️ Start Cloud Node</b> above or run <code>CLOUD_SERVER.bat</code>.</p>"
                )
            QMetaObject.invokeMethod(self.cloud_browser, "setHtml", Qt.QueuedConnection, Q_ARG(str, html))
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_start_cloud(self):
        def worker():
            from cloud.nexus_cloud_server import start_cloud_server_background
            start_cloud_server_background()
            self._refresh_cloud_status()
        threading.Thread(target=worker, daemon=True).start()

    def _handle_ui_cloud_sync(self):
        def worker():
            from cloud.sync_client import cloud_sync
            connected = cloud_sync.check_connection()
            if not connected:
                from cloud.nexus_cloud_server import start_cloud_server_background
                start_cloud_server_background()
            res = cloud_sync.sync()
            msg = res.get("message", "Sync complete.")
            self.set_activity("CLOUD SYNC COMPLETE")
            self._refresh_cloud_status()
        threading.Thread(target=worker, daemon=True).start()

    def _execute_and_display(self, text):
        from core.router import route_command, get_command_target
        from core.command_executor import execute_command
        cmd_type = route_command(text)
        target = get_command_target(text)
        result = execute_command(cmd_type, target)
        self.set_activity(f"EXECUTED: {text}")
        self.set_response(str(result))

    # --------------------------------------------------------
    # SIGNAL HANDLERS & PROTOCOL METHODS
    # --------------------------------------------------------
    def _connect_signals(self):
        self.command_signal.connect(self.update_command)
        self.response_signal.connect(self.set_response)
        self.listening_signal.connect(self.set_listening)
        self.activity_signal.connect(self.set_activity)

    def _handle_send_text(self):
        text = self.text_input.text().strip()
        if not text:
            return
        self.text_input.clear()
        self.text_input_signal.emit(text)
        self.update_command(text)

    def _send_quick_command(self, cmd: str):
        if not cmd:
            return
        self.text_input_signal.emit(cmd)
        self.update_command(cmd)

    def _toggle_mic(self):
        self.mic_active = not self.mic_active
        if self.mic_active:
            self.mic_btn.setText("🎙️ MIC ON")
            self.mic_btn.setStyleSheet("")
            self.mic_badge.setText("● MIC ACTIVE")
            self.mic_badge.setStyleSheet("color: #00e5ff; font-size: 11px; font-weight: bold;")
        else:
            self.mic_btn.setText("🔇 MUTED")
            self.mic_btn.setStyleSheet("color: #ef4444; border-color: #ef4444;")
            self.mic_badge.setText("○ MIC MUTED")
            self.mic_badge.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold;")
        self.mic_toggle_signal.emit(self.mic_active)

    def _handle_stop_speech(self):
        self.stop_speaking_signal.emit()
        self.set_activity("SPEECH STOPPED")

    # --------------------------------------------------------
    # BACKWARD-COMPATIBLE API (CALLED BY main.py)
    # --------------------------------------------------------
    def set_listening(self):
        self.status.setText("●  LISTENING")
        self.activity_status.setText("● LISTENING")
        self.activity_ticker.setText("● TIMELINE: LISTENING TO MICROPHONE...")
        self.core.set_state("LISTENING")

    def set_activity(self, text):
        clean_text = str(text).strip()
        self.activity_status.setText("● " + clean_text)
        self.activity_ticker.setText("● TIMELINE: " + clean_text)

        # Update core state based on activity context
        upper = clean_text.upper()
        if "THINKING" in upper or "SEARCH" in upper or "AI" in upper:
            self.core.set_state("THINKING")
        elif "RESPONSE" in upper or "SPEAK" in upper:
            self.core.set_state("SPEAKING")
        elif "ERROR" in upper or "FAIL" in upper:
            self.core.set_state("ERROR")
        elif "LISTENING" in upper:
            self.core.set_state("LISTENING")

    def update_command(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.status.setText("●  PROCESSING")
        self.core.set_state("THINKING")

        entry = (
            f"<div style='margin-top: 10px; margin-bottom: 6px;'>"
            f"<span style='color: #637b99; font-size: 11px;'>[{now}]</span> "
            f"<span style='color: #00e5ff; font-weight: bold;'>YOU:</span> {text}"
            f"</div>"
        )
        self.chat_browser.append(entry)
        self.command.setText("YOU: " + text)

    def set_response(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.status.setText("●  SYSTEM ONLINE")
        self.core.set_state("SPEAKING")

        entry = (
            f"<div style='margin-bottom: 12px;'>"
            f"<span style='color: #637b99; font-size: 11px;'>[{now}]</span> "
            f"<span style='color: #38bdf8; font-weight: bold;'>NEXUS:</span> {text}"
            f"</div>"
        )
        self.chat_browser.append(entry)
        self.command.setText("NEXUS: " + text)

        # Refresh memory tab if memories changed
        self._refresh_memory_view()

    def set_command(self, text):
        self.update_command(text)

    def animate_core(self):
        # Retained for legacy timer call compatibility
        pass


# ============================================================
# STANDALONE ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NexusUI()
    window.show()
    sys.exit(app.exec())