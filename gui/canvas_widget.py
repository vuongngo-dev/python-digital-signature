"""
Canvas Widget Module
====================

This module provides the `CanvasWidget` class which allows users to either manually draw 
their digital signature or import an existing signature image. The resulting signature 
can be exported as a base64 encoded PNG string.
"""

import base64
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QImage, QMouseEvent, QPaintEvent, QResizeEvent
from PyQt6.QtCore import Qt, QPoint


class CanvasWidget(QWidget):
    """
    A custom QWidget that acts as a canvas for drawing or loading signature images.
    
    Features:
        - Free-hand drawing with mouse events.
        - Importing and scaling an external image to fit the canvas.
        - Exporting the canvas content to a base64 encoded PNG string.
        - Clearing the canvas.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Initializes the CanvasWidget.

        Args:
            parent (QWidget | None): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setMinimumSize(400, 200)
        
        # Initialize the underlying image for drawing
        self.image = QImage(self.size(), QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.white)
        
        # Drawing state variables
        self.drawing: bool = False
        self.last_point: QPoint = QPoint()
        
        # Pen configuration
        self.pen_color: Qt.GlobalColor = Qt.GlobalColor.black
        self.pen_width: int = 3

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handles the resize event to ensure the underlying image buffer 
        is resized accordingly without losing the existing drawing.

        Args:
            event (QResizeEvent): The resize event.
        """
        if self.width() > self.image.width() or self.height() > self.image.height():
            new_width = max(self.width(), self.image.width())
            new_height = max(self.height(), self.image.height())
            
            new_image = QImage(new_width, new_height, QImage.Format.Format_ARGB32)
            new_image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(new_image)
            painter.drawImage(QPoint(0, 0), self.image)
            painter.end()  # Always end the painter to free resources
            
            self.image = new_image
            
        super().resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse press event to start drawing.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse move event to draw lines as the mouse is dragged.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            self.draw_line_to(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handles the mouse release event to stop drawing.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.draw_line_to(event.pos())
            self.drawing = False

    def draw_line_to(self, end_point: QPoint) -> None:
        """
        Draws a line from the last recorded point to the current end point.

        Args:
            end_point (QPoint): The current mouse position.
        """
        painter = QPainter(self.image)
        
        # Configure the pen for smooth lines
        pen = QPen(
            self.pen_color, 
            self.pen_width, 
            Qt.PenStyle.SolidLine, 
            Qt.PenCapStyle.RoundCap, 
            Qt.PenJoinStyle.RoundJoin
        )
        painter.setPen(pen)
        painter.drawLine(self.last_point, end_point)
        painter.end()  # Close the painter to avoid memory leaks
        
        self.last_point = end_point
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paints the underlying image buffer onto the widget.

        Args:
            event (QPaintEvent): The paint event specifying the region to update.
        """
        painter = QPainter(self)
        dirty_rect = event.rect()
        painter.drawImage(dirty_rect, self.image, dirty_rect)
        painter.end()

    def clear(self) -> None:
        """
        Clears the canvas by filling it with a white background.
        """
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def load_image(self, file_path: str) -> bool:
        """
        Loads an external image file and centers it on the canvas, scaling 
        it down if necessary while preserving the aspect ratio.

        Args:
            file_path (str): The absolute or relative path to the image file.

        Returns:
            bool: True if the image was successfully loaded, False otherwise.
        """
        img = QImage(file_path)
        if img.isNull():
            return False
            
        # Reset the canvas background to white before drawing the new image
        self.image.fill(Qt.GlobalColor.white)
        
        painter = QPainter(self.image)
        # Scale the imported image to fit within the canvas size
        scaled_img = img.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Calculate coordinates to center the image
        x_offset = (self.width() - scaled_img.width()) // 2
        y_offset = (self.height() - scaled_img.height()) // 2
        
        painter.drawImage(x_offset, y_offset, scaled_img)
        painter.end()
        
        self.update()
        return True

    def get_base64_image(self) -> str:
        """
        Encodes the current canvas drawing to a base64 PNG string.

        This base64 string is primarily used to embed the visual signature 
        inside the signed JSON envelope/document.

        Returns:
            str: The base64 encoded string of the PNG image.
        """
        from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
        
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        
        self.image.save(buffer, "PNG")
        buffer.close()
        
        return base64.b64encode(byte_array.data()).decode('utf-8')
