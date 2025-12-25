#!/usr/bin/env python3
"""
GA (Genetic Algorithm) Test Suite
BSM307 - Güz 2025

Issue #9, #10, #11, #12: Complete GA implementation tests
"""

import sys
import os

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import networkx as nx
from src.network.generator import RandomNetworkGenerator
from src.algorithms.ga.genetic_algorithm import GeneticAlgorithm
from src.routing.path_validator import PathValidator
from src.metrics.delay import total_delay
from src.metrics.reliability import reliability_cost
from src.metrics.resource_cost import bandwidth_cost, weighted_sum


def test_issue9_population_initialization():
    """Issue #9: Population initialization test"""
    print("=" * 60)
    print("🧪 ISSUE #9: POPULATION INITIALIZATION TEST")
    print("=" * 60)
    
    # 250-node network oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    # S-D çifti seç
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    print(f"📊 Network: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"🎯 Source: {source}, Target: {target}")
    
    # GA oluştur
    ga = GeneticAlgorithm(
        graph=graph,
        source=source,
        target=target,
        population_size=30,
        seed=42
    )
    
    # Popülasyon oluştur
    population = ga.initialize_population()
    
    # Testler
    assert len(population) > 0, "Population should not be empty"
    print(f"✅ Population size: {len(population)}")
    
    # Her path geçerli olmalı
    validator = PathValidator(graph)
    all_valid = True
    for i, path in enumerate(population):
        is_simple = validator.is_simple_path(path)
        has_cap = validator.has_capacity(path, 500.0)
        is_valid = (path[0] == source and path[-1] == target and 
                   is_simple and has_cap)
        
        if not is_valid:
            print(f"❌ Path {i} is invalid: {path[:10] if len(path) > 10 else path}")
            all_valid = False
        else:
            print(f"✅ Path {i}: length={len(path)}, valid={is_valid}")
    
    assert all_valid, "All paths in population should be valid"
    print("\n✅ ALL Issue #9 TESTS PASSED!\n")
    return True


def test_issue10_fitness_function():
    """Issue #10: Fitness function test"""
    print("=" * 60)
    print("🧪 ISSUE #10: FITNESS FUNCTION TEST")
    print("=" * 60)
    
    # Network oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    # GA oluştur
    ga = GeneticAlgorithm(
        graph=graph,
        source=source,
        target=target,
        weights=(0.4, 0.3, 0.3),
        seed=42
    )
    
    # Geçerli bir path bul
    if nx.has_path(graph, source, target):
        path = nx.shortest_path(graph, source, target)
        
        # Fitness hesapla
        fitness = ga.fitness(path)
        
        print(f"📊 Path: {path[:10] if len(path) > 10 else path}...")
        print(f"📊 Path length: {len(path)}")
        print(f"📊 Fitness: {fitness:.4f}")
        
        # Fitness mantıklı olmalı
        assert not (fitness < 0), "Fitness should be non-negative"
        assert not (fitness == float("inf")), "Fitness should not be infinite"
        
        # Manuel hesaplama ile karşılaştır
        delay = total_delay(graph=graph, path=path)
        rel_cost = reliability_cost(graph=graph, path=path)
        res_cost = bandwidth_cost(graph=graph, path=path)
        manual_fitness = weighted_sum(delay, rel_cost, res_cost, (0.4, 0.3, 0.3))
        
        print(f"📊 Manual calculation: {manual_fitness:.4f}")
        assert abs(fitness - manual_fitness) < 0.001, "Fitness should match manual calculation"
        
        # Geçersiz path için sonsuz fitness
        invalid_path = [source, target]  # Edge yoksa geçersiz
        invalid_fitness = ga.fitness(invalid_path)
        if invalid_fitness == float("inf"):
            print("✅ Invalid path correctly returns infinite fitness")
        else:
            print(f"⚠️  Invalid path fitness: {invalid_fitness} (expected inf)")
        
        print("\n✅ ALL Issue #10 TESTS PASSED!\n")
        return True
    else:
        print("❌ No path between source and target")
        return False


def test_issue11_crossover_mutation():
    """Issue #11: Crossover and mutation test"""
    print("=" * 60)
    print("🧪 ISSUE #11: CROSSOVER & MUTATION TEST")
    print("=" * 60)
    
    # Network oluştur
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    # GA oluştur
    ga = GeneticAlgorithm(
        graph=graph,
        source=source,
        target=target,
        seed=42
    )
    
    # İki geçerli parent path oluştur
    if nx.has_path(graph, source, target):
        parent1 = nx.shortest_path(graph, source, target)
        
        # İkinci path (biraz farklı)
        try:
            # All simple paths'ten birini al
            all_paths = list(nx.all_simple_paths(graph, source, target, cutoff=10))
            parent2 = all_paths[1] if len(all_paths) > 1 else parent1
        except:
            parent2 = parent1
        
        print(f"📊 Parent1: length={len(parent1)}, path={parent1[:10] if len(parent1) > 10 else parent1}")
        print(f"📊 Parent2: length={len(parent2)}, path={parent2[:10] if len(parent2) > 10 else parent2}")
        
        # Crossover test
        child1, child2 = ga._crossover(parent1, parent2)
        print(f"📊 Child1: length={len(child1)}, path={child1[:10] if len(child1) > 10 else child1}")
        print(f"📊 Child2: length={len(child2)}, path={child2[:10] if len(child2) > 10 else child2}")
        
        # Child'lar source ve target'a sahip olmalı
        assert child1[0] == source, "Child1 should start with source"
        assert child1[-1] == target, "Child1 should end with target"
        assert child2[0] == source, "Child2 should start with source"
        assert child2[-1] == target, "Child2 should end with target"
        print("✅ Crossover produces valid children (source/target check)")
        
        # Mutation test
        mutated = ga._mutate(parent1.copy())
        print(f"📊 Mutated: length={len(mutated)}, path={mutated[:10] if len(mutated) > 10 else mutated}")
        
        assert mutated[0] == source, "Mutated path should start with source"
        assert mutated[-1] == target, "Mutated path should end with target"
        print("✅ Mutation produces valid path (source/target check)")
        
        print("\n✅ ALL Issue #11 TESTS PASSED!\n")
        return True
    else:
        print("❌ No path between source and target")
        return False


def test_issue12_main_algorithm():
    """Issue #12: Main GA algorithm loop test"""
    print("=" * 60)
    print("🧪 ISSUE #12: MAIN GA ALGORITHM TEST")
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
    
    # GA oluştur
    ga = GeneticAlgorithm(
        graph=graph,
        source=source,
        target=target,
        population_size=20,
        seed=42
    )
    
    # GA çalıştır (kısa test için 5 generation)
    best_path, best_fitness = ga.run(generations=5)
    
    print(f"📊 Best path: {best_path[:15] if len(best_path) > 15 else best_path}...")
    print(f"📊 Best path length: {len(best_path)}")
    print(f"📊 Best fitness: {best_fitness:.4f}")
    
    # Testler
    assert len(best_path) > 0, "Best path should not be empty"
    assert best_path[0] == source, "Best path should start with source"
    assert best_path[-1] == target, "Best path should end with target"
    assert best_fitness != float("inf"), "Best fitness should not be infinite"
    
    # Path geçerli olmalı
    validator = PathValidator(graph)
    assert validator.is_simple_path(best_path), "Best path should be simple"
    assert validator.has_capacity(best_path, 500.0), "Best path should have capacity"
    
    print("✅ Best path is valid")
    
    # Fitness manuel hesaplama ile karşılaştır
    delay = total_delay(graph=graph, path=best_path)
    rel_cost = reliability_cost(graph=graph, path=best_path)
    res_cost = bandwidth_cost(graph=graph, path=best_path)
    manual_fitness = weighted_sum(delay, rel_cost, res_cost, (0.4, 0.3, 0.3))
    
    print(f"📊 Manual fitness: {manual_fitness:.4f}")
    assert abs(best_fitness - manual_fitness) < 0.001, "Fitness should match"
    
    print("\n✅ ALL Issue #12 TESTS PASSED!\n")
    return True


def test_integration():
    """Integration test: Full GA workflow"""
    print("=" * 60)
    print("🧪 INTEGRATION TEST: Full GA Workflow")
    print("=" * 60)
    
    # 250-node network
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    nodes_list = list(graph.nodes())
    source = nodes_list[0]
    target = nodes_list[100]
    
    # GA with different weights
    weights_configs = [
        (0.5, 0.3, 0.2),  # Delay ağırlıklı
        (0.3, 0.5, 0.2),  # Reliability ağırlıklı
        (0.3, 0.2, 0.5),  # Resource ağırlıklı
    ]
    
    all_passed = True
    for weights in weights_configs:
        print(f"\n📊 Testing with weights: {weights}")
        ga = GeneticAlgorithm(
            graph=graph,
            source=source,
            target=target,
            weights=weights,
            population_size=10,  # Daha küçük popülasyon (hızlı test)
            seed=42
        )
        
        best_path, best_fitness = ga.run(generations=3)  # Çok kısa test
        
        print(f"   Best fitness: {best_fitness:.4f}, path length: {len(best_path)}")
        
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
    print("BSM307 - Issue #9, #10, #11, #12: GA Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test Issue #9
        test9_ok = test_issue9_population_initialization()
        
        # Test Issue #10
        test10_ok = test_issue10_fitness_function()
        
        # Test Issue #11
        test11_ok = test_issue11_crossover_mutation()
        
        # Test Issue #12
        test12_ok = test_issue12_main_algorithm()
        
        # Integration test
        test_int_ok = test_integration()
        
        # Özet
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Issue #9 (Population Init): {'✅ PASS' if test9_ok else '❌ FAIL'}")
        print(f"Issue #10 (Fitness Function): {'✅ PASS' if test10_ok else '❌ FAIL'}")
        print(f"Issue #11 (Crossover & Mutation): {'✅ PASS' if test11_ok else '❌ FAIL'}")
        print(f"Issue #12 (Main Algorithm): {'✅ PASS' if test12_ok else '❌ FAIL'}")
        print(f"Integration tests: {'✅ PASS' if test_int_ok else '❌ FAIL'}")
        
        if test9_ok and test10_ok and test11_ok and test12_ok and test_int_ok:
            print("\n✅ ALL TESTS PASSED! Issue #9, #10, #11, #12 implementation is correct.")
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

