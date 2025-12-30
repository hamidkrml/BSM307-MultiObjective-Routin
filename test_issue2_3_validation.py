#!/usr/bin/env python3
"""
Issue #2 ve #3 doğrulama testi
BSM307 - Güz 2025
"""

import sys
import os

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.network.generator import RandomNetworkGenerator
from src.network.node import Node
from src.network.link import Link
import networkx as nx

def test_issue2_node_attributes():
    """Issue #2: Node attributes test"""
    print("=" * 60)
    print("🔍 ISSUE #2: NODE ATTRIBUTES TEST")
    print("=" * 60)
    
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    # İlk 10 düğümü kontrol et
    nodes_to_check = list(graph.nodes())[:10]
    all_valid = True
    
    for node_id in nodes_to_check:
        node_data = graph.nodes[node_id]
        node = Node(id=node_id, attributes=node_data)
        
        processing_delay = node.processing_delay()
        reliability = node.reliability()
        is_valid = node.is_valid()
        
        # PDF gereksinimleri kontrolü
        delay_ok = 0.5 <= processing_delay <= 2.0
        reliability_ok = 0.95 <= reliability <= 0.999
        
        if not delay_ok or not reliability_ok or not is_valid:
            print(f"❌ Node {node_id}: FAILED")
            print(f"   processing_delay: {processing_delay} (expected: [0.5, 2.0])")
            print(f"   reliability: {reliability} (expected: [0.95, 0.999])")
            all_valid = False
        else:
            print(f"✅ Node {node_id}: OK")
            print(f"   processing_delay: {processing_delay:.2f} ms")
            print(f"   reliability: {reliability:.4f}")
    
    print()
    if all_valid:
        print("✅ ISSUE #2: TÜM NODE ATTRIBUTES PDF GEREKSİNİMLERİNE UYGUN!")
    else:
        print("❌ ISSUE #2: BAZI NODE ATTRIBUTES PDF GEREKSİNİMLERİNE UYGUN DEĞİL!")
    
    return all_valid

def test_issue3_link_attributes():
    """Issue #3: Link attributes test"""
    print("=" * 60)
    print("🔍 ISSUE #3: LINK ATTRIBUTES TEST")
    print("=" * 60)
    
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    # İlk 10 kenarı kontrol et
    edges_to_check = list(graph.edges())[:10]
    all_valid = True
    
    for u, v in edges_to_check:
        edge_data = graph.edges[u, v]
        link = Link(source=u, target=v, attributes=edge_data)
        
        bandwidth = link.bandwidth()
        delay = link.delay()
        reliability = link.reliability()
        
        # PDF gereksinimleri kontrolü
        bandwidth_ok = 100 <= bandwidth <= 1000
        delay_ok = 3 <= delay <= 15
        reliability_ok = 0.95 <= reliability <= 0.999
        
        if not bandwidth_ok or not delay_ok or not reliability_ok:
            print(f"❌ Link ({u}, {v}): FAILED")
            print(f"   bandwidth: {bandwidth} (expected: [100, 1000])")
            print(f"   delay: {delay} (expected: [3, 15])")
            print(f"   reliability: {reliability} (expected: [0.95, 0.999])")
            all_valid = False
        else:
            print(f"✅ Link ({u}, {v}): OK")
            print(f"   bandwidth: {bandwidth:.1f} Mbps")
            print(f"   delay: {delay:.2f} ms")
            print(f"   reliability: {reliability:.4f}")
    
    print()
    if all_valid:
        print("✅ ISSUE #3: TÜM LINK ATTRIBUTES PDF GEREKSİNİMLERİNE UYGUN!")
    else:
        print("❌ ISSUE #3: BAZI LINK ATTRIBUTES PDF GEREKSİNİMLERİNE UYGUN DEĞİL!")
    
    return all_valid

def main():
    print("\n" + "=" * 60)
    print("BSM307 - Issue #2 & #3 Validation Test")
    print("=" * 60 + "\n")
    
    issue2_ok = test_issue2_node_attributes()
    print("\n")
    issue3_ok = test_issue3_link_attributes()
    
    print("\n" + "=" * 60)
    print("📊 ÖZET")
    print("=" * 60)
    print(f"Issue #2 (Node Attributes): {'✅ PASS' if issue2_ok else '❌ FAIL'}")
    print(f"Issue #3 (Link Attributes): {'✅ PASS' if issue3_ok else '❌ FAIL'}")
    
    if issue2_ok and issue3_ok:
        print("\n✅ TÜM TESTLER BAŞARILI! Issue #2 ve #3 kapatılabilir.")
        return 0
    else:
        print("\n❌ BAZI TESTLER BAŞARISIZ! Lütfen kodları kontrol edin.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

