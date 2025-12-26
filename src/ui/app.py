"""
Interactive UI - Matplotlib based
BSM307 - Güz 2025

Issue #19, #20, #21, #22: Complete Python UI implementation
"""

import os
import matplotlib

# Docker uyumluluğu: Backend seçimi environment variable'dan
backend = os.environ.get("MPLBACKEND", "TkAgg")
matplotlib.use(backend)

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox, Button
import networkx as nx
from typing import Optional, Tuple
import threading

from ..network.generator import RandomNetworkGenerator
from ..algorithms.ga.genetic_algorithm import GeneticAlgorithm
from ..algorithms.aco.ant_colony import AntColonyOptimizer
from ..metrics.delay import total_delay
from ..metrics.reliability import reliability_cost
from ..metrics.resource_cost import bandwidth_cost, weighted_sum
from ..routing.path_validator import PathValidator
from ..utils.logger import get_logger
from .graph_visualizer import draw_graph

# Experiment runner import (will be imported when needed to avoid circular imports)

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
        
        # Experiment state
        self.experiment_running = False
        self.experiment_progress = ""
        self.num_scenarios = 20
        self.num_repetitions = 5
        
        logger.info("Initialized RoutingUI with graph: %s nodes, %s edges", 
                   graph.number_of_nodes(), graph.number_of_edges())
    
    def setup_ui(self):
        """Issue #19: Setup matplotlib interactive mode and figure."""
        plt.ion()  # Interactive mode
        
        self.fig, self.ax = plt.subplots(figsize=(16, 10))
        plt.subplots_adjust(left=0.1, bottom=0.40, right=0.95, top=0.95)  # Butonlar için daha fazla alan
        
        self.fig.suptitle("BSM307 Çok Amaçlı Yönlendirme - Etkileşimli Arayüz", fontsize=16, fontweight="bold")
        
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
        title = f"Ağ: {self.graph.number_of_nodes()} düğüm, {self.graph.number_of_edges()} kenar"
        if path:
            title += f"\nYol: {self.source} → {self.target} ({len(path)-1} atlamalı)"
            if self.current_metrics:
                title += f" | Gecikme: {self.current_metrics['delay']:.2f}ms"
                title += f" | Maliyet: {self.current_metrics['weighted']:.4f}"
        self.ax.set_title(title, fontsize=12)
        self.ax.axis("off")
        
        plt.draw()
        logger.debug("Network drawn with path: %s", path[:10] if path and len(path) > 10 else path)
    
    def create_controls(self):
        """Issue #21: Create parameter controls (sliders, text boxes, buttons)."""
        # Source input
        ax_source = plt.axes([0.1, 0.28, 0.15, 0.03])
        self.text_source = TextBox(ax_source, "Kaynak: ", initial=str(self.source))
        self.text_source.on_submit(self.update_source)
        
        # Target input
        ax_target = plt.axes([0.3, 0.28, 0.15, 0.03])
        self.text_target = TextBox(ax_target, "Hedef: ", initial=str(self.target))
        self.text_target.on_submit(self.update_target)
        
        # Bandwidth input
        ax_bw = plt.axes([0.5, 0.28, 0.15, 0.03])
        self.text_bandwidth = TextBox(ax_bw, "Bant Genişliği (Mbps): ", initial=str(self.required_bandwidth))
        self.text_bandwidth.on_submit(self.update_bandwidth)
        
        # Algorithm selection (simplified - text box)
        ax_algo = plt.axes([0.7, 0.28, 0.15, 0.03])
        self.text_algorithm = TextBox(ax_algo, "Algoritma (GA/ACO): ", initial=self.algorithm)
        self.text_algorithm.on_submit(self.update_algorithm)
        
        # Weight sliders
        ax_delay = plt.axes([0.1, 0.20, 0.35, 0.03])
        self.slider_delay = Slider(ax_delay, "Gecikme Ağırlığı", 0.0, 1.0, valinit=self.weight_delay, valstep=0.1)
        self.slider_delay.on_changed(self.update_weights)
        
        ax_rel = plt.axes([0.1, 0.16, 0.35, 0.03])
        self.slider_reliability = Slider(ax_rel, "Güvenilirlik Ağırlığı", 0.0, 1.0, valinit=self.weight_reliability, valstep=0.1)
        self.slider_reliability.on_changed(self.update_weights)
        
        ax_res = plt.axes([0.1, 0.12, 0.35, 0.03])
        self.slider_resource = Slider(ax_res, "Kaynak Ağırlığı", 0.0, 1.0, valinit=self.weight_resource, valstep=0.1)
        self.slider_resource.on_changed(self.update_weights)
        
        # Calculate button
        ax_calc = plt.axes([0.5, 0.15, 0.15, 0.04])
        self.button_calc = Button(ax_calc, "Yol Hesapla")
        self.button_calc.on_clicked(self.calculate_path)
        
        # Experiment controls section
        # Scenario count input
        ax_exp_scenarios = plt.axes([0.5, 0.10, 0.12, 0.025])
        self.text_exp_scenarios = TextBox(ax_exp_scenarios, "Senaryolar: ", initial=str(self.num_scenarios))
        self.text_exp_scenarios.on_submit(self.update_exp_scenarios)
        
        # Repetitions input
        ax_exp_reps = plt.axes([0.63, 0.10, 0.12, 0.025])
        self.text_exp_reps = TextBox(ax_exp_reps, "Tekrarlar: ", initial=str(self.num_repetitions))
        self.text_exp_reps.on_submit(self.update_exp_reps)
        
        # Run Experiment button (inline - mevcut UI içinde)
        ax_exp_run = plt.axes([0.76, 0.10, 0.12, 0.04])
        self.button_exp_run = Button(ax_exp_run, "Deneyi Çalıştır", color="lightgreen")
        self.button_exp_run.on_clicked(self.run_experiment)
        
        # Experiment UI butonu (ayrı UI'ye geçiş) - Daha görünür konum
        ax_exp_ui = plt.axes([0.7, 0.18, 0.25, 0.05])
        self.button_exp_ui = Button(ax_exp_ui, "🚀 Experiment UI (20 Senaryo Test)", color="lightblue")
        self.button_exp_ui.on_clicked(self.open_experiment_ui)
        
        # Results text area (simulated with text)
        self.ax_results = plt.axes([0.5, 0.02, 0.45, 0.06])
        self.ax_results.axis("off")
        self.ax_results.text(0.05, 0.5, "Yol bulmak için 'Yol Hesapla'ya tıklayın", 
                            fontsize=9, verticalalignment="center")
        
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
    
    def update_exp_scenarios(self, text: str):
        """Update experiment scenario count."""
        try:
            self.num_scenarios = int(text)
            logger.debug("Experiment scenarios updated to: %s", self.num_scenarios)
        except ValueError:
            logger.warning("Invalid scenario count: %s", text)
    
    def update_exp_reps(self, text: str):
        """Update experiment repetitions."""
        try:
            self.num_repetitions = int(text)
            logger.debug("Experiment repetitions updated to: %s", self.num_repetitions)
        except ValueError:
            logger.warning("Invalid repetitions: %s", text)
    
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
            self.ax_results.text(0.05, 0.5, f"❌ {self.source} ve {self.target} arasında yol yok",
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
            results_text = f"✅ Yol Bulundu ({self.algorithm})\n"
            results_text += f"Yol: {' → '.join(map(str, path[:8]))}{'...' if len(path) > 8 else ''}\n"
            results_text += f"Uzunluk: {len(path)-1} atlamalı\n"
            results_text += f"Gecikme: {delay:.2f} ms | Güvenilirlik Maliyeti: {rel_cost:.4f} | Kaynak Maliyeti: {res_cost:.4f}\n"
            results_text += f"Ağırlıklı Maliyet: {cost:.4f}"
            self.ax_results.text(0.05, 0.5, results_text, fontsize=9, 
                                verticalalignment="center", family="monospace")
            
            plt.draw()
            logger.info("Path calculated: length=%s, cost=%.4f", len(path), cost)
            
        except Exception as e:
            logger.error("Error calculating path: %s", e, exc_info=True)
            self.ax_results.clear()
            self.ax_results.axis("off")
            self.ax_results.text(0.05, 0.5, f"❌ Hata: {str(e)}",
                               fontsize=10, color="red", verticalalignment="center")
            plt.draw()
    
    def run_experiment(self, event):
        """Run experiment in background thread."""
        if self.experiment_running:
            logger.warning("Experiment already running")
            return
        
        # Update UI state
        self.experiment_running = True
        self.button_exp_run.label.set_text("Çalışıyor...")
        self.button_exp_run.color = "lightyellow"
        
        # Update results area
        self.ax_results.clear()
        self.ax_results.axis("off")
        self.ax_results.text(0.05, 0.5, 
                           f"🔄 Deney çalışıyor: {self.num_scenarios} senaryo, her biri için {self.num_repetitions} tekrar...",
                           fontsize=9, verticalalignment="center")
        plt.draw()
        
        # Run in background thread
        thread = threading.Thread(target=self._run_experiment_thread, daemon=True)
        thread.start()
        logger.info("Experiment thread started")
    
    def _run_experiment_thread(self):
        """Run experiment in background thread."""
        try:
            # Import here to avoid circular imports
            import sys
            from datetime import datetime
            from pathlib import Path
            
            # Get project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from experiments.experiment_runner import ExperimentRunner, save_results_to_json
            from experiments.scenario_generator import generate_scenarios_for_experiment
            
            # Normalize weights
            self.update_weights(0.0)
            weights = (self.weight_delay, self.weight_reliability, self.weight_resource)
            
            # Update progress
            self.experiment_progress = "Senaryolar oluşturuluyor..."
            self._update_experiment_status()
            
            # Generate scenarios
            scenarios = generate_scenarios_for_experiment(
                graph=self.graph,
                num_scenarios=self.num_scenarios,
                seed=self.seed
            )
            
            # Update progress
            self.experiment_progress = f"{len(scenarios)} senaryo çalıştırılıyor..."
            self._update_experiment_status()
            
            # Run experiments
            runner = ExperimentRunner(
                graph=self.graph,
                weights=weights,
                num_repetitions=self.num_repetitions
            )
            
            results = runner.run_all_scenarios(
                scenarios=scenarios,
                algorithms=["GA", "ACO"]
            )
            
            # Calculate statistics
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            # Save results
            output_dir = project_root / "experiments" / "results"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = output_dir / f"results_{timestamp}.json"
            
            save_results_to_json(results, str(results_file))
            
            # Update UI with results
            self.experiment_progress = f"✅ Tamamlandı! Başarı: {success_count}/{total_count} ({success_rate:.1f}%)"
            self._update_experiment_status(f"Sonuçlar kaydedildi: {results_file.name}")
            
        except Exception as e:
            logger.error("Error running experiment: %s", e, exc_info=True)
            self.experiment_progress = f"❌ Hata: {str(e)}"
            self._update_experiment_status("Deney başarısız oldu")
        finally:
            self.experiment_running = False
            self.button_exp_run.label.set_text("Deneyi Çalıştır")
            self.button_exp_run.color = "lightgreen"
            plt.draw()
    
    def _update_experiment_status(self, extra_info: str = ""):
        """Update experiment status in UI."""
        try:
            self.ax_results.clear()
            self.ax_results.axis("off")
            status_text = self.experiment_progress
            if extra_info:
                status_text += f"\n{extra_info}"
            self.ax_results.text(0.05, 0.5, status_text,
                               fontsize=8, verticalalignment="center", family="monospace")
            plt.draw()
        except Exception as e:
            logger.error("Error updating experiment status: %s", e)
    
    def open_experiment_ui(self, event):
        """Experiment UI'yi aç (ayrı pencere)."""
        logger.info("Opening Experiment UI")
        plt.close(self.fig)
        
        # Experiment UI'yi import et ve başlat
        from src.ui.experiment_ui import run_experiment_ui
        run_experiment_ui(self.graph, self.seed)
    
    def run(self):
        """Start the interactive UI."""
        # Docker uyumluluğu: Backend kontrolü
        backend = os.environ.get("MPLBACKEND", "TkAgg")
        if backend == "Agg":
            logger.warning("Headless mode (Agg) detected. UI requires GUI backend.")
            logger.warning("For Docker GUI mode, use: docker-compose --profile ui up")
            return
        
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

