"""
GA operatörleri
BSM307 - Güz 2025

Issue #11: Crossover and mutation operators
"""

import random
from typing import List, Tuple

import networkx as nx

from ...utils.logger import get_logger

logger = get_logger(__name__)


def crossover(
    parent_a: List[int],
    parent_b: List[int],
    graph: nx.Graph,
    source: int,
    target: int,
) -> Tuple[List[int], List[int]]:
    """
    Issue #11: İki parent path'ten yeni child path'ler üreten crossover.
    
    Args:
        parent_a: İlk parent path
        parent_b: İkinci parent path
        graph: NetworkX graph
        source: Başlangıç düğümü
        target: Hedef düğümü
        
    Returns:
        (child1, child2) tuple
    """
    if len(parent_a) <= 2 or len(parent_b) <= 2:
        return parent_a.copy(), parent_b.copy()
    
    # Crossover point seç
    start = random.randint(1, len(parent_a) - 2)
    end = random.randint(start + 1, len(parent_a) - 1)
    
    # Child1: Parent1'den segment + Parent2'den kalan
    segment = parent_a[start:end]
    child1 = [source] + segment + [target]
    
    # Parent2'den segment'te olmayan düğümleri ekle
    for node in parent_b[1:-1]:
        if node not in segment and node not in child1:
            insert_pos = random.randint(1, len(child1) - 1)
            child1.insert(insert_pos, node)
    
    # Child2: Parent2'den segment + Parent1'den kalan
    segment2 = parent_b[start:min(end, len(parent_b))] if end < len(parent_b) else parent_b[start:]
    child2 = [source] + segment2 + [target]
    
    for node in parent_a[1:-1]:
        if node not in segment2 and node not in child2:
            insert_pos = random.randint(1, len(child2) - 1)
            child2.insert(insert_pos, node)
    
    logger.debug("Crossover: parent_a=%s, parent_b=%s -> child1=%s, child2=%s",
                 parent_a[:5] if len(parent_a) > 5 else parent_a,
                 parent_b[:5] if len(parent_b) > 5 else parent_b,
                 child1[:5] if len(child1) > 5 else child1,
                 child2[:5] if len(child2) > 5 else child2)
    
    return child1, child2


def mutate(
    chromosome: List[int],
    graph: nx.Graph,
    source: int,
    target: int,
) -> List[int]:
    """
    Issue #11: Path'i rastgele değiştiren mutasyon operatörü.
    
    Args:
        chromosome: Mutasyona uğrayacak path
        graph: NetworkX graph
        source: Başlangıç düğümü
        target: Hedef düğümü
        
    Returns:
        Mutasyona uğramış path
    """
    if len(chromosome) <= 2:
        return chromosome.copy()
    
    mutated = chromosome.copy()
    
    # Rastgele bir pozisyon seç (source ve target hariç)
    pos = random.randint(1, len(mutated) - 2)
    old_node = mutated[pos]
    
    # Önceki ve sonraki düğümlerin komşularını bul
    prev_node = mutated[pos - 1]
    next_node = mutated[pos + 1]
    
    # Önceki düğümün komşularından birini seç (next_node'a gidebilen)
    prev_neighbors = list(graph.neighbors(prev_node))
    valid_replacements = [
        n for n in prev_neighbors
        if n != old_node and graph.has_edge(n, next_node)
    ]
    
    if valid_replacements:
        mutated[pos] = random.choice(valid_replacements)
    else:
        # Geçerli değişim yok, düğümü kaldır (eğer edge varsa)
        if graph.has_edge(prev_node, next_node):
            mutated.pop(pos)
    
    logger.debug("Mutation: %s -> %s",
                 chromosome[:5] if len(chromosome) > 5 else chromosome,
                 mutated[:5] if len(mutated) > 5 else mutated)
    
    return mutated
