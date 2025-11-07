from logic.machine_model import MachineModel
from automata.pda.npda import NPDA
from graph_items.edge_item import EdgeItem
from graph_items.node_item import NodeItem

class PDABuilder(MachineModel):
    EMPTY_STACK_SYMBOL = 'Z'

    def __init__(self, nodes, edges):
        super().__init__(nodes, edges)
        self.stack_symbols = {edge.stack_top for edge in self.edges} | {self.EMPTY_STACK_SYMBOL}

    # def build(self):

    #     pda_transitions = {}
    #     for node in self.nodes:
    #         curr_state_transitions = {}
    #         for edge in node.edges:
    #             if edge.symbol not in curr_state_transitions:
    #                 curr_state_transitions[edge.symbol] = dict()
                
    #             #If stack_top symbol is not yet a key value in the dictionary held by current edge symbol for this node, then add that key value
    #             if edge.stack_top not in curr_state_transitions[edge.symbol]:
    #                 #Nested dictionary set that holds 
    #                 curr_state_transitions[edge.symbol][edge.top_stack] = set()
                
    #             #Check if 

    #             #No altering stack
    #             if edge.stack_action == edge.stack_top:
    #                 curr_state_transitions[edge.symbol][edge.top_stack].add((edge.node.name2, edge.stack_action))
    #             #Pop action
    #             elif edge.stack_action == '':
    #                 curr_state_transitions[edge.symbol][edge.top_stack].add((edge.node.name2, ''))
    #             #Push action
    #             else:
    #                 #Get symbols pushed on to stack, multiple symbols can be pushed at once
    #                 push_symbols = edge.stack_action[:-1]
    #                 curr_state_transitions[edge.symbol][edge.top_stack].add((edge.node.name2, (push_symbols, edge.top_stack)))

    #             curr_state_transitions[edge.symbol].add(edge.node2.name)
    #         pda_transitions[node.name] = curr_state_transitions
        

    #     pda = NPDA(
    #         states = self.states,
    #         input_symbols = self.input_symbols,
    #         stack_symbols = self.stack_symbols,
    #         transitions= pda_transitions,
    #         initial_state = self.initial_state,
    #         initial_stack_symbol = self.EMPTY_STACK_SYMBOL,
    #         final_states = self.final_states,
    #         acceptance_mode='final_state'
    #     )

    #     return pda