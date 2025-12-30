#!/usr/bin/env python3
"""
Metrics test script for Issue #5, #6, #7, #8
BSM307 - Güz 2025
"""

import sys
import os
import math

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.network.generator import RandomNetworkGenerator
from src.metrics.delay import total_delay
from src.metrics.reliability import reliability_cost
from src.metrics.resource_cost import bandwidth_cost, weighted_sum
import networkx as nx


def test_issue5_total_delay():
    """Test Issue #5: Total Delay"""
    print("=" * 60)
    print("🧪 TEST: Issue #5 - Total Delay")
    print("=" * 60)
    
    # Test 1: Direkt delay listesi ile
    delays = [3.5, 5.2, 7.8, 4.1]
    result = total_delay(path_delays=delays)
    expected = sum(delays)
    assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    print(f"✅ Test 1 PASSED: Direct delays list {delays} → {result:.2f} ms")
    
    # Test 2: Graph ve path ile
    generator = RandomNetworkGenerator(num_nodes=10, edge_prob=0.5, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    if len(nodes_list) >= 2:
        source = nodes_list[0]
        target = nodes_list[-1]
        
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Manuel hesapla
            manual_total = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if graph.has_edge(u, v):
                    manual_total += graph.edges[u, v].get("delay", 0.0)
            
            # Fonksiyon ile hesapla
            result = total_delay(graph=graph, path=path)
            
            assert abs(result - manual_total) < 0.01, f"Expected {manual_total}, got {result}"
            print(f"✅ Test 2 PASSED: Graph path {path} → {result:.2f} ms")
    
    # Test 3: Boş path
    result = total_delay(graph=graph, path=[])
    assert result == 0.0, f"Expected 0.0 for empty path, got {result}"
    print(f"✅ Test 3 PASSED: Empty path → 0.0 ms")
    
    print("\n✅ ALL Issue #5 TESTS PASSED!\n")
    return True


def test_issue6_reliability_cost():
    """Test Issue #6: Reliability Cost (-log(R))"""
    print("=" * 60)
    print("🧪 TEST: Issue #6 - Reliability Cost")
    print("=" * 60)
    
    # Test 1: Direkt reliability listesi ile
    reliabilities = [0.95, 0.98, 0.99]
    result = reliability_cost(path_reliabilities=reliabilities)
    
    # Manuel hesapla
    R = 1.0
    for r in reliabilities:
        R *= r
    expected = -math.log(R)
    
    assert abs(result - expected) < 0.0001, f"Expected {expected:.4f}, got {result:.4f}"
    print(f"✅ Test 1 PASSED: Direct reliabilities {reliabilities} → cost {result:.4f}")
    
    # Test 2: Graph ve path ile
    generator = RandomNetworkGenerator(num_nodes=10, edge_prob=0.5, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    if len(nodes_list) >= 2:
        source = nodes_list[0]
        target = nodes_list[-1]
        
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Manuel hesapla
            R = 1.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if graph.has_edge(u, v):
                    R *= graph.edges[u, v].get("reliability", 1.0)
            expected = -math.log(R) if R > 0 else float("inf")
            
            # Fonksiyon ile hesapla
            result = reliability_cost(graph=graph, path=path)
            
            assert abs(result - expected) < 0.0001, f"Expected {expected:.4f}, got {result:.4f}"
            print(f"✅ Test 2 PASSED: Graph path {path} → cost {result:.4f}")
    
    # Test 3: Boş path
    result = reliability_cost(graph=graph, path=[])
    assert result == 0.0, f"Expected 0.0 for empty path, got {result}"
    print(f"✅ Test 3 PASSED: Empty path → 0.0")
    
    print("\n✅ ALL Issue #6 TESTS PASSED!\n")
    return True


def test_issue7_bandwidth_cost():
    """Test Issue #7: Bandwidth Cost (1Gbps/BW)"""
    print("=" * 60)
    print("🧪 TEST: Issue #7 - Bandwidth Cost")
    print("=" * 60)
    
    # Test 1: Direkt bandwidth listesi ile (Mbps)
    bandwidths = [500.0, 750.0, 1000.0]  # Mbps
    result = bandwidth_cost(path_bandwidths=bandwidths)
    
    # Manuel hesapla: 1Gbps / BW (Gbps cinsinden)
    # 500 Mbps = 0.5 Gbps → cost = 1.0 / 0.5 = 2.0
    # 750 Mbps = 0.75 Gbps → cost = 1.0 / 0.75 = 1.333...
    # 1000 Mbps = 1.0 Gbps → cost = 1.0 / 1.0 = 1.0
    expected = (1.0 / 0.5) + (1.0 / 0.75) + (1.0 / 1.0)
    
    assert abs(result - expected) < 0.01, f"Expected {expected:.4f}, got {result:.4f}"
    print(f"✅ Test 1 PASSED: Direct bandwidths {bandwidths} Mbps → cost {result:.4f}")
    
    # Test 2: Graph ve path ile
    generator = RandomNetworkGenerator(num_nodes=10, edge_prob=0.5, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    if len(nodes_list) >= 2:
        source = nodes_list[0]
        target = nodes_list[-1]
        
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Manuel hesapla
            manual_total = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if graph.has_edge(u, v):
                    bw_mbps = graph.edges[u, v].get("bandwidth", 0.0)
                    bw_gbps = bw_mbps / 1000.0
                    if bw_gbps > 0:
                        manual_total += 1.0 / bw_gbps
            
            # Fonksiyon ile hesapla
            result = bandwidth_cost(graph=graph, path=path)
            
            assert abs(result - manual_total) < 0.01, f"Expected {manual_total:.4f}, got {result:.4f}"
            print(f"✅ Test 2 PASSED: Graph path {path} → cost {result:.4f}")
    
    # Test 3: Boş path
    result = bandwidth_cost(graph=graph, path=[])
    assert result == 0.0, f"Expected 0.0 for empty path, got {result}"
    print(f"✅ Test 3 PASSED: Empty path → 0.0")
    
    print("\n✅ ALL Issue #7 TESTS PASSED!\n")
    return True


def test_issue8_weighted_sum():
    """Test Issue #8: Weighted Sum"""
    print("=" * 60)
    print("🧪 TEST: Issue #8 - Weighted Sum")
    print("=" * 60)
    
    # Test 1: Basit hesaplama
    delay = 10.5  # ms
    reliability_cost_val = 0.05  # -log(R)
    resource_cost_val = 2.5  # 1Gbps/BW toplamı
    weights = (0.4, 0.3, 0.3)  # (w_delay, w_reliability, w_resource)
    
    result = weighted_sum(delay, reliability_cost_val, resource_cost_val, weights)
    expected = 0.4 * 10.5 + 0.3 * 0.05 + 0.3 * 2.5
    
    assert abs(result - expected) < 0.0001, f"Expected {expected:.4f}, got {result:.4f}"
    print(f"✅ Test 1 PASSED: Weighted sum = {result:.4f}")
    
    # Test 2: Farklı ağırlıklar
    weights2 = (0.5, 0.3, 0.2)
    result2 = weighted_sum(delay, reliability_cost_val, resource_cost_val, weights2)
    expected2 = 0.5 * 10.5 + 0.3 * 0.05 + 0.2 * 2.5
    
    assert abs(result2 - expected2) < 0.0001, f"Expected {expected2:.4f}, got {result2:.4f}"
    print(f"✅ Test 2 PASSED: Different weights → {result2:.4f}")
    
    # Test 3: Sıfır ağırlıklar
    weights3 = (0.0, 0.5, 0.5)
    result3 = weighted_sum(delay, reliability_cost_val, resource_cost_val, weights3)
    expected3 = 0.0 * 10.5 + 0.5 * 0.05 + 0.5 * 2.5
    
    assert abs(result3 - expected3) < 0.0001, f"Expected {expected3:.4f}, got {result3:.4f}"
    print(f"✅ Test 3 PASSED: Zero weight for delay → {result3:.4f}")
    
    print("\n✅ ALL Issue #8 TESTS PASSED!\n")
    return True


def test_integration():
    """Integration test with real network"""
    print("=" * 60)
    print("🧪 INTEGRATION TEST: All metrics with 250-node network")
    print("=" * 60)
    
    # PDF gereksinimlerine göre 250 düğümlü graf oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    # Rastgele S-D çiftleri seç ve test et
    nodes_list = list(graph.nodes())
    test_pairs = [
        (nodes_list[0], nodes_list[50]),
        (nodes_list[10], nodes_list[100]),
    ]
    
    all_passed = True
    for source, target in test_pairs:
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Tüm metrikleri hesapla
            delay = total_delay(graph=graph, path=path)
            rel_cost = reliability_cost(graph=graph, path=path)
            res_cost = bandwidth_cost(graph=graph, path=path)
            
            # Ağırlıklı toplam
            weights = (0.4, 0.3, 0.3)
            weighted = weighted_sum(delay, rel_cost, res_cost, weights)
            
            print(f"✅ Path {source}→{target}: delay={delay:.2f}ms, rel_cost={rel_cost:.4f}, res_cost={res_cost:.4f}, weighted={weighted:.4f}")
            
            # Değerlerin mantıklı olduğunu kontrol et
            assert delay >= 0, "Delay should be non-negative"
            assert rel_cost >= 0, "Reliability cost should be non-negative"
            assert res_cost >= 0, "Resource cost should be non-negative"
            assert not math.isnan(weighted), "Weighted sum should not be NaN"
            assert not math.isinf(weighted), "Weighted sum should not be infinite"
        else:
            print(f"⚠️  No path between {source} and {target}")
            all_passed = False
    
    if all_passed:
        print("\n✅ INTEGRATION TEST PASSED!\n")
    else:
        print("\n⚠️  Some integration tests had issues\n")
    
    return all_passed


def main():
    print("\n" + "=" * 60)
    print("BSM307 - Issue #5, #6, #7, #8: Metrics Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test Issue #5
        test5_ok = test_issue5_total_delay()
        
        # Test Issue #6
        test6_ok = test_issue6_reliability_cost()
        
        # Test Issue #7
        test7_ok = test_issue7_bandwidth_cost()
        
        # Test Issue #8
        test8_ok = test_issue8_weighted_sum()
        
        # Integration test
        test_int_ok = test_integration()
        
        # Özet
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Issue #5 (Total Delay): {'✅ PASS' if test5_ok else '❌ FAIL'}")
        print(f"Issue #6 (Reliability Cost): {'✅ PASS' if test6_ok else '❌ FAIL'}")
        print(f"Issue #7 (Bandwidth Cost): {'✅ PASS' if test7_ok else '❌ FAIL'}")
        print(f"Issue #8 (Weighted Sum): {'✅ PASS' if test8_ok else '❌ FAIL'}")
        print(f"Integration tests: {'✅ PASS' if test_int_ok else '❌ FAIL'}")
        
        if test5_ok and test6_ok and test7_ok and test8_ok and test_int_ok:
            print("\n✅ ALL TESTS PASSED! Issue #5, #6, #7, #8 implementation is correct.")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED! Please check the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

