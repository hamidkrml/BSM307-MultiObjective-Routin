#!/usr/bin/env python3
"""
BSM307 Multi-Objective Routing - Demo Script
Docker container içinde çalıştırılabilir demo
"""

import os
import sys
from typing import Optional

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
# Headless mode için backend ayarla (Docker için)
backend = os.environ.get("MPLBACKEND", "Agg")
matplotlib.use(backend)

import matplotlib.pyplot as plt
import networkx as nx

from src.network.generator import RandomNetworkGenerator
from src.routing.path_validator import PathValidator
from src.metrics.delay import total_delay
from src.metrics.reliability import reliability_cost
from src.metrics.resource_cost import bandwidth_cost, weighted_sum
from src.algorithms.ga.genetic_algorithm import GeneticAlgorithm
from src.ui.graph_visualizer import draw_graph
from src.utils.logger import get_logger

logger = get_logger(__name__)


def print_header(title: str) -> None:
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str) -> None:
    """Bölüm başlığı yazdır"""
    print(f"\n📌 {title}")
    print("-" * 70)


def main():
    """Ana demo fonksiyonu"""
    print_header("BSM307 Multi-Objective Routing - Docker Demo")
    
    # Environment variables'dan ayarları al
    seed = int(os.environ.get("EXPERIMENT_SEED", "42"))
    num_nodes = int(os.environ.get("NUM_NODES", "250"))
    edge_prob = float(os.environ.get("EDGE_PROB", "0.4"))
    
    print_section("Konfigürasyon")
    print(f"   Seed: {seed}")
    print(f"   Düğüm Sayısı: {num_nodes}")
    print(f"   Edge Probability: {edge_prob}")
    print(f"   Matplotlib Backend: {backend}")
    
    try:
        # 1. Ağ oluştur
        print_section("1. Ağ Oluşturma")
        print("   🔄 Erdos-Renyi graf üretiliyor...")
        
        generator = RandomNetworkGenerator(
            num_nodes=num_nodes,
            edge_prob=edge_prob,
            seed=seed
        )
        graph = generator.generate()
        graph = generator.attach_attributes(graph)
        
        print(f"   ✅ Graf oluşturuldu:")
        print(f"      - Düğüm sayısı: {graph.number_of_nodes()}")
        print(f"      - Kenar sayısı: {graph.number_of_edges()}")
        print(f"      - Bağlılık: {'Bağlı ✓' if nx.is_connected(graph) else 'Bağlı Değil ✗'}")
        
        # 2. S-D çifti seç
        print_section("2. Source-Destination Seçimi")
        nodes_list = list(graph.nodes())
        
        # İyi bir S-D çifti seç (uzak düğümler)
        source = nodes_list[0]
        target = nodes_list[min(100, len(nodes_list) - 1)]
        
        print(f"   🎯 Source: {source}")
        print(f"   🎯 Target: {target}")
        
        # 3. Path bul
        print_section("3. Path Bulma")
        if not nx.has_path(graph, source, target):
            print(f"   ❌ {source} → {target} arasında yol bulunamadı!")
            return 1
        
        # GA ile path bul (Issue #9-12)
        print("   🔄 GA algoritması ile path aranıyor...")
        ga = GeneticAlgorithm(
            graph=graph,
            source=source,
            target=target,
            weights=(0.4, 0.3, 0.3),
            population_size=20,
            seed=seed
        )
        path, ga_fitness = ga.run(generations=10)
        print(f"   ✅ GA ile path bulundu: {len(path)-1} adım (fitness: {ga_fitness:.4f})")
        print(f"      Path: {' → '.join(map(str, path[:10]))}{'...' if len(path) > 10 else ''}")
        
        # 4. Path doğrulama
        print_section("4. Path Doğrulama")
        validator = PathValidator(graph)
        
        is_simple = validator.is_simple_path(path)
        has_cap = validator.has_capacity(path, 500.0)
        
        print(f"   ✅ Basit path (döngü yok): {'Evet ✓' if is_simple else 'Hayır ✗'}")
        print(f"   ✅ Kapasite kontrolü (500 Mbps): {'Yeterli ✓' if has_cap else 'Yetersiz ✗'}")
        
        # 5. Metrikleri hesapla
        print_section("5. Metrik Hesaplamaları")
        
        delay = total_delay(graph=graph, path=path)
        rel_cost = reliability_cost(graph=graph, path=path)
        res_cost = bandwidth_cost(graph=graph, path=path)
        
        print(f"   📊 Toplam Gecikme: {delay:.2f} ms")
        print(f"   📊 Güvenilirlik Maliyeti: {rel_cost:.4f} (-log(R))")
        print(f"   📊 Kaynak Maliyeti: {res_cost:.4f} (1Gbps/BW)")
        
        # 6. Ağırlıklı toplam
        print_section("6. Ağırlıklı Toplam Skor")
        weights = (0.4, 0.3, 0.3)  # (delay, reliability, resource)
        weighted = weighted_sum(delay, rel_cost, res_cost, weights)
        
        print(f"   📈 Ağırlıklar: delay={weights[0]}, reliability={weights[1]}, resource={weights[2]}")
        print(f"   📈 Ağırlıklı Toplam: {weighted:.4f}")
        
        # 7. Görselleştirme
        print_section("7. Görselleştirme")
        
        if backend == "Agg":
            # Headless mode - dosyaya kaydet
            output_dir = "data"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "demo_graph.png")
            
            print(f"   🎨 Grafik headless mode'da oluşturuluyor...")
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Graph layout
            pos = nx.spring_layout(graph, seed=seed, k=0.5, iterations=50)
            
            # Tüm edge'leri çiz (gri)
            nx.draw_networkx_edges(
                graph, pos, alpha=0.1, edge_color="gray", width=0.5, ax=ax
            )
            
            # Tüm node'ları çiz
            nx.draw_networkx_nodes(
                graph, pos, node_size=30, node_color="lightblue", alpha=0.6, ax=ax
            )
            
            # Path'i vurgula (kırmızı)
            if len(path) > 1:
                path_edges = list(zip(path[:-1], path[1:]))
                nx.draw_networkx_edges(
                    graph, pos, edgelist=path_edges, edge_color="red", width=3, alpha=0.8, ax=ax
                )
                # Path node'larını vurgula
                nx.draw_networkx_nodes(
                    graph, pos, nodelist=path, node_size=100, node_color="red", alpha=0.8, ax=ax
                )
                # Source ve target'ı özel göster
                nx.draw_networkx_nodes(
                    graph, pos, nodelist=[source], node_size=200, node_color="green", alpha=1.0, ax=ax
                )
                nx.draw_networkx_nodes(
                    graph, pos, nodelist=[target], node_size=200, node_color="blue", alpha=1.0, ax=ax
                )
            
            ax.set_title(
                f"BSM307 Routing Demo\nPath: {source} → {target} "
                f"(delay={delay:.2f}ms, cost={weighted:.4f})",
                fontsize=14,
                fontweight="bold"
            )
            ax.axis("off")
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=150, bbox_inches="tight")
            print(f"   ✅ Grafik kaydedildi: {output_file}")
            plt.close()
        else:
            # GUI mode - ekranda göster
            print(f"   🎨 Grafik GUI mode'da gösteriliyor...")
            draw_graph(graph, path=path, title=f"Path: {source} → {target}")
        
        # 8. Özet
        print_section("8. Özet")
        print(f"   ✅ Ağ başarıyla oluşturuldu ve analiz edildi")
        print(f"   ✅ Path bulundu ve doğrulandı")
        print(f"   ✅ Tüm metrikler hesaplandı")
        print(f"   ✅ Görselleştirme tamamlandı")
        
        print_header("Demo Başarıyla Tamamlandı! 🎉")
        return 0
        
    except Exception as e:
        logger.error("Demo sırasında hata oluştu: %s", e, exc_info=True)
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

