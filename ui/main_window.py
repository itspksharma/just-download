from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from downloader import download_handler
from core.utils import ensure_downloads_folder

CATS = {
 "Audio": {"MP3 (High Quality)":"mp3","M4A":"m4a","WebM Audio":"webm_audio"},
 "Video": {"MP4 1080p":"mp4_1080p","MP4 720p":"mp4_720p","MP4 480p":"mp4_480p","WebM 720p":"webm_720p"},
 "Image": {"Image File":"image"}
}

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Just Download 1.0 - Media Downloader")
        self.setGeometry(200,100,950,600)
        self.download_path = ensure_downloads_folder()
        self.theme = "dark"
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()
        header=QLabel("Just Download 1.0"); header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial",20,QFont.Bold)); layout.addWidget(header)

        h=QHBoxLayout()
        self.url_in=QLineEdit(); self.url_in.setPlaceholderText("Enter media URL..."); h.addWidget(self.url_in)
        self.cat_box=QComboBox(); self.cat_box.addItems(CATS.keys()); self.cat_box.currentIndexChanged.connect(self.load_formats); h.addWidget(self.cat_box)
        self.fmt_box=QComboBox(); h.addWidget(self.fmt_box)
        self.start_btn=QPushButton("⬇ Start"); self.start_btn.clicked.connect(self.start); h.addWidget(self.start_btn)
        self.folder_btn=QPushButton("📁 Folder"); self.folder_btn.clicked.connect(self.browse); h.addWidget(self.folder_btn)
        self.theme_btn=QPushButton("🌓 Theme"); self.theme_btn.clicked.connect(self.toggle_theme); h.addWidget(self.theme_btn)
        layout.addLayout(h)
        self.load_formats()

        self.table=QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Sl.No","Title / URL","Format","Status","Progress"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        footer=QLabel("Made by Pawan Kumar Sharma"); footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)

    def load_formats(self):
        self.fmt_box.clear()
        for k in CATS[self.cat_box.currentText()]:
            self.fmt_box.addItem(k)

    def start(self):
        u=self.url_in.text().strip()
        if not u:
            QMessageBox.warning(self,"Error","Enter URL"); return

        fmt=CATS[self.cat_box.currentText()][self.fmt_box.currentText()]
        row=self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row,0,QTableWidgetItem(str(row+1)))
        self.table.setItem(row,1,QTableWidgetItem("Fetching title..."))
        self.table.setItem(row,2,QTableWidgetItem(self.fmt_box.currentText()))
        self.table.setItem(row,3,QTableWidgetItem("⬇ Downloading"))
        pbar=QProgressBar(); pbar.setValue(0); self.table.setCellWidget(row,4,pbar)

        def on_title(r, t): QTimer.singleShot(0, lambda: self.table.setItem(r,1,QTableWidgetItem(t)))
        def on_prog(r, p): QTimer.singleShot(0, lambda: self.table.cellWidget(r,4).setValue(p))
        def on_done(r): QTimer.singleShot(0, lambda: (self.table.setItem(r,3,QTableWidgetItem("✅ Done")), self.table.cellWidget(r,4).setValue(100)))

        download_handler(u, fmt, callback=on_done, progress_callback=on_prog, row_id=row, title_callback=on_title, output_path=self.download_path)

    def browse(self):
        d=QFileDialog.getExistingDirectory(self,"Select Folder",self.download_path)
        if d: self.download_path=d

    def toggle_theme(self):
        self.theme="light" if self.theme=="dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        if self.theme=="dark":
            self.setStyleSheet("""
                QWidget { background:#2e2e2e; color:#f0f0f0; font-family:'Segoe UI'; }
                QPushButton { background:#00BFA5; color:white; padding:5px; border-radius:5px }
                QPushButton:hover{background:#00D8A3;}
                QLineEdit, QComboBox { padding:5px;border-radius:5px;border:1px solid #555;background:#3a3a3a;color:white }
                QHeaderView::section{background:#444;color:white;padding:4px;}
                QTableWidget{background:#1e1e1e;gridline-color:#666;}
            """)
        else:
            self.setStyleSheet("""
                QWidget { background:#fff; color:#000; font-family:'Segoe UI'; }
                QPushButton { background:#1976D2; color:white; padding:5px; border-radius:5px }
                QPushButton:hover{background:#1565C0;}
                QLineEdit, QComboBox { padding:5px;border-radius:5px;border:1px solid #999;background:#f9f9f9;color:black }
                QHeaderView::section{background:#f0f0f0;color:black;padding:4px;}
                QTableWidget{background:#fafafa;gridline-color:#ccc;}
            """)
