from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout


class LyricsDialog(QDialog):
    def __init__(self, parent=None, initial_text: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Şarkı Sözlerini Gir")
        self.resize(520, 500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Şarkı sözlerini satır satır, zaman damgası OLMADAN yapıştır.\n"
            "(Otomatik hizalama bir sonraki adımda yapılacak.)"
        ))

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.text_edit.setPlaceholderText("Satır 1...\nSatır 2...\n...")
        layout.addWidget(self.text_edit, 1)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Devam Et")
        ok_btn.clicked.connect(self.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
