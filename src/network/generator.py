"""
Ağ üreticisi
BSM307 - Güz 2025


- 250 düğümlü Erdos-Renyi G(n, p) modeli
- Bağlantı olasılığı P = 0.4
- Bağlı (connected) graf garantisi veya S-D çiftleri arasında yol garantisi
"""

from typing import Tuple

import networkx as nx

from ..utils.logger import get_logger
from ..utils.random_seed import set_seed
from ..utils.graph_helpers import add_node_attributes, add_edge_attributes

logger = get_logger(__name__)


class RandomNetworkGenerator:
    """
    Erdos–Renyi tabanlı rastgele ağ üretimi.
    
    PDF'te belirtilen gereksinimlere göre:
    - N = 250 düğüm
    - P = 0.4 bağlantı olasılığı
    - Bağlı graf garantisi
    """

    def __init__(self, num_nodes: int = 250, edge_prob: float = 0.4, seed: int = 42):
        """
        Args:
            num_nodes: Düğüm sayısı (varsayılan: 250)
            edge_prob: Bağlantı olasılığı (varsayılan: 0.4 - PDF gereksinimi)
            seed: Rastgele tohum değeri
        """
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
        """
        250 düğümlü Erdos-Renyi graf üretir.
        
        PDF gereksinimleri:
        - Erdős-Rényi G(n, p) modeli kullanılır
        - P = 0.4 bağlantı olasılığı
        - Bağlılık kontrolü yapılır
        
        Returns:
            Bağlı (connected) networkx.Graph objesi
        """
        set_seed(self.seed)
        
        # Erdos-Renyi graf üretimi
        graph = nx.erdos_renyi_graph(self.num_nodes, self.edge_prob, seed=self.seed)
        
        # Bağlılık kontrolü ve garantisi
        if not nx.is_connected(graph):
            logger.warning(
                "Generated graph is not connected. Attempting to connect components..."
            )
            # Bağlı bileşenleri birleştir
            components = list(nx.connected_components(graph))
            if len(components) > 1:
                # En büyük bileşeni bul
                largest_component = max(components, key=len)
                # Diğer bileşenleri en büyük bileşene bağla
                for component in components:
                    if component != largest_component:
                        # Her bileşenden bir düğüm seç ve bağla
                        node_from_component = next(iter(component))
                        node_to_largest = next(iter(largest_component))
                        graph.add_edge(node_from_component, node_to_largest)
                        logger.debug(
                            "Connected component %s to largest component via edge (%s, %s)",
                            component,
                            node_from_component,
                            node_to_largest,
                        )
        
        # Bağlılık garantisi kontrolü
        if not nx.is_connected(graph):
            logger.error("Failed to create connected graph. Retrying with different seed...")
            # Alternatif: Yeniden üret (daha yüksek edge_prob ile)
            set_seed(self.seed + 1)
            graph = nx.erdos_renyi_graph(self.num_nodes, min(0.5, self.edge_prob * 1.2), seed=self.seed + 1)
            if not nx.is_connected(graph):
                # Son çare: Minimum spanning tree ekle
                if graph.number_of_nodes() > 1:
                    mst = nx.minimum_spanning_tree(nx.complete_graph(self.num_nodes))
                    graph = nx.compose(graph, mst)
        
        # Final kontrol
        is_connected = nx.is_connected(graph)
        logger.info(
            "Generated graph with %d nodes, %d edges, connected=%s",
            graph.number_of_nodes(),
            graph.number_of_edges(),
            is_connected,
        )
        
        if not is_connected:
            logger.warning(
                "Graph is still not connected. Some S-D pairs may not have paths."
            )
        
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

