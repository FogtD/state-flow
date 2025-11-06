from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy
from ui.main_window import MachineEditorWindow

class StartupMenu(QWidget):
    def __init__(self):
        super().__init__()

        fsa_select_btn = QPushButton("Finite State Automata")
        fsa_select_btn.clicked.connect(self.show_build_window)
        fsa_select_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        pda_select_btn = QPushButton("Pushdown Automata")
        pda_select_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(fsa_select_btn)
        selection_layout.addWidget(pda_select_btn)
        selection_layout.setContentsMargins(0, 0, 0, 0)
        selection_layout.setSpacing(0)


        self.setFixedHeight(576)
        self.setFixedWidth(432)
        self.setWindowTitle("Machine Selection")
        self.setLayout(selection_layout)


    def show_build_window(self, checked):
        self.w = MachineEditorWindow()
        self.w.show()
        self.hide()