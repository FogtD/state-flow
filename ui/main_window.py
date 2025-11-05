from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QGraphicsScene, QMessageBox, QInputDialog)
from PyQt5.QtCore import QSize
from ui.graph_view import GraphView
from graph_items.node_item import NodeItem
from graph_items.edge_item import EdgeItem
from logic.fsm_builder import FSMBuilder

class PlaceholderMachineScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSceneRect(0,0,1920,1080)

        self.node_counter = 0

    def get_next_node_name(self):
        name = f"q{self.node_counter}"
        self.node_counter += 1
        return name
       
        # Set a node to be an initial node and reset the previous initial node to a regular node
    def set_initial_node(self, new_initial_node):
        current_initial = None

        for item in self.items():
            if isinstance(item, NodeItem) and item.is_initial:
                current_initial = item
                break
    
        if current_initial and current_initial != new_initial_node:
            current_initial.is_initial = False
            current_initial.update()

        new_initial_node.is_initial = True
        new_initial_node.update()

class MachineEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("State Flow Automata Visualizer")
        self.setGeometry(100, 100, 1200, 800)

        self.scene = PlaceholderMachineScene()
        self.view = GraphView(self.scene)
        
        self.cursor_button = QPushButton("Cursor")
        self.node_button = QPushButton("Place Node")
        self.edge_button = QPushButton("Place Edge")
        self.test_button = QPushButton("Test String")
           
        # Sets the user's mouse mode to the correct type for placing edges/nodes
        self.cursor_button.clicked.connect(lambda: self.view.set_mode("none"))
        self.node_button.clicked.connect(lambda: self.view.set_mode("node_place"))
        self.edge_button.clicked.connect(lambda: self.view.set_mode("edge_start"))
        self.test_button.clicked.connect(self.test_string)
        
        # Defining the layout for the node and edge buttons
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.cursor_button)
        control_layout.addWidget(self.node_button)
        control_layout.addWidget(self.edge_button)
        control_layout.addWidget(self.test_button)
        control_layout.addStretch(1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)

        main_layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def test_string(self):
        # Get the information for the machine built via the GUI
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        edges = [item for item in self.scene.items() if isinstance(item, EdgeItem)]
    
        # Make sure there are nodes for building the machine
        if not nodes:
            QMessageBox.warning(self, "Error", "No states in the automaton!")
            return
    
        try:
            # Build the DFA
            builder = FSMBuilder(nodes, edges)
            self.dfa = builder.build()
        
            # Test the user's string
            test_input, success = QInputDialog.getText(self, "Test String", "Enter string to test:")
            if success:
                result = self.dfa.accepts_input(test_input)
                status = "ACCEPTED" if result else "REJECTED"
                QMessageBox.information(self, "Result", f"String '{test_input}' is {status}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")