from os import name
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QMenu, QAction, QGraphicsSimpleTextItem, QInputDialog
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainterPath, QFont, QBrush

class NodeItem(QGraphicsEllipseItem):
    RADIUS = 20

    def __init__(self, pos: QPointF, name: str):
        #Constructor of the form QGraphicsElippseitem(x position, y position, width, height)
        super().__init__(-self.RADIUS, -self.RADIUS, 2*self.RADIUS, 2*self.RADIUS)
        self.setPos(pos)
        self.scene_ref = self.scene

        # Set the relevant internal variables to let the user move the node around
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        # Fill the node in blue
        self.setBrush(Qt.blue)
        # Nodes will be on top, above edges
        self.setZValue(1)

        # Will contain the list of edges associated with a node
        self.edges = []

        # Determines if a node is a final or initial node
        self.is_initial = False
        self.is_final = False

        self.name = name
        self.text_item = QGraphicsSimpleTextItem(self.name, self)
        
        if self.name == "q0":
            self.is_initial = True

        font = QFont()
        font.setPointSize(10)
        self.text_item.setFont(font)
        self.text_item.setBrush(Qt.white)

        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)


    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.is_initial:
            # Save the current painter state
            painter.save()
        
            painter.setPen(QPen(Qt.darkGreen, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)  # Don't fill the arrow
        
            # Draw arrow line
            painter.drawLine(QPointF(-self.RADIUS * 2.5, 0), QPointF(-self.RADIUS, 0))
        
            # Draw arrow head as separate lines
            painter.drawLine(QPointF(-self.RADIUS, 0), QPointF(-self.RADIUS - 5, -5))
            painter.drawLine(QPointF(-self.RADIUS, 0), QPointF(-self.RADIUS - 5, 5))
        
            # Restore the painter state
            painter.restore()
    
        if self.is_final:
            # Save painter state
            painter.save()
        
            # Create a double circle if it's a final node
            painter.setPen(QPen(Qt.black, 3))
            painter.setBrush(Qt.NoBrush)  # Don't fill the inner circle
            painter.drawEllipse(-self.RADIUS + 5, -self.RADIUS + 5, 2 * self.RADIUS - 10, 2 * self.RADIUS - 10)
        
            # Restore painter state
            painter.restore()
    
    # This is called whenever QGraphicsItem is moved, so we'll have to update the edges associated with the moved node
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    # Right click menu for designated a starting and final node, as well as deleting nodes
    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete State")
        rename_action = menu.addAction("Rename State")
        menu.addSeparator()

        start_action = QAction("Set as Start State")
        start_action.setCheckable(True)
        start_action.setChecked(self.is_initial)
        menu.addAction(start_action)

        final_action = QAction("Toggle Final State")
        final_action.setCheckable(True)
        final_action.setChecked(self.is_final)
        menu.addAction(final_action)

        # Get the action from where the user clicked in the menu
        action = menu.exec_(event.screenPos())

        if action == delete_action:
            for edge in list(self.edges):
                other_node = edge.node1 if edge.node2 == self else edge.node2

                if edge in other_node.edges:
                    other_node.edges.remove(edge)

                if self.scene():
                    self.scene().removeItem(edge)
                    
            self.scene().removeItem(self)

        elif action == rename_action:
            new_name, success = QInputDialog.getText(self, "Rename State", "Enter new name:", text=self.name)
            if success and new_name:
                self.name = new_name
                self.text_item.setText(self.name)

                text_rect = self.text_item.boundingRect()
                self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
                self.update()


        elif action == start_action:
            if self.scene():
                self.scene().set_initial_node(self)
        elif action == final_action:
                    self.is_final = not self.is_final
                    self.update()