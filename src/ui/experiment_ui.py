"""
Experiment UI - Matplotlib based
BSM307 - Güz 2025

Ayrı experiment arayüzü - kullanıcıdan input alır ve experiment'leri çalıştırır.
"""

import os
import matplotlib
import threading

# Docker uyumluluğu: Backend seçimi environment variable'dan
backend = os.environ.get("MPLBACKEND", "TkAgg")
matplotlib.use(backend)

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox, Button
import networkx as nx
from typing import Optional, Tuple
from pathlib import Path
import sys

# Project root'u path'e ekle
current_file = Path(__file__)
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentRunner, save_results_to_json
from experiments.scenario_generator import generate_scenarios_for_experiment
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExperimentUI:
    """
    Experiment için ayrı UI.
    
    Kullanıcıdan alınan parametrelerle experiment'leri çalıştırır.
    """
    
    def __init__(self, graph: nx.Graph, seed: int = 42):
        """
        Args:
            graph: NetworkX graph
            seed: Random seed
        """
        self.graph = graph
        self.seed = seed
        
        # Experiment parametreleri (varsayılan değerler)
        self.num_scenarios = 20
        self.num_repetitions = 5
        self.weight_delay = 0.4
        self.weight_reliability = 0.3
        self.weight_resource = 0.3
        
        # State
        self.experiment_running = False
        self.experiment_progress = ""
        self.results_file = None
        
        logger.info("Initialized ExperimentUI with graph: %s nodes, %s edges", 
                   graph.number_of_nodes(), graph.number_of_edges())
    
    def setup_ui(self):
        """UI'yi kur."""
        plt.ion()  # Interactive mode
        
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        plt.subplots_adjust(left=0.1, bottom=0.45, right=0.95, top=0.95)
        
        self.fig.suptitle("BSM307 - Experiment Arayüzü", fontsize=16, fontweight="bold")
        
        logger.info("Experiment UI setup complete")
    
    def draw_info(self):
        """Bilgi panelini çiz."""
        self.ax.clear()
        self.ax.axis("off")
        
        # Başlık
        info_text = "EXPERIMENT YAPILANDIRMASI\n"
        info_text += "=" * 50 + "\n\n"
        
        info_text += f"Ağ Bilgisi:\n"
        info_text += f"  • Düğüm Sayısı: {self.graph.number_of_nodes()}\n"
        info_text += f"  • Kenar Sayısı: {self.graph.number_of_edges()}\n"
        info_text += f"  • Seed: {self.seed}\n\n"
        
        info_text += "Experiment Ayarları:\n"
        info_text += f"  • Senaryo Sayısı: {self.num_scenarios}\n"
        info_text += f"  • Tekrar Sayısı: {self.num_repetitions}\n"
        info_text += f"  • Toplam Experiment: {self.num_scenarios * self.num_repetitions * 2}\n"
        info_text += f"    (20 senaryo × {self.num_repetitions} tekrar × 2 algoritma)\n\n"
        
        info_text += "Ağırlıklar:\n"
        info_text += f"  • Gecikme: {self.weight_delay:.2f}\n"
        info_text += f"  • Güvenilirlik: {self.weight_reliability:.2f}\n"
        info_text += f"  • Kaynak: {self.weight_resource:.2f}\n"
        
        self.ax.text(0.05, 0.95, info_text, fontsize=11, 
                    verticalalignment="top", family="monospace",
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        
        plt.draw()
    
    def create_controls(self):
        """Kontrolleri oluştur."""
        # Senaryo sayısı input
        ax_scenarios = plt.axes([0.1, 0.35, 0.25, 0.03])
        self.text_scenarios = TextBox(ax_scenarios, "Senaryo Sayısı: ", initial=str(self.num_scenarios))
        self.text_scenarios.on_submit(self.update_scenarios)
        
        # Tekrar sayısı input
        ax_repetitions = plt.axes([0.4, 0.35, 0.25, 0.03])
        self.text_repetitions = TextBox(ax_repetitions, "Tekrar Sayısı: ", initial=str(self.num_repetitions))
        self.text_repetitions.on_submit(self.update_repetitions)
        
        # Weight sliders
        ax_delay = plt.axes([0.1, 0.28, 0.55, 0.03])
        self.slider_delay = Slider(ax_delay, "Gecikme Ağırlığı", 0.0, 1.0, 
                                   valinit=self.weight_delay, valstep=0.1)
        self.slider_delay.on_changed(self.update_weights)
        
        ax_rel = plt.axes([0.1, 0.24, 0.55, 0.03])
        self.slider_reliability = Slider(ax_rel, "Güvenilirlik Ağırlığı", 0.0, 1.0,
                                         valinit=self.weight_reliability, valstep=0.1)
        self.slider_reliability.on_changed(self.update_weights)
        
        ax_res = plt.axes([0.1, 0.20, 0.55, 0.03])
        self.slider_resource = Slider(ax_res, "Kaynak Ağırlığı", 0.0, 1.0,
                                     valinit=self.weight_resource, valstep=0.1)
        self.slider_resource.on_changed(self.update_weights)
        
        # Run Experiment button
        ax_run = plt.axes([0.7, 0.24, 0.25, 0.10])
        self.button_run = Button(ax_run, "Experiment'i\nÇalıştır", color="lightgreen")
        self.button_run.on_clicked(self.run_experiment)
        
        # Back button (ana UI'ye dönmek için)
        ax_back = plt.axes([0.7, 0.12, 0.25, 0.05])
        self.button_back = Button(ax_back, "Ana UI'ye Dön", color="lightblue")
        self.button_back.on_clicked(self.go_back)
        
        # Progress/Results text area
        self.ax_progress = plt.axes([0.1, 0.02, 0.85, 0.15])
        self.ax_progress.axis("off")
        self.ax_progress.text(0.05, 0.5, 
                             "Parametreleri ayarlayın ve 'Experiment'i Çalıştır' butonuna tıklayın",
                             fontsize=10, verticalalignment="center")
        
        logger.info("Experiment UI controls created")
    
    def update_scenarios(self, text: str):
        """Senaryo sayısını güncelle."""
        try:
            self.num_scenarios = int(text)
            logger.debug("Scenarios updated to: %s", self.num_scenarios)
            self.draw_info()
        except ValueError:
            logger.warning("Invalid scenario count: %s", text)
    
    def update_repetitions(self, text: str):
        """Tekrar sayısını güncelle."""
        try:
            self.num_repetitions = int(text)
            logger.debug("Repetitions updated to: %s", self.num_repetitions)
            self.draw_info()
        except ValueError:
            logger.warning("Invalid repetitions: %s", text)
    
    def update_weights(self, val: float):
        """Ağırlıkları güncelle."""
        self.weight_delay = self.slider_delay.val
        self.weight_reliability = self.slider_reliability.val
        self.weight_resource = self.slider_resource.val
        
        # Normalize
        total = self.weight_delay + self.weight_reliability + self.weight_resource
        if total > 0:
            self.weight_delay /= total
            self.weight_reliability /= total
            self.weight_resource /= total
        
        logger.debug("Weights updated: delay=%.2f, rel=%.2f, res=%.2f",
                    self.weight_delay, self.weight_reliability, self.weight_resource)
    
    def run_experiment(self, event):
        """Experiment'i başlat."""
        if self.experiment_running:
            logger.warning("Experiment already running")
            return
        
        self.experiment_running = True
        self.button_run.label.set_text("Çalışıyor...")
        self.button_run.color = "lightyellow"
        
        # Progress güncelle
        self._update_progress(f"🔄 Experiment başlatılıyor: {self.num_scenarios} senaryo, {self.num_repetitions} tekrar...")
        plt.draw()
        
        # Background thread'de çalıştır
        thread = threading.Thread(target=self._run_experiment_thread, daemon=True)
        thread.start()
        logger.info("Experiment thread started")
    
    def _run_experiment_thread(self):
        """Experiment'i background thread'de çalıştır."""
        try:
            from datetime import datetime
            
            weights = (self.weight_delay, self.weight_reliability, self.weight_resource)
            
            # Senaryoları üret
            self._update_progress("📋 Senaryolar oluşturuluyor...")
            scenarios = generate_scenarios_for_experiment(
                graph=self.graph,
                num_scenarios=self.num_scenarios,
                seed=self.seed
            )
            
            # Experiment runner
            self._update_progress(f"🚀 {len(scenarios)} senaryo çalıştırılıyor...")
            runner = ExperimentRunner(
                graph=self.graph,
                weights=weights,
                num_repetitions=self.num_repetitions
            )
            
            # Experiment'leri çalıştır
            results = runner.run_all_scenarios(
                scenarios=scenarios,
                algorithms=["GA", "ACO"]
            )
            
            # İstatistikler
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            # Sonuçları kaydet
            output_dir = project_root / "experiments" / "results"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = output_dir / f"results_{timestamp}.json"
            
            save_results_to_json(results, str(results_file))
            self.results_file = results_file
            
            # Başarı mesajı
            self._update_progress(
                f"✅ Experiment tamamlandı!\n\n"
                f"Başarı: {success_count}/{total_count} ({success_rate:.1f}%)\n"
                f"Sonuçlar kaydedildi: {results_file.name}\n"
                f"Konum: {results_file.parent}"
            )
            
        except Exception as e:
            logger.error("Error running experiment: %s", e, exc_info=True)
            self._update_progress(f"❌ Hata: {str(e)}")
        finally:
            self.experiment_running = False
            self.button_run.label.set_text("Experiment'i\nÇalıştır")
            self.button_run.color = "lightgreen"
            plt.draw()
    
    def _update_progress(self, message: str):
        """Progress mesajını güncelle."""
        self.experiment_progress = message
        try:
            self.ax_progress.clear()
            self.ax_progress.axis("off")
            self.ax_progress.text(0.05, 0.5, message, fontsize=9,
                                verticalalignment="center", family="monospace",
                                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.3))
            plt.draw()
        except Exception as e:
            logger.error("Error updating progress: %s", e)
    
    def go_back(self, event):
        """Ana UI'ye dön."""
        logger.info("Returning to main UI")
        plt.close(self.fig)
        # Ana UI'yi yeniden başlat
        from src.ui.app import run_app
        run_app(self.graph, self.seed)
    
    def run(self):
        """UI'yi başlat."""
        backend = os.environ.get("MPLBACKEND", "TkAgg")
        if backend == "Agg":
            logger.warning("Headless mode (Agg) detected. UI requires GUI backend.")
            return
        
        self.setup_ui()
        self.create_controls()
        self.draw_info()
        logger.info("Experiment UI started, waiting for user interaction...")
        plt.show(block=True)


def run_experiment_ui(graph: Optional[nx.Graph] = None, seed: int = 42) -> None:
    """
    Experiment UI'yi başlat.
    
    Args:
        graph: NetworkX graph (if None, generates new one)
        seed: Random seed
    """
    if graph is None:
        from src.network.generator import RandomNetworkGenerator
        logger.info("Generating new network...")
        generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=seed)
        graph = generator.generate()
        graph = generator.attach_attributes(graph)
    
    ui = ExperimentUI(graph, seed=seed)
    ui.run()


if __name__ == "__main__":
    run_experiment_ui()

