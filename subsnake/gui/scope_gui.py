from PySide6.QtCore import QPointF, Qt, QTimer, QMutexLocker
from PySide6.QtWidgets import (
    QGroupBox, QGraphicsScene, QSizePolicy,
    QGraphicsView, QGraphicsPathItem, QGridLayout,
)
from PySide6.QtGui import (
    QPolygonF, QPainterPath, QPen,
    QColor, QPainter
)
import numpy as np

class ScopeGUI(QGroupBox):
    def __init__(self, scope_mutex, scope_buffer, scope_frames):
        super().__init__()
        self.scope_mutex = scope_mutex
        self.scope_buffer = scope_buffer
        self.scope_frames = scope_frames

        self.test_data_x = np.arange(4096)
        self.test_data_y = np.arange(4096) / 2048.0

        self.scope_timer = QTimer()
        self.scope_timer.setInterval(17) #~60fps
        self.scope_timer.timeout.connect(self.update_display)

        self.scope_scene = QGraphicsScene()
        self.scope_scene.setSceneRect(0.0, 0.0, 4096.0, 2.0)
        self.scope_scene.setBackgroundBrush(Qt.GlobalColor.transparent)
        self.scope_view = QGraphicsView(self.scope_scene)
        self.scope_view.setRenderHint(QPainter.Antialiasing)
        self.scope_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scope_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scope_view.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        scope_size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scope_view.setSizePolicy(scope_size_policy)
        
        self.scope_points_list = [self.test_data_x, self.test_data_y]
        self.scope_points_buffer = np.column_stack(self.scope_points_list)
        self.scope_points = [QPointF(x, y) for x, y in self.scope_points_buffer]
        self.scope_polygon = QPolygonF(self.scope_points)
        self.scope_painter_path = QPainterPath()
        self.scope_painter_path.addPolygon(self.scope_polygon)

        self.scope_pen = QPen(QColor("#b4b4d2"))
        self.scope_pen.setWidth(0)
        self.scope_path = QGraphicsPathItem(self.scope_painter_path)
        self.scope_path.setPen(self.scope_pen)

        self.scope_scene.addItem(self.scope_path)

        layout = QGridLayout()
        layout.addWidget(self.scope_view, 0, 0)

        self.setLayout(layout)
        self.setTitle("scope")
        self.setObjectName("scope_group")
        self.scope_timer.start()

    def update_display(self):
        with QMutexLocker(self.scope_mutex):
            frames = self.scope_frames[0]
            x_coords = np.linspace(0, 4096, frames, dtype=np.float32)
            self.scope_points_list[0] = x_coords
            self.scope_points_list[1] = np.sum(self.scope_buffer[:frames], axis=1)
            self.scope_points_buffer = np.column_stack(self.scope_points_list)
            self.scope_points = [QPointF(x, y+1.0) for x, y in self.scope_points_buffer]
            self.scope_polygon = QPolygonF(self.scope_points)
            self.scope_painter_path = QPainterPath()
            self.scope_painter_path.addPolygon(self.scope_polygon)
            self.scope_path.setPath(self.scope_painter_path)
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scope_view.fitInView(self.scope_scene.sceneRect(), Qt.IgnoreAspectRatio)

    def showEvent(self, event):
        super().showEvent(event)
        self.scope_view.fitInView(self.scope_scene.sceneRect(), Qt.IgnoreAspectRatio)
        