from dataclasses import dataclass
from typing import List, Dict
import math

@dataclass
class Node:
    piece: bytes
    pos: int
    length: int
    node_id: int
    connections: List['Node']
    score: float = 0.0
    cumulative_score: float = 0.0
    gamma: float = 0.0

    def debug_string(self):
        return (f"Node(piece={self.piece.decode()}, pos={self.pos}, "
                f"length={self.length}, node_id={self.node_id})")

class Lattice:
    alpha: List[float] = []
    beta: List[float] = []
    def __init__(self, sentence:str, probability_distribution:Dict[str, float]):
        self.sentence = sentence
        self.size = len(sentence)
        self.sentence_utf8 = self.sentence.encode('utf-8')
        self.surface = memoryview(self.sentence_utf8)
        self.node_id_counter = 2
        self.nodes = []
        self.begin_nodes: Dict[int, List[Node]] = {}
        self.end_nodes: Dict[int, List[Node]] = {}
        self.byte_offsets = [0]
        for ch in sentence:
            self.byte_offsets.append(self.byte_offsets[-1] + len(ch.encode('utf-8')))
        self._create_base_structure()
        self.generate_lattice(probability_distribution)
        self._connect_nodes()

    def _create_base_structure(self):
        self.bos = Node(piece=b"<BOS>", pos=-1, length=1, node_id=0, connections=[], score=1.0)
        self.eos = Node(piece=b"<EOS>", pos=len(self.sentence), length=1, node_id=1, connections=[], score=1.0)
        self.begin_nodes = {i: [] for i in range(-1, self.size + 1)}
        self.end_nodes = {i: [] for i in range(-1, self.size + 2)}

        self.begin_nodes[-1].append(self.bos)
        self.end_nodes[0].append(self.bos)
        self.begin_nodes[self.size].append(self.eos)
        self.end_nodes[self.size+1].append(self.eos)

    def generate_lattice(self, probability_distribution:Dict[str, float]):
        for i in range(self.size):
            for j in range(1, self.size - i + 1):
                end = i + j
                sb, eb = self.byte_offsets[i], self.byte_offsets[i+j]
                node_bytes = memoryview(self.sentence_utf8)[sb:eb]
                if node_bytes in [b"<BOS>", b"<EOS>"]:
                    continue
                if node_bytes.tobytes().decode() not in probability_distribution:
                    continue
                probabilty = probability_distribution.get(node_bytes.tobytes().decode(), -math.inf)

                node = Node(
                    piece=node_bytes,
                    pos=i,
                    length=j,
                    node_id=self.node_id_counter,
                    score=probabilty,
                    connections=[]
                )
                self.node_id_counter += 1

                self.begin_nodes[i].append(node)
                self.end_nodes[end].append(node)
                self.nodes.append(node)

        
        self.nodes.extend([self.bos, self.eos])

    def remove_node(self, node:Node):
        # Remove node from begin and end nodes
        for pos in self.begin_nodes:
            for i in self.begin_nodes[pos]:
                if i == node:
                    self.begin_nodes[pos].remove(i)
        for pos in self.end_nodes:
            for i in self.end_nodes[pos]:
                if i == node:
                    self.end_nodes[pos].remove(i)
        for i in self.nodes:
            if i == node:
                self.nodes.remove(i)
        # Remove node from connections
        for i in self.nodes:
            if node in i.connections:
                i.connections.remove(node)

    def _connect_nodes(self):
        # Create connections between nodes
        for end_pos in self.end_nodes:
            for node in self.end_nodes[end_pos]:
                node.connections.extend(self.begin_nodes.get(end_pos, []))

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
    
