from logic.machine_model import MachineModel
from automata.fa.nfa import NFA
from graph_items.edge_item import EdgeItem
from graph_items.node_item import NodeItem

class FSMBuilder(MachineModel):

    def build(self):
        nfa_transitions = {}
        for node in self.nodes:
            curr_state_transitions = {}
            for edge in node.out_edges:
                edge_sym = edge.symbol

                #Convert lambda to empty string for NFA machine to handle
                if edge_sym == "λ":
                    edge_sym = ''

                if edge_sym not in curr_state_transitions:
                    curr_state_transitions[edge_sym] = set()
                curr_state_transitions[edge_sym].add(edge.target_node.name)
            nfa_transitions[node.name] = curr_state_transitions
        
        nfa = NFA(
            states = self.states,
            input_symbols = self.input_symbols,
            transitions = nfa_transitions,
            initial_state = self.initial_state,
            final_states = self.final_states
            )

        return nfa
        
