from PyQt5.QtWidgets import QGraphicsLineItem, QMenu, QGraphicsSimpleTextItem, QGraphicsItem, QInputDialog
from PyQt5.QtCore import QLineF, Qt, QPointF
from PyQt5.QtGui import QPen, QPolygonF
import math
from graph_items.node_item import NodeItem


class EdgeItem(QGraphicsLineItem):
    def __init__(self, src_node: NodeItem, target_node: NodeItem):
        super().__init__()
        self.src_node = src_node
        self.target_node = target_node

        # Edges will be in black with thickness 2
        self.setPen(QPen(Qt.black, 2))

        # Edges will appear below nodes
        self.setZValue(0)

        self.symbol = ""
        self.text_item = QGraphicsSimpleTextItem(self.symbol)
        self.text_item.setZValue(1)

        # Remove this line:
        # self.arrow_head = QGraphicsPolygonF()

        self.src_node.edges.append(self)
        self.src_node.out_edges.append(self)

        #Ensure target node, is aware of one of its in-edges
        if self.src_node != self.target_node:
            self.target_node.edges.append(self)
    
        self.update_position()
        
        # This function actually draws the line and will be called whenever an edge is created or a node is moved that already has an edge
        self.update_position()

        # If the edge we're trying to add has other "sibling" edges, make sure we update them too
        for edge in self.src_node.out_edges:
            if edge.target_node == self.target_node and edge != self:
                edge.update_position()

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
        if self.src_node == self.target_node:
            line = QLineF(self.src_node.pos(), self.target_node.pos())
            self.setLine(line)
            mid_point = self.src_node.pos() + QPointF(0, -self.src_node.RADIUS * 2)
        else:
            # Calculate line from center to center
            line = QLineF(self.src_node.pos(), self.target_node.pos())
            
            # Shorten the line so it starts and ends at the edge of the circles
            angle = math.atan2(line.dy(), line.dx())
            
            start_point = QPointF(
                self.src_node.pos().x() + self.src_node.RADIUS * math.cos(angle),
                self.src_node.pos().y() + self.src_node.RADIUS * math.sin(angle)
            )
            
            end_point = QPointF(
                self.target_node.pos().x() - self.target_node.RADIUS * math.cos(angle),
                self.target_node.pos().y() - self.target_node.RADIUS * math.sin(angle)
            )
            
            self.setLine(QLineF(start_point, end_point))
            
            # Calculate midpoint for text
            mid_point = (start_point + end_point) / 2

        # Sibling edges have the same source and target nodes
        sibling_edges = [edge for edge in self.src_node.out_edges if edge.target_node == self.target_node]

        try:
            my_index = sibling_edges.index(self)
        except ValueError:
            my_index = 0

        num_siblings = len(sibling_edges)
        
        text_rect = self.text_item.boundingRect()

        vertical_spacing = text_rect.height() + 2

        if self.src_node == self.target_node:
            # Self-loop: Simple vertical stacking
            base_offset_pos = mid_point - QPointF(text_rect.width() / 2, text_rect.height() + 5)
            # Stack downwards (positive Y)
            stacking_offset = QPointF(0, my_index * vertical_spacing) 
            offset_pos = base_offset_pos + stacking_offset
        else:
            # Regular edge: Offset perpendicular to the line
            line = self.line()
            angle = math.atan2(line.dy(), line.dx())
            # Get perpendicular angle ("above" the line)
            perp_angle = angle - math.pi / 2 
            
            # Unit vector pointing "above"
            perp_vector = QPointF(math.cos(perp_angle), math.sin(perp_angle))
            
            # Base position: centered on the midpoint
            base_text_pos = mid_point - QPointF(text_rect.width() / 2, text_rect.height() / 2)
            
            # Total distance from the line:
            # 5 pixels base, plus the sibling offset
            total_offset_distance = 5 + (my_index * vertical_spacing)
            
            # Final position
            offset_pos = base_text_pos + (perp_vector * total_offset_distance)
            
        self.text_item.setPos(offset_pos)

       

    def paint(self, painter, option, widget):
        # Draw the line
        super().paint(painter, option, widget)
        
        if self.src_node != self.target_node:
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
        change_sym_action = menu.addAction("Change Symbol")
        action = menu.exec_(event.screenPos())

        if action == delete_action:
            self.removal()
        
        if action == change_sym_action:
            graph_view = self.scene().views()[0]
            symbol, success = QInputDialog.getText(graph_view, "Edge Symbol", "Enter transition symbol:")
            if success:
                self.set_symbol(symbol)


    def removal(self):
        try:
            siblings = [edge for edge in self.src_node.out_edges if edge.target_node == self.target_node and edge != self]
        except AttributeError:
            siblings = []

        if self.scene():
            self.scene().removeItem(self.text_item)
            self.scene().removeItem(self)      
        
        if self in self.src_node.edges:
            self.src_node.edges.remove(self)
            self.src_node.out_edges.remove(self)
        if self.src_node != self.target_node:
            if self in self.target_node.edges:
                self.target_node.edges.remove(self)

        for edge in siblings:
            edge.update_position()
        
