from abc import ABC, abstractmethod
from automata.base.exceptions import InitialStateError

class MachineModel(ABC):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.states = {node.name for node in self.nodes}
        self.input_symbols = {edge.symbol for edge in self.edges}

        self.initial_state = None
        self.final_states = set()

        for node in self.nodes:
            if node.is_initial:
                self.initial_state = node.name
            if node.is_final:
                self.final_states.add(node.name)

        #Raise error if no initial state was set when walking through nodes
        if self.initial_state is None:
            raise InitialStateError

    @abstractmethod
    # Builds and returns a machine subclass from the specific machine builder classes
    def build(self):
        pass