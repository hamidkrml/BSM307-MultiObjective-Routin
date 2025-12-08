"""
Graf görselleştirici
BSM307 - Güz 2025
"""

from typing import Any, Optional

import matplotlib.pyplot as plt
import networkx as nx

from ..utils.logger import get_logger

logger = get_logger(__name__)


def draw_graph(graph: nx.Graph, path: Optional[list] = None, title: str = "Network") -> None:
    """TODO: UI ile entegre et, path kenarlarını renklendir."""
    pos = nx.spring_layout(graph, seed=42)
    nx.draw_networkx(graph, pos, node_size=50, with_labels=False)
    if path:
        edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color="r", width=2)
    plt.title(title)
    logger.info("Displaying graph with title=%s", title)
    plt.show()

