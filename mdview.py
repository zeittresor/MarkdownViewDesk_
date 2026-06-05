# SPDX-License-Identifier: GPL-3.0-or-later
# MarkdownViewDesk - lightweight Markdown viewer for Windows / PyQt6
# Original source / updates: https://github.com/zeittresor

from __future__ import annotations

import html
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import markdown
    from markdown.extensions.toc import slugify_unicode
    from pygments.formatters import HtmlFormatter
except Exception:  # pragma: no cover - shown in GUI at runtime
    markdown = None
    slugify_unicode = None
    HtmlFormatter = None

from PyQt6.QtCore import Qt, QTimer, QUrl, QSettings, QSignalBlocker
from PyQt6.QtGui import QAction, QDesktopServices, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "MarkdownViewDesk"
APP_VERSION = "0.1.4"
APP_SOURCE_URL = "github.com/zeittresor"
MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd", ".txt"}
AMIGAGUIDE_EXTENSIONS = {".guide"}
DIZ_EXTENSIONS = {".diz"}
SUPPORTED_EXTENSIONS = MARKDOWN_EXTENSIONS | AMIGAGUIDE_EXTENSIONS | DIZ_EXTENSIONS

THEME_ORDER = ["light", "dark", "sepia", "ocean", "matrix", "purple", "hellfire"]
THEME_LABELS = {
    "en": {
        "light": "Light",
        "dark": "Dark",
        "sepia": "Sepia",
        "ocean": "Ocean",
        "matrix": "Matrix",
        "purple": "Purple",
        "hellfire": "Hellfire",
    },
    "de": {
        "light": "Hell",
        "dark": "Dunkel",
        "sepia": "Sepia",
        "ocean": "Ocean",
        "matrix": "Matrix",
        "purple": "Purple",
        "hellfire": "Hölle",
    },
}

THEME_ALIASES = {
    "light": "light",
    "bright": "light",
    "licht": "light",
    "hell": "hellfire",
    "dark": "dark",
    "dunkel": "dark",
    "sepia": "sepia",
    "ocean": "ocean",
    "matrix": "matrix",
    "purple": "purple",
    "violett": "purple",
    "lila": "purple",
    "hölle": "hellfire",
    "hoelle": "hellfire",
    "hellfire": "hellfire",
    "inferno": "hellfire",
}

I18N = {
    "en": {
        "menu_file": "File",
        "menu_view": "View",
        "menu_help": "Help",
        "open": "Open document…",
        "reload": "Reload",
        "open_folder": "Open containing folder",
        "exit": "Exit",
        "source": "Source",
        "outline": "Outline",
        "about": "About",
        "theme": "Theme:",
        "language": "Language:",
        "find_placeholder": "Find in rendered document…",
        "next": "Next",
        "prev": "Prev",
        "zoom_minus": "Zoom -",
        "zoom_plus": "Zoom +",
        "zoom_reset": "100%",
        "outline_heading": "Outline / Headings",
        "no_headings": "No headings found",
        "ready": "Ready",
        "open_dialog_title": "Open document",
        "file_not_found_title": "File not found",
        "file_not_found_body": "The file does not exist:",
        "jumped_to": "Jumped to:",
        "anchor": "Anchor:",
        "zoom_status": "Zoom:",
        "about_title": "About {app}",
        "about_body": (
            "{app} {version}\n\n"
            "A small PyQt6 document viewer optimized for README.md, AmigaGuide .guide, FILE_ID.DIZ and local text documents.\n\n"
            "Original source / updates:\n{source}\n\n"
            "Rendering stack: PyQt6 WebEngine, Python-Markdown and Pygments.\n"
            "License: GPL-3.0-or-later."
        ),
        "welcome_md": """# MarkdownViewDesk\n\nOpen a `README.md`, AmigaGuide `.guide`, `FILE_ID.DIZ` or another supported text document with **File → Open** or drag it into this window.\n\n## Supported display features\n\n- Headings with outline navigation\n- Tables\n- Fenced code blocks with syntax highlighting\n- Task lists like `- [x] done`\n- Relative image and file links\n- App-wide Light, Dark, Sepia, Ocean, Matrix, Purple and Hellfire themes\n- English and German user interface\n- Source view toggle
- Basic AmigaGuide `.guide` rendering
- Fixed-width `FILE_ID.DIZ` / `.diz` display\n\n```python\ndef hello_markdown():\n    print(\"MarkdownViewDesk is ready.\")\n```\n""",
    },
    "de": {
        "menu_file": "Datei",
        "menu_view": "Ansicht",
        "menu_help": "Hilfe",
        "open": "Dokument öffnen…",
        "reload": "Neu laden",
        "open_folder": "Ordner öffnen",
        "exit": "Beenden",
        "source": "Quelltext",
        "outline": "Gliederung",
        "about": "Über",
        "theme": "Theme:",
        "language": "Sprache:",
        "find_placeholder": "Im gerenderten Dokument suchen…",
        "next": "Weiter",
        "prev": "Zurück",
        "zoom_minus": "Zoom -",
        "zoom_plus": "Zoom +",
        "zoom_reset": "100%",
        "outline_heading": "Gliederung / Überschriften",
        "no_headings": "Keine Überschriften gefunden",
        "ready": "Bereit",
        "open_dialog_title": "Dokument öffnen",
        "file_not_found_title": "Datei nicht gefunden",
        "file_not_found_body": "Die Datei existiert nicht:",
        "jumped_to": "Gesprungen zu:",
        "anchor": "Anker:",
        "zoom_status": "Zoom:",
        "about_title": "Über {app}",
        "about_body": (
            "{app} {version}\n\n"
            "Ein kleiner PyQt6-Dokumentviewer für README.md, AmigaGuide .guide, FILE_ID.DIZ und lokale Textdokumente.\n\n"
            "Originalquelle / Updates:\n{source}\n\n"
            "Rendering-Stack: PyQt6 WebEngine, Python-Markdown und Pygments.\n"
            "Lizenz: GPL-3.0-or-later."
        ),
        "welcome_md": """# MarkdownViewDesk\n\nÖffne eine `README.md`, AmigaGuide-`.guide`, `FILE_ID.DIZ` oder ein anderes unterstütztes Textdokument über **Datei → Öffnen** oder ziehe die Datei in dieses Fenster.\n\n## Unterstützte Darstellung\n\n- Überschriften mit Gliederungsnavigation\n- Tabellen\n- Codeblöcke mit Syntaxhervorhebung\n- Aufgabenlisten wie `- [x] erledigt`\n- Relative Bild- und Dateilinks\n- App-weite Themes: Hell, Dunkel, Sepia, Ocean, Matrix, Purple und Hölle\n- Englische und deutsche Benutzeroberfläche\n- Umschaltbare Quelltextansicht
- Einfache AmigaGuide-`.guide`-Darstellung
- Festbreite Anzeige für `FILE_ID.DIZ` / `.diz`\n\n```python\ndef hello_markdown():\n    print(\"MarkdownViewDesk ist bereit.\")\n```\n""",
    },
}

APP_THEME = {
    "light": {
        "app_bg": "#f6f8fa",
        "panel_bg": "#ffffff",
        "control_bg": "#ffffff",
        "control_alt": "#f3f4f6",
        "fg": "#1f2328",
        "muted": "#57606a",
        "border": "#c9d1d9",
        "accent": "#0969da",
        "selection_bg": "#dbeafe",
        "selection_fg": "#111827",
    },
    "dark": {
        "app_bg": "#0d1117",
        "panel_bg": "#161b22",
        "control_bg": "#0f1722",
        "control_alt": "#21262d",
        "fg": "#e6edf3",
        "muted": "#8b949e",
        "border": "#30363d",
        "accent": "#58a6ff",
        "selection_bg": "#1f6feb",
        "selection_fg": "#ffffff",
    },
    "sepia": {
        "app_bg": "#ead9b8",
        "panel_bg": "#fbf1dc",
        "control_bg": "#fff5df",
        "control_alt": "#f3e3c3",
        "fg": "#3f3122",
        "muted": "#6d5c45",
        "border": "#c9ad80",
        "accent": "#7b4f00",
        "selection_bg": "#e7c989",
        "selection_fg": "#2a1d10",
    },
    "ocean": {
        "app_bg": "#061923",
        "panel_bg": "#092436",
        "control_bg": "#0d2e42",
        "control_alt": "#123d55",
        "fg": "#e6fbff",
        "muted": "#93c5d6",
        "border": "#1e5b73",
        "accent": "#5eead4",
        "selection_bg": "#0e7490",
        "selection_fg": "#f0fdff",
    },
    "matrix": {
        "app_bg": "#020702",
        "panel_bg": "#061106",
        "control_bg": "#081808",
        "control_alt": "#0d260d",
        "fg": "#b6ffb6",
        "muted": "#66cc77",
        "border": "#146b2f",
        "accent": "#00ff66",
        "selection_bg": "#0b7a2d",
        "selection_fg": "#eaffea",
    },
    "purple": {
        "app_bg": "#12061f",
        "panel_bg": "#1d0b33",
        "control_bg": "#261044",
        "control_alt": "#34185a",
        "fg": "#f4e8ff",
        "muted": "#c4a7e7",
        "border": "#6d3fb3",
        "accent": "#c084fc",
        "selection_bg": "#7e22ce",
        "selection_fg": "#fff7ff",
    },
    "hellfire": {
        "app_bg": "#170505",
        "panel_bg": "#240808",
        "control_bg": "#2c0a06",
        "control_alt": "#421109",
        "fg": "#ffe1c7",
        "muted": "#ffb17a",
        "border": "#7f1d1d",
        "accent": "#ff8a3d",
        "selection_bg": "#b91c1c",
        "selection_fg": "#fff7ed",
    },
}

PYGMENTS_STYLE_BY_THEME = {
    "light": "friendly",
    "dark": "monokai",
    "sepia": "friendly",
    "ocean": "native",
    "matrix": "native",
    "purple": "monokai",
    "hellfire": "monokai",
}


@dataclass
class Heading:
    level: int
    text: str
    identifier: str


def normalize_theme_key(value: str | None) -> str:
    if not value:
        return "light"
    key = str(value).strip().lower()
    return THEME_ALIASES.get(key, key if key in THEME_ORDER else "light")


def normalize_language(value: str | None) -> str:
    key = str(value or "en").strip().lower()
    return "de" if key.startswith("de") else "en"


class MarkdownPage(QWebEnginePage):
    """Intercept link clicks so local Markdown links open inside the viewer."""

    def __init__(self, owner: "MarkdownViewDesk") -> None:
        super().__init__(owner)
        self.owner = owner

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame: bool) -> bool:
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # Same-page anchors should remain internal browser navigation.
            # For setHtml(baseUrl=file:///folder/), fragment links can resolve to
            # the base folder URL plus #fragment instead of the Markdown file path.
            if self.owner.is_same_document_anchor(url):
                return True
            self.owner.open_url_from_markdown(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class MarkdownViewDesk(QMainWindow):
    def __init__(self, initial_file: str | None = None) -> None:
        super().__init__()
        self.settings = QSettings("Zeittresor", APP_NAME)
        self.current_file: Path | None = None
        self.current_text = ""
        self.current_headings: list[Heading] = []
        self.current_theme_key = normalize_theme_key(str(self.settings.value("theme", "light")))
        self.current_language = normalize_language(str(self.settings.value("language", "en")))
        self.zoom_factor = float(self.settings.value("zoom", 1.0))

        self.setWindowTitle(APP_NAME)
        self.setAcceptDrops(True)
        self.resize(1200, 820)
        self._build_ui()
        self._build_actions()
        self._restore_geometry()

        self.web.setZoomFactor(self.zoom_factor)
        self.rebuild_theme_combo()
        self.rebuild_language_combo()
        self.apply_application_theme()
        self.apply_translation()

        if initial_file:
            self.open_file(Path(initial_file))
        else:
            self.show_welcome()

    # ---------- Translation / theme helpers ----------

    def tr(self, key: str) -> str:
        return I18N.get(self.current_language, I18N["en"]).get(key, I18N["en"].get(key, key))

    def theme_label(self, key: str) -> str:
        return THEME_LABELS.get(self.current_language, THEME_LABELS["en"]).get(key, key.title())

    def rebuild_theme_combo(self) -> None:
        blocker = QSignalBlocker(self.theme_combo)
        self.theme_combo.clear()
        for key in THEME_ORDER:
            self.theme_combo.addItem(self.theme_label(key), key)
        index = self.theme_combo.findData(self.current_theme_key)
        self.theme_combo.setCurrentIndex(index if index >= 0 else 0)
        del blocker

    def rebuild_language_combo(self) -> None:
        blocker = QSignalBlocker(self.language_combo)
        self.language_combo.clear()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Deutsch", "de")
        index = self.language_combo.findData(self.current_language)
        self.language_combo.setCurrentIndex(index if index >= 0 else 0)
        del blocker

    def apply_translation(self) -> None:
        self.open_action.setText(self.tr("open"))
        self.reload_action.setText(self.tr("reload"))
        self.open_folder_action.setText(self.tr("open_folder"))
        self.quit_action.setText(self.tr("exit"))
        self.zoom_out_action.setText(self.tr("zoom_minus"))
        self.zoom_in_action.setText(self.tr("zoom_plus"))
        self.zoom_reset_action.setText(self.tr("zoom_reset"))
        self.source_action.setText(self.tr("source"))
        self.outline_action.setText(self.tr("outline"))
        self.about_action.setText(self.tr("about"))
        self.find_input.setPlaceholderText(self.tr("find_placeholder"))
        self.find_next_button.setText(self.tr("next"))
        self.find_prev_button.setText(self.tr("prev"))
        self.theme_label_widget.setText(f" {self.tr('theme')} ")
        self.language_label_widget.setText(f" {self.tr('language')} ")
        self.outline_title_label.setText(self.tr("outline_heading"))
        self.outline_dock.setWindowTitle(self.tr("outline"))
        self.file_menu.setTitle(self.tr("menu_file"))
        self.view_menu.setTitle(self.tr("menu_view"))
        self.help_menu.setTitle(self.tr("menu_help"))
        self.rebuild_theme_combo()
        if not self.current_file:
            self.show_welcome()

    def theme_values(self) -> dict[str, str]:
        return APP_THEME.get(self.current_theme_key, APP_THEME["light"])

    def apply_application_theme(self) -> None:
        t = self.theme_values()
        self.setStyleSheet(f"""
QMainWindow, QWidget {{
    background-color: {t['app_bg']};
    color: {t['fg']};
}}
QDockWidget {{
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background-color: {t['control_alt']};
    color: {t['fg']};
    padding: 4px;
    border: 1px solid {t['border']};
}}
QToolBar, QMenuBar, QStatusBar {{
    background-color: {t['control_alt']};
    color: {t['fg']};
    border-bottom: 1px solid {t['border']};
}}
QMenuBar::item:selected, QMenu::item:selected {{
    background-color: {t['selection_bg']};
    color: {t['selection_fg']};
}}
QMenu {{
    background-color: {t['panel_bg']};
    color: {t['fg']};
    border: 1px solid {t['border']};
}}
QLineEdit, QTextEdit, QListWidget, QComboBox {{
    background-color: {t['control_bg']};
    color: {t['fg']};
    border: 1px solid {t['border']};
    selection-background-color: {t['selection_bg']};
    selection-color: {t['selection_fg']};
}}
QLineEdit, QComboBox {{
    padding: 3px 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {t['panel_bg']};
    color: {t['fg']};
    selection-background-color: {t['selection_bg']};
    selection-color: {t['selection_fg']};
    border: 1px solid {t['border']};
}}
QPushButton {{
    background-color: {t['control_bg']};
    color: {t['fg']};
    border: 1px solid {t['border']};
    padding: 4px 10px;
}}
QPushButton:hover {{
    background-color: {t['control_alt']};
    border-color: {t['accent']};
}}
QPushButton:pressed {{
    background-color: {t['selection_bg']};
    color: {t['selection_fg']};
}}
QListWidget::item:selected {{
    background-color: {t['selection_bg']};
    color: {t['selection_fg']};
}}
QSplitter::handle {{
    background-color: {t['border']};
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background-color: {t['app_bg']};
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background-color: {t['muted']};
    border-radius: 4px;
}}
QLabel {{
    color: {t['fg']};
}}
""")

    # ---------- UI ----------

    def _build_ui(self) -> None:
        self.web = QWebEngineView(self)
        self.web.setPage(MarkdownPage(self))
        self._configure_web_security()

        self.source_edit = QTextEdit(self)
        self.source_edit.setReadOnly(True)
        self.source_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.source_edit.hide()

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.addWidget(self.web)
        self.splitter.addWidget(self.source_edit)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.setCentralWidget(self.splitter)

        self.outline = QListWidget(self)
        self.outline.setMaximumWidth(360)
        self.outline.itemActivated.connect(self.jump_to_heading)
        self.outline.itemClicked.connect(self.jump_to_heading)

        outline_container = QWidget(self)
        outline_layout = QVBoxLayout(outline_container)
        outline_layout.setContentsMargins(8, 8, 8, 8)
        self.outline_title_label = QLabel("Outline / Headings", self)
        outline_layout.addWidget(self.outline_title_label)
        outline_layout.addWidget(self.outline)
        outline_container.setLayout(outline_layout)

        self.outline_dock = self.addDockWidgetCompat("Outline", outline_container)

        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

    def addDockWidgetCompat(self, title: str, widget: QWidget) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        return dock

    def _build_actions(self) -> None:
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.open_action = QAction("Open .md…", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_dialog)
        toolbar.addAction(self.open_action)

        self.reload_action = QAction("Reload", self)
        self.reload_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.reload_action.triggered.connect(self.reload_file)
        toolbar.addAction(self.reload_action)

        toolbar.addSeparator()

        self.find_input = QLineEdit(self)
        self.find_input.returnPressed.connect(lambda: self.find_text(backwards=False))
        toolbar.addWidget(self.find_input)

        self.find_next_button = QPushButton("Next", self)
        self.find_next_button.clicked.connect(lambda: self.find_text(backwards=False))
        toolbar.addWidget(self.find_next_button)

        self.find_prev_button = QPushButton("Prev", self)
        self.find_prev_button.clicked.connect(lambda: self.find_text(backwards=True))
        toolbar.addWidget(self.find_prev_button)

        toolbar.addSeparator()

        self.zoom_out_action = QAction("Zoom -", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(lambda: self.change_zoom(-0.1))
        toolbar.addAction(self.zoom_out_action)

        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(lambda: self.change_zoom(0.1))
        toolbar.addAction(self.zoom_in_action)

        self.zoom_reset_action = QAction("100%", self)
        self.zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        self.zoom_reset_action.triggered.connect(self.reset_zoom)
        toolbar.addAction(self.zoom_reset_action)

        toolbar.addSeparator()

        self.source_action = QAction("Source", self)
        self.source_action.setCheckable(True)
        self.source_action.triggered.connect(self.toggle_source)
        toolbar.addAction(self.source_action)

        self.outline_action = QAction("Outline", self)
        self.outline_action.setCheckable(True)
        self.outline_action.setChecked(True)
        self.outline_action.triggered.connect(lambda checked: self.outline_dock.setVisible(checked))
        toolbar.addAction(self.outline_action)
        self.outline_dock.visibilityChanged.connect(self.outline_action.setChecked)

        self.theme_label_widget = QLabel(" Theme: ", self)
        toolbar.addWidget(self.theme_label_widget)
        self.theme_combo = QComboBox(self)
        self.theme_combo.currentIndexChanged.connect(self.change_theme_from_combo)
        toolbar.addWidget(self.theme_combo)

        self.language_label_widget = QLabel(" Language: ", self)
        toolbar.addWidget(self.language_label_widget)
        self.language_combo = QComboBox(self)
        self.language_combo.currentIndexChanged.connect(self.change_language_from_combo)
        toolbar.addWidget(self.language_combo)

        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.reload_action)
        self.file_menu.addSeparator()

        self.open_folder_action = QAction("Open containing folder", self)
        self.open_folder_action.triggered.connect(self.open_containing_folder)
        self.file_menu.addAction(self.open_folder_action)

        self.file_menu.addSeparator()
        self.quit_action = QAction("Exit", self)
        self.quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.quit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.quit_action)

        self.view_menu = menubar.addMenu("View")
        self.view_menu.addAction(self.zoom_in_action)
        self.view_menu.addAction(self.zoom_out_action)
        self.view_menu.addAction(self.zoom_reset_action)
        self.view_menu.addAction(self.source_action)
        self.view_menu.addAction(self.outline_action)

        self.help_menu = menubar.addMenu("Help")
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

    def _configure_web_security(self) -> None:
        settings = self.web.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)

    # ---------- File handling ----------

    def open_dialog(self) -> None:
        start_dir = str(self.current_file.parent if self.current_file else Path.home())
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("open_dialog_title"),
            start_dir,
            "Supported documents (*.md *.markdown *.mdown *.mkd *.guide *.diz *.txt);;Markdown files (*.md *.markdown *.mdown *.mkd);;AmigaGuide files (*.guide);;DIZ files (*.diz);;Text files (*.txt);;All files (*.*)",
        )
        if path:
            self.open_file(Path(path))

    def open_file(self, path: Path) -> None:
        path = path.expanduser().resolve()
        if not path.exists():
            QMessageBox.warning(self, self.tr("file_not_found_title"), f"{self.tr('file_not_found_body')}\n{path}")
            return
        if path.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
            return

        text = self._read_text(path)
        self.current_file = path
        self.current_text = text
        self.source_edit.setPlainText(text)
        self.render_current_markdown()
        self.setWindowTitle(f"{path.name} - {APP_NAME}")
        self.status.showMessage(str(path))
        self.settings.setValue("last_file", str(path))

    def _read_text(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return path.read_bytes().decode("utf-8", errors="replace")

    def reload_file(self) -> None:
        if not self.current_file:
            self.show_welcome()
            return
        self.open_file(self.current_file)

    def open_containing_folder(self) -> None:
        if not self.current_file:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.current_file.parent)))

    def is_same_document_anchor(self, url: QUrl) -> bool:
        if not url.hasFragment():
            return False
        if url.toString().startswith("#"):
            return True
        if not url.isLocalFile() or not self.current_file:
            return False
        try:
            local_path = Path(url.toLocalFile()).resolve()
        except OSError:
            return False
        return local_path == self.current_file.parent.resolve() or local_path == self.current_file.resolve()

    def open_url_from_markdown(self, url: QUrl) -> None:
        if url.isLocalFile():
            local_path = Path(url.toLocalFile()).resolve()
            suffix = local_path.suffix.lower()
            if suffix in SUPPORTED_EXTENSIONS and local_path.exists():
                self.open_file(local_path)
                return
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path)))
            return

        if url.scheme() in {"http", "https", "mailto"}:
            QDesktopServices.openUrl(url)
            return

        # Fragment links in documents rendered from setHtml() can appear as relative URLs.
        if url.toString().startswith("#") and self.current_file:
            self.status.showMessage(f"{self.tr('anchor')} {url.toString()}", 2500)

    # ---------- Rendering ----------

    def render_current_markdown(self) -> None:
        if not self.current_file:
            self.show_welcome()
            return

        html_body, headings = render_text_to_html(self.current_text, self.current_file)
        self.current_headings = headings
        self.populate_outline(headings)
        full_html = self.build_html_document(html_body, self.current_file.name)
        base_url = QUrl.fromLocalFile(str(self.current_file.parent) + os.sep)
        self.web.setHtml(full_html, base_url)

    def build_html_document(self, body: str, title: str) -> str:
        pygments_css = self.pygments_css()
        return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
{pygments_css}
{self.base_css()}
</style>
</head>
<body class="theme-{self.current_theme_key}">
<main class="markdown-body">
{body}
</main>
</body>
</html>"""

    def pygments_css(self) -> str:
        if not HtmlFormatter:
            return ""
        style = PYGMENTS_STYLE_BY_THEME.get(self.current_theme_key, "friendly")
        try:
            return HtmlFormatter(style=style).get_style_defs(".codehilite")
        except Exception:
            return HtmlFormatter().get_style_defs(".codehilite")

    def base_css(self) -> str:
        return r"""
:root {
  --bg: #ffffff;
  --fg: #24292f;
  --muted: #57606a;
  --border: #d0d7de;
  --soft: #f6f8fa;
  --link: #0969da;
  --code-bg: #f6f8fa;
  --code-fg: #1f2328;
  --code-border: #d0d7de;
  --quote-border: #d0d7de;
  --table-alt: #f6f8fa;
  --kbd-bg: #fafbfc;
}
body.theme-dark {
  --bg: #0d1117;
  --fg: #e6edf3;
  --muted: #8b949e;
  --border: #30363d;
  --soft: #161b22;
  --link: #58a6ff;
  --code-bg: #111820;
  --code-fg: #e6edf3;
  --code-border: #3d444d;
  --quote-border: #30363d;
  --table-alt: #161b22;
  --kbd-bg: #21262d;
}
body.theme-sepia {
  --bg: #fbf1dc;
  --fg: #3f3122;
  --muted: #6d5c45;
  --border: #d8c3a5;
  --soft: #f3e3c3;
  --link: #7b4f00;
  --code-bg: #f3e3c3;
  --code-fg: #2d2117;
  --code-border: #c9ad80;
  --quote-border: #cfb58c;
  --table-alt: #f5e8cf;
  --kbd-bg: #fff4dd;
}
body.theme-ocean {
  --bg: #061923;
  --fg: #e6fbff;
  --muted: #93c5d6;
  --border: #1e5b73;
  --soft: #092436;
  --link: #5eead4;
  --code-bg: #05131c;
  --code-fg: #e6fbff;
  --code-border: #247087;
  --quote-border: #2dd4bf;
  --table-alt: #092436;
  --kbd-bg: #0d2e42;
}
body.theme-matrix {
  --bg: #020702;
  --fg: #b6ffb6;
  --muted: #66cc77;
  --border: #146b2f;
  --soft: #061106;
  --link: #00ff66;
  --code-bg: #001100;
  --code-fg: #caffca;
  --code-border: #159947;
  --quote-border: #00ff66;
  --table-alt: #061106;
  --kbd-bg: #081808;
}
body.theme-purple {
  --bg: #12061f;
  --fg: #f4e8ff;
  --muted: #c4a7e7;
  --border: #6d3fb3;
  --soft: #1d0b33;
  --link: #c084fc;
  --code-bg: #190927;
  --code-fg: #fff1ff;
  --code-border: #7e22ce;
  --quote-border: #a855f7;
  --table-alt: #1d0b33;
  --kbd-bg: #261044;
}
body.theme-hellfire {
  --bg: #170505;
  --fg: #ffe1c7;
  --muted: #ffb17a;
  --border: #7f1d1d;
  --soft: #240808;
  --link: #ff8a3d;
  --code-bg: #260604;
  --code-fg: #fff1e5;
  --code-border: #b91c1c;
  --quote-border: #f97316;
  --table-alt: #240808;
  --kbd-bg: #421109;
}
html { background: var(--bg); }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.58;
}
.markdown-body {
  max-width: 1040px;
  margin: 0 auto;
  padding: 40px 54px 80px;
  box-sizing: border-box;
}
@media (max-width: 720px) {
  .markdown-body { padding: 24px 18px 64px; }
}
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5em;
  margin-bottom: 0.65em;
  font-weight: 650;
  line-height: 1.25;
}
h1, h2 { padding-bottom: .35em; border-bottom: 1px solid var(--border); }
h1 { font-size: 2.0em; }
h2 { font-size: 1.55em; }
h3 { font-size: 1.25em; }
p, ul, ol, blockquote, table, pre { margin-top: 0; margin-bottom: 1em; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; border-radius: 6px; }
hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
blockquote {
  padding: 0 1em;
  color: var(--muted);
  border-left: .25em solid var(--quote-border);
}
code, kbd, pre, samp {
  font-family: "Cascadia Mono", "Consolas", "Liberation Mono", Menlo, monospace;
}
code {
  padding: .2em .4em;
  margin: 0;
  font-size: 85%;
  white-space: break-spaces;
  color: var(--code-fg);
  background-color: var(--code-bg);
  border: 1px solid rgba(127,127,127,.18);
  border-radius: 6px;
}
pre {
  padding: 16px;
  overflow: auto;
  font-size: 90%;
  line-height: 1.45;
  color: var(--code-fg);
  background-color: var(--code-bg) !important;
  border: 1px solid var(--code-border);
  border-radius: 8px;
}
pre code { padding: 0; background: transparent; border: 0; white-space: pre; color: inherit; }
.codehilite {
  background: var(--code-bg) !important;
  color: var(--code-fg);
  border: 1px solid var(--code-border);
  border-radius: 8px;
  margin-bottom: 1em;
}
.codehilite pre {
  background: transparent !important;
  border: 0;
  margin: 0;
  color: inherit;
}
.codehilite code { background: transparent; border: 0; }
table {
  border-spacing: 0;
  border-collapse: collapse;
  display: block;
  width: 100%;
  overflow: auto;
}
table th, table td {
  padding: 6px 13px;
  border: 1px solid var(--border);
}
table tr { background-color: var(--bg); border-top: 1px solid var(--border); }
table tr:nth-child(2n) { background-color: var(--table-alt); }
table th { font-weight: 650; background-color: var(--soft); }
kbd {
  display: inline-block;
  padding: 3px 5px;
  font-size: 0.9em;
  line-height: 10px;
  color: var(--fg);
  vertical-align: middle;
  background-color: var(--kbd-bg);
  border: solid 1px var(--border);
  border-bottom-color: var(--muted);
  border-radius: 6px;
  box-shadow: inset 0 -1px 0 var(--muted);
}
.task-list-control { margin-right: .45em; }
.admonition {
  padding: 12px 16px;
  margin-bottom: 1em;
  border-left: 4px solid var(--link);
  background: var(--soft);
  border-radius: 6px;
}
.admonition-title { font-weight: 650; margin-top: 0; }

.format-note {
  display: inline-block;
  margin: 0 0 1.2em 0;
  padding: 6px 10px;
  color: var(--muted);
  background: var(--soft);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.92em;
}
.amigaguide-node {
  margin: 1.4em 0 2.2em;
  padding: 1em 1.2em;
  background: var(--soft);
  border: 1px solid var(--border);
  border-radius: 10px;
}
.amigaguide-node h2 {
  margin-top: 0;
}
.amigaguide-node-name {
  color: var(--muted);
  font-size: 0.85em;
  margin-top: -0.4em;
  margin-bottom: 1em;
}
.amigaguide-body {
  white-space: normal;
  font-family: "Cascadia Mono", "Consolas", "Liberation Mono", Menlo, monospace;
  line-height: 1.45;
}
.amigaguide-body a.guide-link {
  display: inline-block;
  padding: 1px 7px;
  margin: 0 1px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--kbd-bg);
  color: var(--link);
  font-family: inherit;
}
.diz-note {
  margin-bottom: 1em;
}
.diz-card {
  display: inline-block;
  max-width: 100%;
  overflow-x: auto;
  padding: 14px 16px;
  background: var(--code-bg);
  color: var(--code-fg);
  border: 1px solid var(--code-border);
  border-radius: 10px;
  font-family: "Cascadia Mono", "Consolas", "Liberation Mono", Menlo, monospace;
  line-height: 1.35;
}
.diz-ruler,
.diz-line {
  white-space: pre;
  tab-size: 4;
  font-family: inherit;
}
.diz-ruler {
  color: var(--muted);
  margin-bottom: 0.45em;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.35em;
}
.diz-main {
  display: inline-block;
  width: 45ch;
}
.diz-overflow {
  background: rgba(255, 99, 71, 0.28);
  border-left: 2px solid var(--accent);
  padding-left: 2px;
}
.diz-line.beyond10 {
  opacity: 0.65;
}
.diz-line.beyond10::before {
  content: "+ ";
  color: var(--muted);
}
"""

    def populate_outline(self, headings: list[Heading]) -> None:
        self.outline.clear()
        if not headings:
            self.outline.addItem(self.tr("no_headings"))
            self.outline.setEnabled(False)
            return
        self.outline.setEnabled(True)
        for heading in headings:
            indent = "   " * max(0, heading.level - 1)
            item = QListWidgetItem(f"{indent}{heading.text}")
            item.setData(Qt.ItemDataRole.UserRole, heading)
            self.outline.addItem(item)

    def jump_to_heading(self, item: QListWidgetItem) -> None:
        heading = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(heading, Heading):
            return
        # JavaScript is disabled for safer rendering, so use WebEngine's built-in search as a robust jump.
        self.web.findText(heading.text)
        self.status.showMessage(f"{self.tr('jumped_to')} {heading.text}", 1800)

    def show_welcome(self) -> None:
        welcome_md = self.tr("welcome_md")
        body, headings = render_markdown_to_html(welcome_md)
        self.current_headings = headings
        self.populate_outline(headings)
        self.web.setHtml(self.build_html_document(body, APP_NAME), QUrl.fromLocalFile(str(Path.cwd()) + os.sep))
        self.source_edit.setPlainText(welcome_md)
        self.status.showMessage(self.tr("ready"))

    # ---------- View actions ----------

    def find_text(self, backwards: bool = False) -> None:
        text = self.find_input.text().strip()
        if not text:
            return
        flags = QWebEnginePage.FindFlag(0)
        if backwards:
            flags |= QWebEnginePage.FindFlag.FindBackward
        self.web.findText(text, flags)

    def change_zoom(self, delta: float) -> None:
        self.zoom_factor = max(0.5, min(2.5, self.web.zoomFactor() + delta))
        self.web.setZoomFactor(self.zoom_factor)
        self.settings.setValue("zoom", self.zoom_factor)
        self.status.showMessage(f"{self.tr('zoom_status')} {int(self.zoom_factor * 100)}%", 1200)

    def reset_zoom(self) -> None:
        self.zoom_factor = 1.0
        self.web.setZoomFactor(self.zoom_factor)
        self.settings.setValue("zoom", self.zoom_factor)
        self.status.showMessage(f"{self.tr('zoom_status')} 100%", 1200)

    def toggle_source(self, checked: bool) -> None:
        self.source_edit.setVisible(checked)

    def change_theme_from_combo(self, index: int) -> None:
        if index < 0:
            return
        theme_key = self.theme_combo.itemData(index)
        if not theme_key:
            return
        self.current_theme_key = normalize_theme_key(str(theme_key))
        self.settings.setValue("theme", self.current_theme_key)
        self.apply_application_theme()
        if self.current_file:
            self.render_current_markdown()
        else:
            self.show_welcome()

    def change_language_from_combo(self, index: int) -> None:
        if index < 0:
            return
        language = self.language_combo.itemData(index)
        if not language:
            return
        self.current_language = normalize_language(str(language))
        self.settings.setValue("language", self.current_language)
        self.apply_translation()
        if self.current_file:
            self.render_current_markdown()

    # ---------- Drag & drop ----------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() in SUPPORTED_EXTENSIONS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    self.open_file(path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    # ---------- Window state ----------

    def _restore_geometry(self) -> None:
        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            self.tr("about_title").format(app=APP_NAME),
            self.tr("about_body").format(app=APP_NAME, version=APP_VERSION, source=APP_SOURCE_URL),
        )


def preprocess_task_lists(text: str) -> str:
    """Convert GitHub-style task list markers to disabled checkbox HTML before Markdown conversion."""

    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        checked = " checked" if match.group(2).lower() == "x" else ""
        return f'{prefix}<input class="task-list-control" type="checkbox" disabled{checked}> '

    return re.sub(r"^(\s*[-*+]\s+)\[([ xX])\]\s+", repl, text, flags=re.MULTILINE)


def flatten_toc_tokens(tokens: Iterable[dict[str, Any]]) -> list[Heading]:
    headings: list[Heading] = []
    for token in tokens:
        name = html.unescape(str(token.get("name", ""))).strip()
        identifier = str(token.get("id", ""))
        level = int(token.get("level", 1))
        if name:
            headings.append(Heading(level=level, text=name, identifier=identifier))
        children = token.get("children", []) or []
        headings.extend(flatten_toc_tokens(children))
    return headings



@dataclass
class GuideNode:
    name: str
    title: str
    lines: list[str]


NODE_RE = re.compile(r'^\s*@node\s+(?:"([^"]+)"|(\S+))(?:\s+"([^"]+)")?', re.IGNORECASE)
ENDNODE_RE = re.compile(r'^\s*@endnode\b', re.IGNORECASE)
GUIDE_DIRECTIVE_RE = re.compile(r'^\s*(?:@\$ver:|@(database|master|title|author|copyright|version|index|remark|wordwrap|smartwrap|font|help|height|width|tab)\b)', re.IGNORECASE)
GUIDE_LINK_RE = re.compile(r'@\{\s*"([^"]+)"\s+LINK\s+("[^"]+"|\S+)(?:\s+\d+)?\s*\}', re.IGNORECASE)
GUIDE_INLINE_COMMAND_RE = re.compile(r'@\{\s*([^}]*)\s*\}', re.IGNORECASE)


def render_text_to_html(text: str, path: Path | None) -> tuple[str, list[Heading]]:
    suffix = path.suffix.lower() if path else ""
    if suffix in AMIGAGUIDE_EXTENSIONS:
        return render_amigaguide_to_html(text, path.name if path else "AmigaGuide")
    if suffix in DIZ_EXTENSIONS:
        return render_diz_to_html(text, path.name if path else "FILE_ID.DIZ")
    return render_markdown_to_html(text)


def guide_anchor(name: str) -> str:
    value = html.unescape(str(name)).strip().lower()
    value = re.sub(r'\s+', '-', value)
    value = re.sub(r'[^a-z0-9_\-\.]+', '-', value)
    value = value.strip('-') or 'node'
    return f"guide-{value}"


def parse_amigaguide_nodes(text: str) -> tuple[list[GuideNode], list[str]]:
    nodes: list[GuideNode] = []
    preamble: list[str] = []
    current: GuideNode | None = None

    for raw_line in text.splitlines():
        node_match = NODE_RE.match(raw_line)
        if node_match:
            if current is not None:
                nodes.append(current)
            name = node_match.group(1) or node_match.group(2) or "Node"
            title = node_match.group(3) or name
            current = GuideNode(name=name, title=title, lines=[])
            continue

        if ENDNODE_RE.match(raw_line):
            if current is not None:
                nodes.append(current)
                current = None
            continue

        if current is not None:
            current.lines.append(raw_line)
        elif raw_line.strip() and not GUIDE_DIRECTIVE_RE.match(raw_line):
            preamble.append(raw_line)

    if current is not None:
        nodes.append(current)
    return nodes, preamble


def guide_link_href(target: str) -> str:
    target = target.strip()
    if len(target) >= 2 and target[0] == '"' and target[-1] == '"':
        target = target[1:-1]
    target = target.strip()

    if re.match(r'^[a-z][a-z0-9+.-]*:', target, re.IGNORECASE):
        return target

    normalized = target.replace('\\', '/')
    match = re.match(r'(.+?\.(?:guide|md|markdown|txt|diz))(?:/([^/#]+))?$', normalized, re.IGNORECASE)
    if match:
        file_part = match.group(1)
        node_part = match.group(2)
        return file_part + (f"#{guide_anchor(node_part)}" if node_part else "")

    return f"#{guide_anchor(target)}"


def render_amigaguide_inline(line: str) -> str:
    line = line.replace('@@', '@')
    pieces: list[str] = []
    pos = 0
    for match in GUIDE_LINK_RE.finditer(line):
        pieces.append(render_amigaguide_style_segment(line[pos:match.start()]))
        label = match.group(1)
        target = match.group(2)
        href = guide_link_href(target)
        pieces.append(f'<a class="guide-link" href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
        pos = match.end()
    pieces.append(render_amigaguide_style_segment(line[pos:]))
    return ''.join(pieces)


def render_amigaguide_style_segment(segment: str) -> str:
    escaped = html.escape(segment)

    def repl(match: re.Match[str]) -> str:
        command = match.group(1).strip().lower()
        if command in {"b", "bold"}:
            return "<strong>"
        if command in {"ub", "/b", "boldoff"}:
            return "</strong>"
        if command in {"i", "italic"}:
            return "<em>"
        if command in {"ui", "/i", "italicoff"}:
            return "</em>"
        if command in {"u", "underline"}:
            return "<u>"
        if command in {"uu", "/u", "underlineoff"}:
            return "</u>"
        if command == "par":
            return "<br><br>"
        if command == "line":
            return "<hr>"
        return ""

    return GUIDE_INLINE_COMMAND_RE.sub(repl, escaped)


def render_amigaguide_lines(lines: list[str]) -> str:
    rendered: list[str] = []
    for line in lines:
        stripped = line.strip()
        if GUIDE_DIRECTIVE_RE.match(line):
            continue
        if stripped.startswith('@') and not stripped.startswith('@{') and not stripped.startswith('@@'):
            continue
        rendered.append(render_amigaguide_inline(line))
    return '<br>\n'.join(rendered)


def render_amigaguide_to_html(text: str, title: str) -> tuple[str, list[Heading]]:
    nodes, preamble = parse_amigaguide_nodes(text)
    sections: list[str] = []
    headings: list[Heading] = []

    escaped_title = html.escape(title)
    sections.append(f'<h1>{escaped_title}</h1>')
    sections.append('<p class="format-note">AmigaGuide view: basic node/link rendering for typical <code>.guide</code> documentation files.</p>')

    if preamble:
        body = render_amigaguide_lines(preamble)
        preamble_anchor = guide_anchor("Preamble")
        sections.append(f'<section class="amigaguide-node" id="{preamble_anchor}"><h2>Preamble</h2><div class="amigaguide-body">{body}</div></section>')
        headings.append(Heading(level=2, text="Preamble", identifier=preamble_anchor))

    if nodes:
        for node in nodes:
            anchor = guide_anchor(node.name)
            heading_text = node.title or node.name
            headings.append(Heading(level=2, text=heading_text, identifier=anchor))
            node_name = html.escape(node.name)
            node_title = html.escape(heading_text)
            body = render_amigaguide_lines(node.lines)
            sections.append(
                f'<section class="amigaguide-node" id="{anchor}">'
                f'<h2>{node_title}</h2>'
                f'<div class="amigaguide-node-name">@node {node_name}</div>'
                f'<div class="amigaguide-body">{body}</div>'
                f'</section>'
            )
    else:
        body = render_amigaguide_lines(text.splitlines())
        sections.append(f'<section class="amigaguide-node"><div class="amigaguide-body">{body}</div></section>')

    return '\n'.join(sections), headings


def diz_ruler(width: int = 45) -> str:
    chars: list[str] = []
    for i in range(1, width + 1):
        if i % 10 == 0:
            chars.append(str((i // 10) % 10))
        elif i % 5 == 0:
            chars.append('+')
        else:
            chars.append('-')
    return ''.join(chars)


def render_diz_to_html(text: str, title: str) -> tuple[str, list[Heading]]:
    raw_lines = text.splitlines()
    lines = raw_lines if raw_lines else [""]
    rendered_lines: list[str] = []
    longest = 0
    overflow_count = 0
    for index, line in enumerate(lines, start=1):
        longest = max(longest, len(line))
        before = html.escape(line[:45]) or '&nbsp;'
        after_raw = line[45:]
        class_name = 'diz-line beyond10' if index > 10 else 'diz-line'
        overflow_html = ''
        if after_raw:
            overflow_count += 1
            overflow_html = f'<span class="diz-overflow">{html.escape(after_raw)}</span>'
        rendered_lines.append(f'<div class="{class_name}"><span class="diz-main">{before}</span>{overflow_html}</div>')

    note = (
        f'{len(raw_lines)} line(s), longest line {longest} character(s). '
        f'The classic FILE_ID.DIZ boundary is shown as 45 columns / 10 lines; overflow is highlighted instead of rewrapped.'
    )
    if overflow_count:
        note += f' {overflow_count} line(s) exceed 45 columns.'
    body = f'''
<h1>{html.escape(title)}</h1>
<p class="format-note diz-note">{html.escape(note)}</p>
<div class="diz-card" aria-label="Fixed-width DIZ preview">
  <div class="diz-ruler">{html.escape(diz_ruler())}</div>
  {''.join(rendered_lines)}
</div>
'''
    return body, [Heading(level=1, text=title, identifier='diz')]


def render_markdown_to_html(text: str) -> tuple[str, list[Heading]]:
    if markdown is None:
        escaped = html.escape(text)
        return f"<pre><code>{escaped}</code></pre><p><strong>Missing dependency:</strong> install Markdown and Pygments.</p>", []

    text = preprocess_task_lists(text)
    md = markdown.Markdown(
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "admonition",
            "codehilite",
            "nl2br",
        ],
        extension_configs={
            "toc": {
                "permalink": "#",
                "slugify": slugify_unicode,
            },
            "codehilite": {
                "guess_lang": False,
                "linenums": False,
                "use_pygments": True,
            },
        },
        output_format="html5",
    )
    body = md.convert(text)
    headings = flatten_toc_tokens(getattr(md, "toc_tokens", []))
    return body, headings


def main() -> int:
    QApplication.setApplicationName(APP_NAME)
    QApplication.setOrganizationName("Zeittresor")
    app = QApplication(sys.argv)
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    window = MarkdownViewDesk(initial)
    window.show()
    QTimer.singleShot(0, window.raise_)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
