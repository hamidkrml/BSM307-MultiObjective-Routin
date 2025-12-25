"""
Interactive UI - Matplotlib based
BSM307 - Güz 2025

Issue #19, #20, #21, #22: Complete Python UI implementation
"""

import matplotlib
matplotlib.use("TkAgg")  # Interactive backend

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox, Button
import networkx as nx
from typing import Optional, Tuple

from ..network.generator import RandomNetworkGenerator
from ..algorithms.ga.genetic_algorithm import GeneticAlgorithm
from ..algorithms.aco.ant_colony import AntColonyOptimizer
from ..metrics.delay import total_delay
from ..metrics.reliability import reliability_cost
from ..metrics.resource_cost import bandwidth_cost, weighted_sum
from ..routing.path_validator import PathValidator
from ..utils.logger import get_logger
from .graph_visualizer import draw_graph

logger = get_logger(__name__)


class RoutingUI:
    """
    Interactive matplotlib-based UI for routing.
    
    Issue #19: Matplotlib interactive setup
    Issue #20: Network visualization
    Issue #21: Parameter controls
    Issue #22: Results display
    """
    
    def __init__(self, graph: nx.Graph, seed: int = 42):
        """
        Args:
            graph: NetworkX graph
            seed: Random seed
        """
        self.graph = graph
        self.seed = seed
        self.current_path: Optional[list] = None
        self.current_metrics: Optional[dict] = None
        
        # UI state
        self.source = 0
        self.target = min(100, graph.number_of_nodes() - 1)
        self.weight_delay = 0.4
        self.weight_reliability = 0.3
        self.weight_resource = 0.3
        self.required_bandwidth = 500.0
        self.algorithm = "GA"  # "GA" or "ACO"
        
        logger.info("Initialized RoutingUI with graph: %s nodes, %s edges", 
                   graph.number_of_nodes(), graph.number_of_edges())
    
    def setup_ui(self):
        """Issue #19: Setup matplotlib interactive mode and figure."""
        plt.ion()  # Interactive mode
        
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        plt.subplots_adjust(left=0.1, bottom=0.35, right=0.95, top=0.95)
        
        self.fig.suptitle("BSM307 Multi-Objective Routing - Interactive UI", fontsize=16, fontweight="bold")
        
        logger.info("UI setup complete")
    
    def draw_network(self, path: Optional[list] = None):
        """
        Issue #20: Draw network with optional path highlighting.
        
        Args:
            path: Path to highlight (optional)
        """
        self.ax.clear()
        
        # Graph layout
        pos = nx.spring_layout(self.graph, seed=self.seed, k=0.5, iterations=50)
        
        # Draw all edges (gray, thin)
        nx.draw_networkx_edges(
            self.graph, pos, 
            alpha=0.1, edge_color="gray", width=0.5, ax=self.ax
        )
        
        # Draw all nodes (light blue)
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_size=30, node_color="lightblue", alpha=0.6, ax=self.ax
        )
        
        # Highlight path if provided
        if path and len(path) > 1:
            path_edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(
                self.graph, pos, edgelist=path_edges,
                edge_color="red", width=3, alpha=0.8, ax=self.ax
            )
            nx.draw_networkx_nodes(
                self.graph, pos, nodelist=path,
                node_size=100, node_color="red", alpha=0.8, ax=self.ax
            )
            
            # Source and target
            nx.draw_networkx_nodes(
                self.graph, pos, nodelist=[self.source],
                node_size=200, node_color="green", alpha=1.0, ax=self.ax
            )
            nx.draw_networkx_nodes(
                self.graph, pos, nodelist=[self.target],
                node_size=200, node_color="blue", alpha=1.0, ax=self.ax
            )
        
        # Title with metrics
        title = f"Network: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges"
        if path:
            title += f"\nPath: {self.source} → {self.target} ({len(path)-1} hops)"
            if self.current_metrics:
                title += f" | Delay: {self.current_metrics['delay']:.2f}ms"
                title += f" | Cost: {self.current_metrics['weighted']:.4f}"
        self.ax.set_title(title, fontsize=12)
        self.ax.axis("off")
        
        plt.draw()
        logger.debug("Network drawn with path: %s", path[:10] if path and len(path) > 10 else path)
    
    def create_controls(self):
        """Issue #21: Create parameter controls (sliders, text boxes, buttons)."""
        # Source input
        ax_source = plt.axes([0.1, 0.28, 0.15, 0.03])
        self.text_source = TextBox(ax_source, "Source: ", initial=str(self.source))
        self.text_source.on_submit(self.update_source)
        
        # Target input
        ax_target = plt.axes([0.3, 0.28, 0.15, 0.03])
        self.text_target = TextBox(ax_target, "Target: ", initial=str(self.target))
        self.text_target.on_submit(self.update_target)
        
        # Bandwidth input
        ax_bw = plt.axes([0.5, 0.28, 0.15, 0.03])
        self.text_bandwidth = TextBox(ax_bw, "Bandwidth (Mbps): ", initial=str(self.required_bandwidth))
        self.text_bandwidth.on_submit(self.update_bandwidth)
        
        # Algorithm selection (simplified - text box)
        ax_algo = plt.axes([0.7, 0.28, 0.15, 0.03])
        self.text_algorithm = TextBox(ax_algo, "Algorithm (GA/ACO): ", initial=self.algorithm)
        self.text_algorithm.on_submit(self.update_algorithm)
        
        # Weight sliders
        ax_delay = plt.axes([0.1, 0.20, 0.35, 0.03])
        self.slider_delay = Slider(ax_delay, "Delay Weight", 0.0, 1.0, valinit=self.weight_delay, valstep=0.1)
        self.slider_delay.on_changed(self.update_weights)
        
        ax_rel = plt.axes([0.1, 0.16, 0.35, 0.03])
        self.slider_reliability = Slider(ax_rel, "Reliability Weight", 0.0, 1.0, valinit=self.weight_reliability, valstep=0.1)
        self.slider_reliability.on_changed(self.update_weights)
        
        ax_res = plt.axes([0.1, 0.12, 0.35, 0.03])
        self.slider_resource = Slider(ax_res, "Resource Weight", 0.0, 1.0, valinit=self.weight_resource, valstep=0.1)
        self.slider_resource.on_changed(self.update_weights)
        
        # Calculate button
        ax_calc = plt.axes([0.5, 0.12, 0.2, 0.05])
        self.button_calc = Button(ax_calc, "Calculate Path")
        self.button_calc.on_clicked(self.calculate_path)
        
        # Results text area (simulated with text)
        self.ax_results = plt.axes([0.5, 0.02, 0.45, 0.08])
        self.ax_results.axis("off")
        self.ax_results.text(0.05, 0.5, "Click 'Calculate Path' to find route", 
                            fontsize=10, verticalalignment="center")
        
        logger.info("Controls created")
    
    def update_source(self, text: str):
        """Update source node."""
        try:
            self.source = int(text)
            logger.debug("Source updated to: %s", self.source)
            self.draw_network(self.current_path)
        except ValueError:
            logger.warning("Invalid source value: %s", text)
    
    def update_target(self, text: str):
        """Update target node."""
        try:
            self.target = int(text)
            logger.debug("Target updated to: %s", self.target)
            self.draw_network(self.current_path)
        except ValueError:
            logger.warning("Invalid target value: %s", text)
    
    def update_bandwidth(self, text: str):
        """Update required bandwidth."""
        try:
            self.required_bandwidth = float(text)
            logger.debug("Bandwidth updated to: %s", self.required_bandwidth)
        except ValueError:
            logger.warning("Invalid bandwidth value: %s", text)
    
    def update_algorithm(self, text: str):
        """Update algorithm selection."""
        algo = text.upper().strip()
        if algo in ["GA", "ACO"]:
            self.algorithm = algo
            logger.debug("Algorithm updated to: %s", self.algorithm)
        else:
            logger.warning("Invalid algorithm: %s (use GA or ACO)", text)
    
    def update_weights(self, val: float):
        """Update weight values from sliders."""
        self.weight_delay = self.slider_delay.val
        self.weight_reliability = self.slider_reliability.val
        self.weight_resource = self.slider_resource.val
        
        # Normalize weights
        total = self.weight_delay + self.weight_reliability + self.weight_resource
        if total > 0:
            self.weight_delay /= total
            self.weight_reliability /= total
            self.weight_resource /= total
        
        logger.debug("Weights updated: delay=%.2f, rel=%.2f, res=%.2f",
                    self.weight_delay, self.weight_reliability, self.weight_resource)
    
    def calculate_path(self, event):
        """
        Issue #22: Calculate path using selected algorithm and display results.
        
        Args:
            event: Button click event
        """
        logger.info("Calculating path: source=%s, target=%s, algorithm=%s",
                   self.source, self.target, self.algorithm)
        
        # Normalize weights
        self.update_weights(0.0)
        weights = (self.weight_delay, self.weight_reliability, self.weight_resource)
        
        # Check if path exists
        if not nx.has_path(self.graph, self.source, self.target):
            self.ax_results.clear()
            self.ax_results.axis("off")
            self.ax_results.text(0.05, 0.5, f"❌ No path between {self.source} and {self.target}",
                               fontsize=10, color="red", verticalalignment="center")
            plt.draw()
            return
        
        # Run algorithm
        try:
            if self.algorithm == "GA":
                ga = GeneticAlgorithm(
                    graph=self.graph,
                    source=self.source,
                    target=self.target,
                    weights=weights,
                    required_bandwidth=self.required_bandwidth,
                    population_size=20,
                    seed=self.seed
                )
                path, cost = ga.run(generations=10)
            else:  # ACO
                aco = AntColonyOptimizer(
                    graph=self.graph,
                    source=self.source,
                    target=self.target,
                    weights=weights,
                    required_bandwidth=self.required_bandwidth,
                    num_ants=15,
                    seed=self.seed
                )
                path, cost = aco.run(iterations=10)
            
            # Calculate metrics
            delay = total_delay(graph=self.graph, path=path)
            rel_cost = reliability_cost(graph=self.graph, path=path)
            res_cost = bandwidth_cost(graph=self.graph, path=path)
            
            self.current_path = path
            self.current_metrics = {
                "delay": delay,
                "reliability_cost": rel_cost,
                "resource_cost": res_cost,
                "weighted": cost
            }
            
            # Update visualization
            self.draw_network(path)
            
            # Update results display
            self.ax_results.clear()
            self.ax_results.axis("off")
            results_text = f"✅ Path Found ({self.algorithm})\n"
            results_text += f"Path: {' → '.join(map(str, path[:8]))}{'...' if len(path) > 8 else ''}\n"
            results_text += f"Length: {len(path)-1} hops\n"
            results_text += f"Delay: {delay:.2f} ms | Rel Cost: {rel_cost:.4f} | Res Cost: {res_cost:.4f}\n"
            results_text += f"Weighted Cost: {cost:.4f}"
            self.ax_results.text(0.05, 0.5, results_text, fontsize=9, 
                                verticalalignment="center", family="monospace")
            
            plt.draw()
            logger.info("Path calculated: length=%s, cost=%.4f", len(path), cost)
            
        except Exception as e:
            logger.error("Error calculating path: %s", e, exc_info=True)
            self.ax_results.clear()
            self.ax_results.axis("off")
            self.ax_results.text(0.05, 0.5, f"❌ Error: {str(e)}",
                               fontsize=10, color="red", verticalalignment="center")
            plt.draw()
    
    def run(self):
        """Start the interactive UI."""
        self.setup_ui()
        self.create_controls()
        self.draw_network()
        logger.info("UI started, waiting for user interaction...")
        plt.show(block=True)  # Block until window is closed


def run_app(graph: Optional[nx.Graph] = None, seed: int = 42) -> None:
    """
    Issue #19: Launch interactive UI.
    
    Args:
        graph: NetworkX graph (if None, generates new one)
        seed: Random seed
    """
    if graph is None:
        logger.info("Generating new network...")
        generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=seed)
        graph = generator.generate()
        graph = generator.attach_attributes(graph)
    
    ui = RoutingUI(graph, seed=seed)
    ui.run()

