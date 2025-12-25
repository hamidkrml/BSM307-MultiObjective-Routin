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
    """
    Draw graph with optional path highlighting.
    
    Issue #20: Enhanced visualization with path highlighting.
    
    Args:
        graph: NetworkX graph
        path: Path to highlight (optional)
        title: Graph title
    """
    pos = nx.spring_layout(graph, seed=42)
    
    # Draw all edges (gray)
    nx.draw_networkx_edges(graph, pos, alpha=0.1, edge_color="gray", width=0.5)
    
    # Draw all nodes (light blue)
    nx.draw_networkx_nodes(graph, pos, node_size=50, node_color="lightblue", alpha=0.6)
    
    # Highlight path if provided
    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color="r", width=3, alpha=0.8)
        nx.draw_networkx_nodes(graph, pos, nodelist=path, node_size=100, node_color="red", alpha=0.8)
        
        # Source and target
        if len(path) > 0:
            nx.draw_networkx_nodes(graph, pos, nodelist=[path[0]], node_size=200, node_color="green", alpha=1.0)
            nx.draw_networkx_nodes(graph, pos, nodelist=[path[-1]], node_size=200, node_color="blue", alpha=1.0)
    
    plt.title(title)
    logger.info("Displaying graph with title=%s, path=%s", title, path[:10] if path and len(path) > 10 else path)
    plt.show()

