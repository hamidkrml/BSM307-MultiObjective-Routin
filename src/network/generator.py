"""
Ağ üreticisi
BSM307 - Güz 2025
"""

from typing import Tuple

import networkx as nx

from ..utils.logger import get_logger
from ..utils.random_seed import set_seed
from ..utils.graph_helpers import add_node_attributes, add_edge_attributes

logger = get_logger(__name__)


class RandomNetworkGenerator:
    """Erdos–Renyi tabanlı rastgele ağ üretimi için iskelet."""

    def __init__(self, num_nodes: int = 250, edge_prob: float = 0.02, seed: int = 42):
        self.num_nodes = num_nodes
        self.edge_prob = edge_prob
        self.seed = seed
        logger.info(
            "Initialized RandomNetworkGenerator nodes=%s, p=%s, seed=%s",
            num_nodes,
            edge_prob,
            seed,
        )

    def generate(self) -> nx.Graph:
        """TODO: Düğüm/bağ attribute atamaları ve doğrulaması ekle."""
        set_seed(self.seed)
        graph = nx.erdos_renyi_graph(self.num_nodes, self.edge_prob, seed=self.seed)
        logger.info("Generated graph with %d nodes and %d edges", graph.number_of_nodes(), graph.number_of_edges())
        return graph

    def attach_attributes(self, graph: nx.Graph) -> nx.Graph:
        """Örnek attribute ekleme akışı."""
        node_attrs, edge_attrs = self._sample_attributes(graph)
        add_node_attributes(graph, node_attrs)
        add_edge_attributes(graph, edge_attrs)
        return graph

    def _sample_attributes(self, graph: nx.Graph) -> Tuple[dict, dict]:
        """TODO: Gerçekçi attribute dağılımlarını tanımla."""
        node_attrs = {n: {"processing_delay": 0.0, "reliability": 0.999} for n in graph.nodes}
        edge_attrs = {
            (u, v): {"bandwidth": 1.0, "delay": 1.0, "reliability": 0.999}
            for u, v in graph.edges
        }
        return node_attrs, edge_attrs

