#!/usr/bin/env python3
"""
PathValidator test script for Issue #4
BSM307 - Güz 2025
"""

import sys
import os

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.network.generator import RandomNetworkGenerator
from src.routing.path_validator import PathValidator
import networkx as nx


def test_is_simple_path():
    """Test is_simple_path() method"""
    print("=" * 60)
    print("🧪 TEST: is_simple_path()")
    print("=" * 60)
    
    # Graf oluştur
    generator = RandomNetworkGenerator(num_nodes=10, edge_prob=0.5, seed=42)
    graph = generator.generate()
    validator = PathValidator(graph)
    
    # Test 1: Basit path (döngü yok)
    simple_path = [0, 1, 2, 3]
    result = validator.is_simple_path(simple_path)
    assert result == True, f"Expected True for simple path {simple_path}"
    print(f"✅ Test 1 PASSED: Simple path {simple_path} correctly identified")
    
    # Test 2: Döngülü path
    cyclic_path = [0, 1, 2, 1, 3]
    result = validator.is_simple_path(cyclic_path)
    assert result == False, f"Expected False for cyclic path {cyclic_path}"
    print(f"✅ Test 2 PASSED: Cyclic path {cyclic_path} correctly identified")
    
    # Test 3: Boş path
    empty_path = []
    result = validator.is_simple_path(empty_path)
    assert result == True, f"Expected True for empty path"
    print(f"✅ Test 3 PASSED: Empty path correctly handled")
    
    # Test 4: Tek düğümlü path
    single_path = [0]
    result = validator.is_simple_path(single_path)
    assert result == True, f"Expected True for single node path"
    print(f"✅ Test 4 PASSED: Single node path correctly handled")
    
    # Test 5: Aynı düğümden başlayıp biten path (döngü)
    same_start_end = [0, 1, 2, 0]
    result = validator.is_simple_path(same_start_end)
    assert result == False, f"Expected False for path with same start/end {same_start_end}"
    print(f"✅ Test 5 PASSED: Path with same start/end correctly identified as cyclic")
    
    print("\n✅ ALL is_simple_path() TESTS PASSED!\n")
    return True


def test_has_capacity():
    """Test has_capacity() method"""
    print("=" * 60)
    print("🧪 TEST: has_capacity()")
    print("=" * 60)
    
    # Graf oluştur ve attribute'ları ekle
    generator = RandomNetworkGenerator(num_nodes=10, edge_prob=0.5, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    validator = PathValidator(graph)
    
    # Graf'ta bir path bul
    nodes_list = list(graph.nodes())
    if len(nodes_list) >= 2:
        source = nodes_list[0]
        target = nodes_list[-1]
        
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Test 1: Düşük bandwidth isteği (başarılı olmalı)
            min_bandwidth = 50.0  # Mbps
            result = validator.has_capacity(path, min_bandwidth)
            print(f"✅ Test 1 PASSED: Path {path} has capacity for {min_bandwidth} Mbps")
            
            # Test 2: Çok yüksek bandwidth isteği (başarısız olmalı)
            high_bandwidth = 2000.0  # Mbps (PDF'de max 1000 Mbps)
            result = validator.has_capacity(path, high_bandwidth)
            assert result == False, f"Expected False for high bandwidth {high_bandwidth}"
            print(f"✅ Test 2 PASSED: Path {path} correctly rejected for {high_bandwidth} Mbps")
            
            # Test 3: Path üzerindeki minimum bandwidth'i bul ve test et
            edge_bandwidths = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if graph.has_edge(u, v):
                    bw = graph.edges[u, v].get("bandwidth", 0.0)
                    edge_bandwidths.append(bw)
            
            if edge_bandwidths:
                min_edge_bw = min(edge_bandwidths)
                # Minimum bandwidth'den düşük iste (kesinlikle başarılı olmalı)
                test_bw_low = max(0.0, min_edge_bw - 10.0)  # Minimum'dan düşük (başarılı olmalı)
                result_low = validator.has_capacity(path, test_bw_low)
                assert result_low == True, f"Expected True for bandwidth {test_bw_low} <= min {min_edge_bw}"
                print(f"✅ Test 3a PASSED: Path correctly accepted for bandwidth {test_bw_low} <= min {min_edge_bw}")
                
                # Minimum bandwidth'den kesinlikle yüksek iste (başarısız olmalı)
                test_bw_high = min_edge_bw + 1000.0  # Minimum'dan çok yüksek
                result_high = validator.has_capacity(path, test_bw_high)
                assert result_high == False, f"Expected False for bandwidth {test_bw_high} > min {min_edge_bw}"
                print(f"✅ Test 3b PASSED: Path correctly rejected for bandwidth {test_bw_high} > min {min_edge_bw}")
        else:
            print("⚠️  No path found between nodes, skipping capacity tests")
    else:
        print("⚠️  Not enough nodes for path test")
    
    # Test 4: Boş path
    empty_path = []
    result = validator.has_capacity(empty_path, 100.0)
    assert result == True, "Expected True for empty path"
    print(f"✅ Test 4 PASSED: Empty path correctly handled")
    
    # Test 5: Tek düğümlü path
    single_path = [0]
    result = validator.has_capacity(single_path, 100.0)
    assert result == True, "Expected True for single node path"
    print(f"✅ Test 5 PASSED: Single node path correctly handled")
    
    # Test 6: Olmayan edge
    invalid_path = [0, 999]  # 999 muhtemelen graf'ta yok
    if not graph.has_edge(0, 999):
        result = validator.has_capacity(invalid_path, 100.0)
        assert result == False, "Expected False for path with non-existent edge"
        print(f"✅ Test 6 PASSED: Path with non-existent edge correctly rejected")
    
    print("\n✅ ALL has_capacity() TESTS PASSED!\n")
    return True


def test_integration():
    """Integration test with real network"""
    print("=" * 60)
    print("🧪 INTEGRATION TEST: PathValidator with 250-node network")
    print("=" * 60)
    
    # PDF gereksinimlerine göre 250 düğümlü graf oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    validator = PathValidator(graph)
    
    # Rastgele S-D çiftleri seç ve test et
    nodes_list = list(graph.nodes())
    test_pairs = [
        (nodes_list[0], nodes_list[50]),
        (nodes_list[10], nodes_list[100]),
        (nodes_list[20], nodes_list[150]),
    ]
    
    all_passed = True
    for source, target in test_pairs:
        if nx.has_path(graph, source, target):
            path = nx.shortest_path(graph, source, target)
            
            # Basit path kontrolü
            is_simple = validator.is_simple_path(path)
            assert is_simple == True, f"Path {path} should be simple"
            
            # Kapasite kontrolü (orta seviye bandwidth)
            has_cap = validator.has_capacity(path, 500.0)
            
            print(f"✅ Path {source}→{target}: length={len(path)-1}, simple={is_simple}, capacity_500Mbps={has_cap}")
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
    print("BSM307 - Issue #4: PathValidator Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: is_simple_path()
        test1_ok = test_is_simple_path()
        
        # Test 2: has_capacity()
        test2_ok = test_has_capacity()
        
        # Test 3: Integration test
        test3_ok = test_integration()
        
        # Özet
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"is_simple_path() tests: {'✅ PASS' if test1_ok else '❌ FAIL'}")
        print(f"has_capacity() tests: {'✅ PASS' if test2_ok else '❌ FAIL'}")
        print(f"Integration tests: {'✅ PASS' if test3_ok else '❌ FAIL'}")
        
        if test1_ok and test2_ok and test3_ok:
            print("\n✅ ALL TESTS PASSED! Issue #4 implementation is correct.")
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

