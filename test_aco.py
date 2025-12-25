#!/usr/bin/env python3
"""
ACO (Ant Colony Optimization) Test Suite
BSM307 - Güz 2025

Issue #13, #14, #15: Complete ACO implementation tests
"""

import sys
import os

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import networkx as nx
from src.network.generator import RandomNetworkGenerator
from src.algorithms.aco.ant_colony import AntColonyOptimizer
from src.algorithms.aco.pheromone import PheromoneModel
from src.routing.path_validator import PathValidator
from src.metrics.delay import total_delay
from src.metrics.reliability import reliability_cost
from src.metrics.resource_cost import bandwidth_cost, weighted_sum


def test_issue13_pheromone_model():
    """Issue #13: Pheromone model test"""
    print("=" * 60)
    print("🧪 ISSUE #13: PHEROMONE MODEL TEST")
    print("=" * 60)
    
    # Küçük bir network oluştur
    generator = RandomNetworkGenerator(num_nodes=50, edge_prob=0.5, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    # Pheromone model oluştur
    pheromone = PheromoneModel(graph, initial=1.0, rho=0.1)
    
    print(f"📊 Network: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"📊 Initial pheromone: {pheromone.initial}")
    print(f"📊 Evaporation rate: {pheromone.rho}")
    
    # İlk feromon değerlerini kontrol et
    first_edge = list(graph.edges())[0]
    initial_value = pheromone.get(first_edge[0], first_edge[1])
    assert abs(initial_value - 1.0) < 0.001, f"Initial pheromone should be 1.0, got {initial_value}"
    print(f"✅ Initial pheromone value: {initial_value}")
    
    # Evaporation test
    pheromone.evaporate()
    after_evap = pheromone.get(first_edge[0], first_edge[1])
    expected = 1.0 * (1.0 - 0.1)  # 0.9
    assert abs(after_evap - expected) < 0.001, f"After evaporation should be {expected}, got {after_evap}"
    print(f"✅ After evaporation: {after_evap} (expected: {expected})")
    
    # Deposit test
    if nx.has_path(graph, 0, 10):
        path = nx.shortest_path(graph, 0, 10)
        quality = 10.0
        before_deposit = pheromone.get(path[0], path[1])
        pheromone.deposit(path, quality)
        after_deposit = pheromone.get(path[0], path[1])
        assert after_deposit > before_deposit, "Pheromone should increase after deposit"
        print(f"✅ Deposit test: before={before_deposit:.4f}, after={after_deposit:.4f}")
    
    print("\n✅ ALL Issue #13 TESTS PASSED!\n")
    return True


def test_issue14_solution_construction():
    """Issue #14: Solution construction test"""
    print("=" * 60)
    print("🧪 ISSUE #14: SOLUTION CONSTRUCTION TEST")
    print("=" * 60)
    
    # Network oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    print(f"📊 Network: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"🎯 Source: {source}, Target: {target}")
    
    # ACO oluştur
    aco = AntColonyOptimizer(
        graph=graph,
        source=source,
        target=target,
        num_ants=10,
        seed=42
    )
    
    # Path oluştur
    path = aco.construct_solution()
    
    if path is None:
        print("⚠️  Could not construct path (may happen with random selection)")
        return False
    
    print(f"📊 Constructed path: {path[:10] if len(path) > 10 else path}...")
    print(f"📊 Path length: {len(path)}")
    
    # Testler
    assert len(path) > 0, "Path should not be empty"
    assert path[0] == source, "Path should start with source"
    assert path[-1] == target, "Path should end with target"
    
    # Path geçerli olmalı
    validator = PathValidator(graph)
    assert validator.is_simple_path(path), "Path should be simple (no cycles)"
    assert validator.has_capacity(path, 500.0), "Path should have sufficient capacity"
    
    print("✅ Path is valid")
    
    # Heuristic value test
    if len(path) > 1:
        heuristic = aco._heuristic_value(path[0], path[1])
        assert heuristic > 0, "Heuristic value should be positive"
        print(f"✅ Heuristic value: {heuristic:.4f}")
    
    print("\n✅ ALL Issue #14 TESTS PASSED!\n")
    return True


def test_issue15_main_algorithm():
    """Issue #15: Main ACO algorithm loop test"""
    print("=" * 60)
    print("🧪 ISSUE #15: MAIN ACO ALGORITHM TEST")
    print("=" * 60)
    
    # Network oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    print(f"📊 Network: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"🎯 Source: {source}, Target: {target}")
    
    # ACO oluştur
    aco = AntColonyOptimizer(
        graph=graph,
        source=source,
        target=target,
        num_ants=15,
        seed=42
    )
    
    # ACO çalıştır (kısa test için 5 iterasyon)
    best_path, best_cost = aco.run(iterations=5)
    
    print(f"📊 Best path: {best_path[:15] if len(best_path) > 15 else best_path}...")
    print(f"📊 Best path length: {len(best_path)}")
    print(f"📊 Best cost: {best_cost:.4f}")
    
    # Testler
    assert len(best_path) > 0, "Best path should not be empty"
    assert best_path[0] == source, "Best path should start with source"
    assert best_path[-1] == target, "Best path should end with target"
    assert best_cost != float("inf"), "Best cost should not be infinite"
    
    # Path geçerli olmalı
    validator = PathValidator(graph)
    assert validator.is_simple_path(best_path), "Best path should be simple"
    assert validator.has_capacity(best_path, 500.0), "Best path should have capacity"
    
    print("✅ Best path is valid")
    
    # Cost manuel hesaplama ile karşılaştır
    delay = total_delay(graph=graph, path=best_path)
    rel_cost = reliability_cost(graph=graph, path=best_path)
    res_cost = bandwidth_cost(graph=graph, path=best_path)
    manual_cost = weighted_sum(delay, rel_cost, res_cost, (0.4, 0.3, 0.3))
    
    print(f"📊 Manual cost: {manual_cost:.4f}")
    assert abs(best_cost - manual_cost) < 0.001, "Cost should match manual calculation"
    
    print("\n✅ ALL Issue #15 TESTS PASSED!\n")
    return True


def test_integration():
    """Integration test: Full ACO workflow"""
    print("=" * 60)
    print("🧪 INTEGRATION TEST: Full ACO Workflow")
    print("=" * 60)
    
    # 250-node network
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    # ACO with different parameters
    configs = [
        {"alpha": 1.0, "beta": 2.0, "num_ants": 10},
        {"alpha": 2.0, "beta": 1.0, "num_ants": 15},
    ]
    
    all_passed = True
    for config in configs:
        print(f"\n📊 Testing with alpha={config['alpha']}, beta={config['beta']}, ants={config['num_ants']}")
        aco = AntColonyOptimizer(
            graph=graph,
            source=source,
            target=target,
            alpha=config["alpha"],
            beta=config["beta"],
            num_ants=config["num_ants"],
            seed=42
        )
        
        best_path, best_cost = aco.run(iterations=3)  # Kısa test
        
        print(f"   Best cost: {best_cost:.4f}, path length: {len(best_path)}")
        
        # Metrikleri hesapla
        delay = total_delay(graph=graph, path=best_path)
        rel_cost = reliability_cost(graph=graph, path=best_path)
        res_cost = bandwidth_cost(graph=graph, path=best_path)
        
        print(f"   Metrics: delay={delay:.2f}ms, rel_cost={rel_cost:.4f}, res_cost={res_cost:.4f}")
        
        # Geçerlilik kontrolü
        validator = PathValidator(graph)
        if not (validator.is_simple_path(best_path) and validator.has_capacity(best_path, 500.0)):
            print(f"   ❌ Path is invalid!")
            all_passed = False
        else:
            print(f"   ✅ Path is valid")
    
    if all_passed:
        print("\n✅ ALL INTEGRATION TESTS PASSED!\n")
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED!\n")
    
    return all_passed


def main():
    print("\n" + "=" * 60)
    print("BSM307 - Issue #13, #14, #15: ACO Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test Issue #13
        test13_ok = test_issue13_pheromone_model()
        
        # Test Issue #14
        test14_ok = test_issue14_solution_construction()
        
        # Test Issue #15
        test15_ok = test_issue15_main_algorithm()
        
        # Integration test
        test_int_ok = test_integration()
        
        # Özet
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Issue #13 (Pheromone Model): {'✅ PASS' if test13_ok else '❌ FAIL'}")
        print(f"Issue #14 (Solution Construction): {'✅ PASS' if test14_ok else '❌ FAIL'}")
        print(f"Issue #15 (Main Algorithm): {'✅ PASS' if test15_ok else '❌ FAIL'}")
        print(f"Integration tests: {'✅ PASS' if test_int_ok else '❌ FAIL'}")
        
        if test13_ok and test14_ok and test15_ok and test_int_ok:
            print("\n✅ ALL TESTS PASSED! Issue #13, #14, #15 implementation is correct.")
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

