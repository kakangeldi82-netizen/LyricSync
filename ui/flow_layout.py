from PyQt6.QtWidgets import QLayout, QLayoutItem
from PyQt6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """Widget'ları soldan sağa dizip sığmayınca alt satıra kaydıran layout."""

    def __init__(self, parent=None, margin: int = 0, hspacing: int = 8, vspacing: int = 6):
        super().__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items: list[QLayoutItem] = []
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        # Tüm item'lar tek satırda yan yana dizilseydi kaplayacağı toplam
        # genişlik/yükseklik. minimumSize() burada YANLIŞ çünkü o sadece
        # tek bir (en büyük) item'ın boyutunu döndürür; bu da LineWidget'ın
        # tek kelime genişliğinde sıkışmasına ve diğer kelimelerin
        # görünmemesine yol açıyordu.
        width = 0
        height = 0
        for item in self._items:
            hint = item.sizeHint()
            width += hint.width() + self._hspacing
            height = max(height, hint.height())
        if width > 0:
            width -= self._hspacing
        m = self.contentsMargins()
        return QSize(width + m.left() + m.right(), height + m.top() + m.bottom())

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        m = self.contentsMargins()
        effective = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y = effective.x(), effective.y()
        line_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._hspacing
            if next_x - self._hspacing > effective.right() and line_height > 0:
                x = effective.x()
                y += line_height + self._vspacing
                next_x = x + hint.width() + self._hspacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y() + m.bottom()
