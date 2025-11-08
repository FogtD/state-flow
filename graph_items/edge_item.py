from PyQt5.QtWidgets import QGraphicsLineItem, QMenu, QGraphicsSimpleTextItem, QGraphicsItem
from PyQt5.QtCore import QLineF, Qt, QPointF
from PyQt5.QtGui import QPen, QPolygonF
import math
from graph_items.node_item import NodeItem


class EdgeItem(QGraphicsLineItem):
    def __init__(self, node1: NodeItem, node2: NodeItem):
        super().__init__()
        self.node1 = node1
        self.node2 = node2

        # Edges will be in black with thickness 2
        self.setPen(QPen(Qt.black, 2))

        # Edges will appear below nodes
        self.setZValue(0)

        self.symbol = ""
        self.text_item = QGraphicsSimpleTextItem(self.symbol)
        self.text_item.setZValue(1)

        # Remove this line:
        # self.arrow_head = QGraphicsPolygonF()

        self.node1.edges.append(self)
        if self.node1 != self.node2:
            self.node2.edges.append(self)
    
        self.update_position()
        
        # This function actually draws the line and will be called whenever an edge is created or a node is moved that already has an edge
        self.update_position()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSceneChange and value:
            value.addItem(self.text_item)
        return super().itemChange(change, value)

    def set_symbol(self, symbol):
        self.symbol = symbol
        if self.symbol == "":
            self.symbol = "λ"
        self.text_item.setText(self.symbol)
        self.update_position()

    def update_position(self):
        if self.node1 == self.node2:
            line = QLineF(self.node1.pos(), self.node2.pos())
            self.setLine(line)
            mid_point = self.node1.pos() + QPointF(0, -self.node1.RADIUS * 2)
        else:
            # Calculate line from center to center
            line = QLineF(self.node1.pos(), self.node2.pos())
            
            # Shorten the line so it starts and ends at the edge of the circles
            angle = math.atan2(line.dy(), line.dx())
            
            start_point = QPointF(
                self.node1.pos().x() + self.node1.RADIUS * math.cos(angle),
                self.node1.pos().y() + self.node1.RADIUS * math.sin(angle)
            )
            
            end_point = QPointF(
                self.node2.pos().x() - self.node2.RADIUS * math.cos(angle),
                self.node2.pos().y() - self.node2.RADIUS * math.sin(angle)
            )
            
            self.setLine(QLineF(start_point, end_point))
            
            # Calculate midpoint for text
            mid_point = (start_point + end_point) / 2

        # Position text above the line
        text_rect = self.text_item.boundingRect()
        offset_pos = mid_point - QPointF(text_rect.width() / 2, text_rect.height() + 5)
        self.text_item.setPos(offset_pos)

    def paint(self, painter, option, widget):
        # Draw the line
        super().paint(painter, option, widget)
        
        if self.node1 != self.node2:
            # Draw arrow head
            line = self.line()
            angle = math.atan2(-line.dy(), line.dx())
            
            arrow_size = 10
            arrow_p1 = line.p2() - QPointF(
                math.cos(angle + math.pi / 6) * arrow_size,
                math.sin(angle + math.pi / 6) * arrow_size
            )
            arrow_p2 = line.p2() - QPointF(
                math.cos(angle - math.pi / 6) * arrow_size,
                math.sin(angle - math.pi / 6) * arrow_size
            )
            
            arrow_head = QPolygonF([line.p2(), arrow_p1, arrow_p2])
            
            painter.setBrush(Qt.black)
            painter.drawPolygon(arrow_head)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete Transition")
        action = menu.exec_(event.screenPos())

        if action == delete_action:
            self.removal()
            # if self.scene():
            #     self.scene().removeItem(self.text_item)

            # self.scene().removeItem(self)
            
            # if self in self.node1.edges:
            #     self.node1.edges.remove(self)
            # if self.node1 != self.node2:
            #     if self in self.node2.edges:
            #         self.node2.edges.remove(self)

    def removal(self):
        if self.scene():
            self.scene().removeItem(self.text_item)

        self.scene().removeItem(self)
        
        if self in self.node1.edges:
            self.node1.edges.remove(self)
        if self.node1 != self.node2:
            if self in self.node2.edges:
                self.node2.edges.remove(self)
        
