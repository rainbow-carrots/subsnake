from PySide6.QtCore import QPointF, Qt, QTimer, QMutexLocker
from PySide6.QtWidgets import (
    QGroupBox, QGraphicsScene, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsView, QGraphicsPathItem, QGridLayout, QGraphicsItem
)
from PySide6.QtGui import (
    QPolygonF, QPainterPath, QPen,
    QColor, QPainter
)
import numpy as np

class ScopeGUI(QGroupBox):
    def __init__(self, scope_mutex, scope_buffer, scope_frames, scope_head):
        super().__init__()
        self.scope_mutex = scope_mutex
        self.scope_buffer = scope_buffer
        self.scope_frames = scope_frames
        self.scope_head = scope_head

        self.test_data_x = np.arange(4096)
        self.test_data_y = np.arange(4096) / 2048.0

        self.scope_timer = QTimer()
        self.scope_timer.setInterval(33) #~30fps
        self.scope_timer.timeout.connect(self.update_display)

        self.scope_scene = QGraphicsScene()
        self.scope_scene.setSceneRect(0.0, 0.0, 2048.0, 2.0)
        self.scope_scene.setBackgroundBrush(Qt.GlobalColor.transparent)
        self.scope_view = QGraphicsView(self.scope_scene)
        self.scope_view.setRenderHint(QPainter.Antialiasing)
        self.scope_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scope_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scope_view.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scope_view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        scope_size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scope_view.setSizePolicy(scope_size_policy)
        
        self.scope_points_list = [self.test_data_x, self.test_data_y]
        self.scope_points_buffer = np.column_stack(self.scope_points_list)
        self.scope_points = [QPointF(x, y) for x, y in self.scope_points_buffer]
        self.scope_polygon = QPolygonF(self.scope_points)
        self.scope_painter_path = QPainterPath()
        self.scope_painter_path.addPolygon(self.scope_polygon)

        self.scope_pen = QPen(QColor("#b4b4d2"))
        self.scope_pen.setWidth(2)
        self.scope_pen.setCosmetic(True)
        self.scope_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.scope_path = QGraphicsPathItem(self.scope_painter_path)
        self.scope_path.setPen(self.scope_pen)

        self.scope_glow = QGraphicsDropShadowEffect()
        self.scope_glow.setOffset(0.0, 0.0)
        self.scope_glow.setBlurRadius(12)
        self.scope_glow.setColor(QColor("#b4b4d2"))
        self.scope_path.setGraphicsEffect(self.scope_glow)
        self.scope_path.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

        self.scope_scene.addItem(self.scope_path)

        layout = QGridLayout()
        layout.addWidget(self.scope_view, 0, 0)

        self.setLayout(layout)
        self.setTitle("scope")
        self.setObjectName("scope_group")
        self.scope_timer.start()

    def update_display(self):
        with QMutexLocker(self.scope_mutex):
            head_pos = self.scope_head[0]

            scope_flat = np.roll(self.scope_buffer, -head_pos)
            search_start = max(0, len(scope_flat) - 6144)
            search_end = len(scope_flat) - 2048
            search_window = np.sum(scope_flat[search_start:search_end], axis=1)

            kernel = np.ones(15, dtype=np.float32) / 15.0
            smoothed_window = np.convolve(search_window, kernel, mode="same")

            peak_amp = np.max(np.abs(smoothed_window))
            hysteresis_thresh = -0.1*peak_amp if peak_amp > 0 else -.01
                
            zero_crossings = np.where((smoothed_window[:-1] <= 0) & (smoothed_window[1:] > 0))[0]
            valid_crossings = []
            for c in zero_crossings:
                lookback = smoothed_window[max(0, c - 1000):c]
                if len(lookback) > 0 and np.min(lookback) < hysteresis_thresh:
                    valid_crossings.append(c)

            if len(valid_crossings) > 0:
                last_crossing_index = valid_crossings[-1]
                y1 = smoothed_window[last_crossing_index]
                y2 = smoothed_window[last_crossing_index + 1]
                fraction = (0.0 - y1) / (y2 - y1) if y2 != y1 else 0.0
                trigger_index = last_crossing_index + search_start
                stable_scope = scope_flat[trigger_index:trigger_index + 2048]
                x_coords = np.arange(2048, dtype=np.float32) - fraction
            else:
                stable_scope = scope_flat[-2048:]
                x_coords = np.arange(2048, dtype=np.float32)
            self.scope_points_list[0] = x_coords
            self.scope_points_list[1] = np.mean(stable_scope, axis=1)
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
        