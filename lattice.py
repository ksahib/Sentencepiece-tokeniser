from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Node:
    piece: bytes
    pos: int 
    length: int 
    node_id: int
    connections: List['Node']

    def debug_string(self):
        return (f"Node(piece={self.piece.decode()}, pos={self.pos}, "
                f"length={self.length}, node_id={self.node_id})")


class Lattice:
    def __init__(self, sentence:str):
        self.sentence = sentence
        self.size = len(sentence)
        self.sentence_utf8 = self.sentence.encode('utf-8')
        self.surface = memoryview(self.sentence_utf8)
        self.node_id_counter = 0
        self.nodes = []
        self.begin_nodes: Dict[int, List[Node]] = {}
        self.end_nodes: Dict[int, List[Node]] = {}

        self._create_base_structure()
        self.generate_lattice()

    def _create_base_structure(self):
        self.bos = Node(piece=b"<BOS>", pos=-1, length=0, node_id=self.node_id_counter, connections=[])
        self.node_id_counter += 1
        self.eos = Node(piece=b"<EOS>", pos=len(self.sentence), length=0, node_id=self.node_id_counter, connections=[])
        self.node_id_counter += 1
        self.begin_nodes = {i: [] for i in range(-1, self.size + 1)}
        self.end_nodes = {i: [] for i in range(-1, self.size + 1)}

        self.begin_nodes[-1].append(self.bos)
        self.end_nodes[0].append(self.bos)

    def generate_lattice(self):
        for i in range(self.size):
            for j in range(1, self.size - i + 1):
                end = i + j
                node_bytes = self.sentence_utf8[i:end]

                node = Node(
                    piece=node_bytes,
                    pos=i,
                    length=j,
                    node_id=self.node_id_counter,
                    connections=[]
                )
                self.node_id_counter += 1

                self.begin_nodes[i].append(node)
                self.end_nodes[end].append(node)
                self.nodes.append(node)

        self.begin_nodes[self.size].append(self.eos)
        self.end_nodes[self.size].append(self.eos)
        self.nodes.append(self.eos)

        for end_node, nodes in self.end_nodes.items():
            for node in nodes:
                node.connections.extend(self.begin_nodes.get(end_node, []))

    def print_lattice(self):
        print(f"Sentence: {self.sentence}")
        for pos in sorted(self.begin_nodes.keys()):
            if pos == -1:
                print("\n[START]")
            elif pos == self.size:
                print("\n[END]")
            else:
                print(f"\nPosition {pos}:")
                
            for node in self.begin_nodes[pos]:
                piece_str = bytes(node.piece).decode()
                if piece_str in ["<BOS>", "<EOS>"]:
                    continue
                    
                connections = ", ".join([bytes(n.piece).decode() for n in node.connections])
                print(f"  {piece_str} ({node.pos}-{node.pos+node.length}) → [{connections}]")
    
lattice = Lattice("cat")
lattice.print_lattice()