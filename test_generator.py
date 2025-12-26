#!/usr/bin/env python3
"""
Test script for RandomNetworkGenerator
BSM307 - Güz 2025
"""

import sys
import os

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.network.generator import RandomNetworkGenerator
import networkx as nx

def main():
    print("=" * 60)
    print("BSM307 - Network Generator Test")
    print("=" * 60)
    print()
    
    # Generator oluştur (PDF gereksinimlerine göre)
    print("📊 Generator oluşturuluyor...")
    print("   - Düğüm sayısı: 250")
    print("   - Edge probability: 0.4")
    print("   - Seed: 42")
    print()
    
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    
    # Graf üret
    print("🔄 Graf üretiliyor...")
    graph = generator.generate()
    print()
    
    # Sonuçları göster
    print("=" * 60)
    print("📈 GRAF ÖZELLİKLERİ")
    print("=" * 60)
    print(f"✅ Düğüm sayısı: {graph.number_of_nodes()}")
    print(f"✅ Kenar sayısı: {graph.number_of_edges()}")
    print(f"✅ Bağlılık durumu: {'Bağlı ✓' if nx.is_connected(graph) else 'Bağlı Değil ✗'}")
    print()
    
    # Beklenen kenar sayısı (yaklaşık)
    expected_edges = int(250 * 249 * 0.4 / 2)  # n*(n-1)*p/2
    print(f"📊 Beklenen kenar sayısı (yaklaşık): {expected_edges}")
    print(f"📊 Gerçek kenar sayısı: {graph.number_of_edges()}")
    print(f"📊 Fark: {abs(graph.number_of_edges() - expected_edges)}")
    print()
    
    # Bağlılık analizi
    if nx.is_connected(graph):
        print("✅ Graf bağlı - Tüm S-D çiftleri arasında yol var")
    else:
        components = list(nx.connected_components(graph))
        print(f"⚠️  Graf bağlı değil - {len(components)} bağlı bileşen var")
        print(f"   En büyük bileşen: {len(max(components, key=len))} düğüm")
    print()
    
    # Örnek düğüm ve kenar bilgileri
    print("=" * 60)
    print("🔍 ÖRNEK BİLGİLER")
    print("=" * 60)
    
    # İlk 5 düğümün komşularını göster
    print("\n📌 İlk 5 düğümün komşu sayıları:")
    for i, node in enumerate(list(graph.nodes())[:5]):
        neighbors = list(graph.neighbors(node))
        print(f"   Düğüm {node}: {len(neighbors)} komşu")
        if len(neighbors) > 0:
            print(f"      Komşular: {neighbors[:5]}{'...' if len(neighbors) > 5 else ''}")
    print()
    
    # İlk 5 kenarı göster
    print("🔗 İlk 5 kenar:")
    for i, edge in enumerate(list(graph.edges())[:5]):
        print(f"   {edge[0]} ↔ {edge[1]}")
    print()
    
    # Graf yoğunluğu
    density = nx.density(graph)
    print(f"📊 Graf yoğunluğu: {density:.4f}")
    print(f"   (1.0 = tam bağlı graf, 0.0 = boş graf)")
    print()
    
    # Kısa yol örneği (eğer mümkünse)
    nodes_list = list(graph.nodes())
    if len(nodes_list) >= 2:
        source = nodes_list[0]
        target = nodes_list[-1]
        try:
            if nx.has_path(graph, source, target):
                path_length = nx.shortest_path_length(graph, source, target)
                print(f"🛤️  Örnek yol uzunluğu: {source} → {target} = {path_length} adım")
            else:
                print(f"⚠️  {source} → {target} arasında yol yok")
        except Exception as e:
            print(f"⚠️  Yol analizi hatası: {e}")
    print()
    
    print("=" * 60)
    print("✅ Test tamamlandı!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

