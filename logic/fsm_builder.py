from logic.machine_model import MachineModel
from automata.fa.nfa import NFA
from graph_items.edge_item import EdgeItem
from graph_items.node_item import NodeItem

class FSMBuilder(MachineModel):
    # Self will now contain a MachineModel object within it (type of inheritence)
    def build(self):
        # Get the transitions and edges to create a dictionary in the form
        # 'start state' : {'symbol': 'end state', 'symbol': 'end state'}
        # Basically you're building the transitions dictionary
        
        nfa_transitions = {}
        for node in self.nodes:
            curr_state_transitions = {}
            for edge in node.edges:
                if edge.symbol not in curr_state_transitions:
                    curr_state_transitions[edge.symbol] = set()
                curr_state_transitions[edge.symbol].add(edge.node2.name)
            nfa_transitions[node.name] = curr_state_transitions
        
        nfa = NFA(
            states = self.states,
            input_symbols = self.input_symbols,
            transitions = nfa_transitions,
            initial_state = self.initial_state,
            final_states = self.final_states
            )

        ##For debug use - delete later
        for t in nfa.iter_transitions():
            print(t)
        return nfa
        
