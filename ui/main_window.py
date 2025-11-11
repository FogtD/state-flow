from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QGraphicsScene, QMessageBox, QInputDialog,
                             QMenu, QAction, QToolButton, QLabel)
from PyQt5.QtGui import QBrush, QFont
from PyQt5.QtCore import QSize, Qt
from ui.graph_view import GraphView
from graph_items.node_item import NodeItem
from graph_items.edge_item import EdgeItem
from logic.fsm_builder import FSMBuilder
from automata.base.exceptions import InitialStateError

HIGHLIGHT_COLORS = {
    "active": QBrush(Qt.yellow),
    "accept": QBrush(Qt.green),
    "reject": QBrush(Qt.red)
}


class PlaceholderMachineScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSceneRect(0,0,1920,1080)

        self.node_counter = 0

        # Keep a list of nodes in the machine so you can easily update the highlighting
        self.nodes = {}

    def get_next_node_name(self):
        name = f"q{self.node_counter}"
        self.node_counter += 1
        return name

    # Overrides the addItem method to add the node to our dictionary of nodes whenever they're created
    def addItem(self, item):
        if isinstance(item, NodeItem):
            self.nodes[item.name] = item
        super().addItem(item)

    def removeItem(self, item):
        if isinstance(item, NodeItem):
            if item.name in self.nodes:
                del self.nodes[item.name]
        super().removeItem(item)
       
        # Set a node to be an initial node and reset the previous initial node to a regular node
    def set_initial_node(self, new_initial_node):
            current_initial = None

            for node in self.nodes.values():
                if node.is_initial:
                    current_initial = node
                    break


            if current_initial and current_initial != new_initial_node:
                current_initial.is_initial = False
                current_initial.update()

            new_initial_node.is_initial = True
            new_initial_node.update()

    def get_all_nodes(self):
        return list(self.nodes.values())

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

        # The test button is a drop down menu where you can choose to quick test or step test
        self.test_button = QToolButton()
        self.test_button.setText("Test String")
        self.test_button.setPopupMode(QToolButton.MenuButtonPopup)

        self.test_menu = QMenu()
        self.test_button.setMenu(self.test_menu)

        self.quick_test_action = QAction("Quick Test")
        self.quick_test_action.triggered.connect(self.quick_test_string)
        self.test_menu.addAction(self.quick_test_action)

        self.step_test_action = QAction("Step Test")
        self.step_test_action.triggered.connect(self.start_step_test)
        self.test_menu.addAction(self.step_test_action)

        self.clear_button = QPushButton("Clear")
           
        # Sets the user's mouse mode to the correct type for placing edges/nodes
        self.cursor_button.clicked.connect(lambda: self.view.set_mode("none"))
        self.node_button.clicked.connect(lambda: self.view.set_mode("node_place"))
        self.edge_button.clicked.connect(lambda: self.view.set_mode("edge_start"))
        self.clear_button.clicked.connect(self.clear_graph)
        
        # Defining the layout for the node and edge buttons
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.cursor_button)
        control_layout.addWidget(self.node_button)
        control_layout.addWidget(self.edge_button)
        control_layout.addWidget(self.test_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addStretch(1)

        # UI for controlling the step test
        self.step_test_widget = QWidget()
        self.step_test_layout = QHBoxLayout()
        self.step_string_label = QLabel("")
        font = QFont("Atlas", 14)
        self.step_string_label.setFont(font)

        self.next_step_button = QPushButton("Next Step")
        self.next_step_button.clicked.connect(self.advance_step_test)

        self.reset_step_button = QPushButton("Reset Test")
        self.reset_step_button.clicked.connect(self.reset_step_test)

        self.step_test_layout.addWidget(self.step_string_label)
        self.step_test_layout.addStretch(1)
        self.step_test_layout.addWidget(self.next_step_button)
        self.step_test_layout.addWidget(self.reset_step_button)

        self.step_test_widget.setLayout(self.step_test_layout)

        # Variables for tracking the state of the step test
        self.step_test_nfa = None
        self.step_test_iterator = None
        self.step_test_string = ""
        self.step_test_index = 0
        self.current_step_states = set()

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)

        main_layout.addWidget(self.step_test_widget)
        main_layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.reset_step_test()
    
    def quick_test_string(self):
        self.reset_step_test()

        # Get the information for the machine built via the GUI
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        edges = [item for item in self.scene.items() if isinstance(item, EdgeItem)]
    
        # Make sure there are nodes for building the machine
        if not nodes:
            QMessageBox.warning(self, "Error", "No states in the automaton!")
            return
    
        try:
            # Build the FSM
            builder = FSMBuilder(nodes, edges)
            self.nfa = builder.build()
        
            # Test the user's string
            test_input, success = QInputDialog.getText(self, "Test String", "Enter string to test:")
            if success:
                result = self.nfa.accepts_input(test_input)
                status = "ACCEPTED" if result else "REJECTED"
                QMessageBox.information(self, "Result", f"String '{test_input}' is {status}")
        except InitialStateError as e:
            QMessageBox.warning(self, "Error", "Initial state not set")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def build_nfa(self):
        nodes = self.scene.get_all_nodes()
        edges = [item for item in self.scene.items() if isinstance(item, EdgeItem)]

        try:
            builder = FSMBuilder(nodes, edges)
            return builder.build()
        except InitialStateError as e:
            QMessageBox.warning(self, "Error", "Initial state not set")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            return None

    def start_step_test(self):
        self.reset_step_test()
        self.step_test_nfa = self.build_nfa()

        # Get the user's string and make sure there was no error
        test_input, success = QInputDialog.getText(self, "Test String", "Enter string to test")
        if not success:
            return

        self.step_test_string = test_input
        self.step_test_index = 0

        # The built in read_input_stepwise function in the automata library is a generator which we can iterate through using an iterator
        self.step_test_iterator = self.step_test_nfa.read_input_stepwise(self.step_test_string)

        self.step_test_widget.show()

        self.current_step_states = next(self.step_test_iterator, set())
        self.highlight_nodes(self.current_step_states, "active")
        self.update_string_label()
       
    def advance_step_test(self):
        try:
            # Get the next set of possible states given the input from the iterator
            self.current_step_states = next(self.step_test_iterator)
            self.step_test_index += 1

            # Check if there are any states left to transition to
            if not self.current_step_states:
                self.reset_all_node_highlights()
                self.step_string_label.setText("<b>Test Complete. No possible states to transition to. String REJECTED</b>")
                self.next_step_button.setEnabled(False)
                return

            self.reset_all_node_highlights()
            self.highlight_nodes(self.current_step_states, "active")
            self.update_string_label()
        except StopIteration:
            # This would mean the iterator has nothing left to continue to, meaning the string is exhausted
            self.next_step_button.setEnabled(False)
            self.reset_all_node_highlights()

            # If any of the current states that are possible are final states, then accept the string
            is_accepted = any(state in self.step_test_nfa.final_states for state in self.current_step_states)

            if is_accepted:
                # Accepted nodes are final nodes which we are also in the current state of
                accepted_nodes = {state for state in self.current_step_states if state in self.step_test_nfa.final_states}
                self.highlight_nodes(accepted_nodes, "accept")
                self.step_string_label.setText("<b>Test Complete. String ACCEPTED</b>")
            else:
                # If none of the current states are final states, reject them all
                self.highlight_nodes(self.current_step_states, "reject")
                set.step_string_label.setText("<b>Test Complete. String REJECTED</b>")

    def reset_step_test(self):
        self.step_test_widget.hide()

        self.next_step_button.setEnabled(True)

        self.step_test_nfa = None
        self.step_test_iterator = None
        self.step_test_string = ""
        self.step_test_index = 0
        self.current_step_states = set()

        self.reset_all_node_highlights()
        self.update_string_label()

    def update_string_label(self):
        if not self.step_test_string:
            self.step_string_label.setText("")
            return

        # Check if we've reached the end of the string
        if self.step_test_index >= len(self.step_test_string):
            processed = self.step_test_string
            current = ""
            upcoming = ""
        else:
            processed = self.step_test_string[:self.step_test_index]
            current = self.step_test_string[self.step_test_index]
            upcoming = self.step_test_string[self.step_test_index + 1:]

        # Use HTML for coloring the string to indicate where we are
        self.step_string_label.setText(
            f"<font color='gray'>{processed}</font>"
            f"<font color='blue' style='background-color: yellow;'><b>{current}</b></font>"
            f"<font color='black'>{upcoming}</font>"
        )

    def highlight_nodes(self, node_names, color_key):
        brush = HIGHLIGHT_COLORS[color_key]

        for name in node_names:
            if name in self.scene.nodes:
                self.scene.nodes[name].set_highlight(brush)

    def reset_all_node_highlights(self):
        for node in self.scene.get_all_nodes():
            node.reset_highlight()

    def clear_graph(self):
        #By deleting all nodes all edges connected for each will be deleted too
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.removal()
        self.scene.node_counter = 0 


            