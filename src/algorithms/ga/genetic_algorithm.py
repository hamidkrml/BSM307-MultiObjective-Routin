"""
Genetik Algoritma - Çok Amaçlı Rotalama
BSM307 - Güz 2025

Issue #9, #10, #11, #12: Complete GA implementation
"""

import math
import random
from typing import List, Optional, Sequence, Tuple

import networkx as nx

from ...metrics.delay import total_delay
from ...metrics.reliability import reliability_cost
from ...metrics.resource_cost import bandwidth_cost, weighted_sum
from ...routing.path_validator import PathValidator
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GeneticAlgorithm:
    """
    Genetik Algoritma ile çok amaçlı rota optimizasyonu.
    
    Issue #9: Population initialization
    Issue #10: Fitness function
    Issue #11: Crossover & mutation operators
    Issue #12: Main algorithm loop
    """

    def __init__(
        self,
        graph: nx.Graph,
        source: int,
        target: int,
        weights: Sequence[float] = (0.4, 0.3, 0.3),
        required_bandwidth: float = 500.0,
        population_size: int = 50,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.05,
        seed: Optional[int] = None,
    ):
        """
        Args:
            graph: NetworkX graph objesi
            source: Başlangıç düğümü
            target: Hedef düğümü
            weights: (delay_weight, reliability_weight, resource_weight) tuple
            required_bandwidth: Minimum gerekli bandwidth (Mbps)
            population_size: Popülasyon boyutu
            crossover_rate: Çaprazlama olasılığı
            mutation_rate: Mutasyon olasılığı
            seed: Rastgele tohum (reproducibility için)
        """
        self.graph = graph
        self.source = source
        self.target = target
        self.weights = tuple(weights)
        self.required_bandwidth = required_bandwidth
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.validator = PathValidator(graph)
        
        if seed is not None:
            random.seed(seed)
        
        logger.info(
            "Initialized GeneticAlgorithm: source=%s, target=%s, weights=%s, pop_size=%s",
            source, target, weights, population_size
        )

    def initialize_population(self, size: Optional[int] = None) -> List[List[int]]:
        """
        Issue #9: Rastgele geçerli path'lerden oluşan başlangıç popülasyonu oluştur.
        
        Strateji:
        1. Shortest path'i ekle (deterministic)
        2. Kalan popülasyon için rastgele path'ler üret
        3. Her path geçerli olmalı (simple path, capacity check)
        
        Args:
            size: Popülasyon boyutu (None ise self.population_size kullanılır)
            
        Returns:
            Geçerli path'lerden oluşan popülasyon listesi
        """
        pop_size = size if size is not None else self.population_size
        logger.debug("Initializing population size=%s", pop_size)
        
        population = []
        max_attempts = pop_size * 50  # Artırıldı: Her path için daha fazla deneme
        
        # 1. Shortest path'i ekle (deterministic, iyi başlangıç)
        if nx.has_path(self.graph, self.source, self.target):
            try:
                shortest = nx.shortest_path(self.graph, self.source, self.target)
                if self._is_valid_path(shortest):
                    population.append(shortest)
                    logger.debug("Added shortest path to population: %s", shortest)
            except nx.NetworkXNoPath:
                pass
        
        # 2. Weighted shortest paths ekle (ağırlıklara göre farklı path'ler)
        wd, wr, wc = self.weights
        unique_paths = set(tuple(p) for p in population)  # Duplicate kontrolü için set
        
        if len(population) < pop_size:
            # Delay ağırlığı yüksekse, delay-weighted path ekle
            if wd > 0.3:
                try:
                    delay_path = nx.shortest_path(
                        self.graph, self.source, self.target, 
                        weight="delay"
                    )
                    if self._is_valid_path(delay_path):
                        path_tuple = tuple(delay_path)
                        if path_tuple not in unique_paths:
                            population.append(delay_path)
                            unique_paths.add(path_tuple)
                            logger.debug("Added delay-weighted path to population")
                except (nx.NetworkXNoPath, KeyError):
                    pass
            
            # Resource ağırlığı yüksekse, bandwidth-weighted path ekle (yüksek bandwidth = düşük cost)
            if wc > 0.3:
                try:
                    # Bandwidth'e göre path bulmak için edge weight'i 1/bandwidth yap
                    G_weighted = self.graph.copy()
                    for u, v in G_weighted.edges():
                        bw = G_weighted.edges[u, v].get("bandwidth", 100.0)
                        # Yüksek bandwidth = düşük weight (ters çevir)
                        G_weighted.edges[u, v]["bw_weight"] = 1000.0 / max(bw, 1.0)
                    
                    bw_path = nx.shortest_path(
                        G_weighted, self.source, self.target,
                        weight="bw_weight"
                    )
                    if self._is_valid_path(bw_path):
                        path_tuple = tuple(bw_path)
                        if path_tuple not in unique_paths:
                            population.append(bw_path)
                            unique_paths.add(path_tuple)
                            logger.debug("Added bandwidth-weighted path to population")
                except (nx.NetworkXNoPath, KeyError):
                    pass
            
            # Reliability ağırlığı yüksekse, reliability-weighted path ekle
            if wr > 0.3:
                try:
                    # Reliability'e göre path bulmak için edge weight'i -log(reliability) yap
                    G_weighted = self.graph.copy()
                    for u, v in G_weighted.edges():
                        rel = G_weighted.edges[u, v].get("reliability", 0.99)
                        G_weighted.edges[u, v]["rel_weight"] = -math.log(max(rel, 0.01))
                    
                    rel_path = nx.shortest_path(
                        G_weighted, self.source, self.target,
                        weight="rel_weight"
                    )
                    if self._is_valid_path(rel_path):
                        path_tuple = tuple(rel_path)
                        if path_tuple not in unique_paths:
                            population.append(rel_path)
                            unique_paths.add(path_tuple)
                            logger.debug("Added reliability-weighted path to population")
                except (nx.NetworkXNoPath, KeyError):
                    pass
        
        # 3. Rastgele path'ler üret (ağırlıklara göre bias ile)
        attempts = 0
        
        while len(population) < pop_size and attempts < max_attempts:
            attempts += 1
            path = self._generate_random_path()
            
            if path is not None and self._is_valid_path(path):
                path_tuple = tuple(path)
                # Duplicate kontrolü
                if path_tuple not in unique_paths:
                    population.append(path)
                    unique_paths.add(path_tuple)
                    logger.debug("Added random path %s to population (attempt %s)", 
                               path[:5] if len(path) > 5 else path, attempts)
        
        if len(population) < pop_size:
            logger.warning(
                "Could only generate %s valid paths (requested %s) after %s attempts",
                len(population), pop_size, attempts
            )
            # Eğer çok az path bulunduysa, mevcut path'leri çoğaltarak popülasyonu doldur
            if len(population) > 0:
                logger.info("Duplicating and mutating existing paths to fill population")
                fill_attempts = 0
                max_fill_attempts = pop_size * 20
                while len(population) < pop_size and fill_attempts < max_fill_attempts:
                    fill_attempts += 1
                    # Mevcut path'lerden birini seç ve mutate et
                    base_path = random.choice(population)
                    mutated = self._mutate(base_path.copy())
                    if self._is_valid_path(mutated):
                        path_tuple = tuple(mutated)
                        if path_tuple not in unique_paths:
                            population.append(mutated)
                            unique_paths.add(path_tuple)
                        elif len(population) < 5:
                            # Çok küçük popülasyonlar için duplicate'leri de kabul et
                            population.append(mutated)
        
        logger.info("Initialized population with %s valid paths", len(population))
        return population

    def _generate_random_path(self) -> Optional[List[int]]:
        """
        Rastgele bir path üret (DFS veya random walk kullanarak).
        Bandwidth kontrolü yaparak sadece geçerli edge'leri seçer.
        
        Returns:
            Geçerli path veya None
        """
        # Random walk stratejisi - bandwidth filtresi ile
        path = [self.source]
        visited = {self.source}
        max_length = self.graph.number_of_nodes()  # Sonsuz döngüyü önle
        
        current = self.source
        for _ in range(max_length):
            if current == self.target:
                return path
            
            # Rastgele komşu seç - sadece yeterli bandwidth'e sahip edge'ler
            neighbors = list(self.graph.neighbors(current))
            # Bandwidth filtresi: sadece yeterli bandwidth'e sahip edge'leri dahil et
            valid_neighbors = []
            for neighbor in neighbors:
                if neighbor not in visited:
                    if self.graph.has_edge(current, neighbor):
                        edge_bandwidth = self.graph.edges[current, neighbor].get("bandwidth", 0.0)
                        if edge_bandwidth >= self.required_bandwidth:
                            valid_neighbors.append(neighbor)
            
            # Eğer hiçbir geçerli komşu yoksa, bandwidth filtresini kaldır (fallback)
            if not valid_neighbors:
                valid_neighbors = [n for n in neighbors if n not in visited]
            
            if not valid_neighbors:
                # Tüm komşular ziyaret edilmiş veya geçersiz, backtrack yap
                if len(path) > 1:
                    path.pop()
                    visited.remove(current)
                    current = path[-1]
                    continue
                else:
                    return None  # Yol bulunamadı
            
            # Ağırlıklara göre komşu seçimi (bias)
            wd, wr, wc = self.weights
            if len(valid_neighbors) > 1:
                # Her komşu için ağırlıklı skor hesapla
                neighbor_scores = []
                for neighbor in valid_neighbors:
                    if self.graph.has_edge(current, neighbor):
                        edge_data = self.graph.edges[current, neighbor]
                        delay = edge_data.get("delay", 15.0)
                        bandwidth = edge_data.get("bandwidth", 100.0)
                        reliability = edge_data.get("reliability", 0.99)
                        
                        # Resource cost: 1 / bandwidth (Gbps)
                        bandwidth_gbps = bandwidth / 1000.0
                        resource_cost = 1.0 / bandwidth_gbps if bandwidth_gbps > 0 else float("inf")
                        
                        # Reliability cost: -log(reliability)
                        rel_cost = -math.log(reliability) if reliability > 0 else float("inf")
                        
                        # Ağırlıklı maliyet (düşük = iyi)
                        weighted_cost = wd * delay + wr * rel_cost + wc * resource_cost
                        
                        # Score: 1 / cost (yüksek = iyi)
                        score = 1.0 / weighted_cost if weighted_cost > 0 else 0.0
                        neighbor_scores.append((neighbor, score))
                
                # Weighted random selection (scores'a göre)
                total_score = sum(score for _, score in neighbor_scores)
                if total_score > 0:
                    r = random.random() * total_score
                    cumulative = 0.0
                    for neighbor, score in neighbor_scores:
                        cumulative += score
                        if r <= cumulative:
                            next_node = neighbor
                            break
                    else:
                        next_node = neighbor_scores[-1][0]  # Fallback
                else:
                    next_node = random.choice(valid_neighbors)
            else:
                next_node = valid_neighbors[0] if valid_neighbors else None
            
            if next_node is None:
                return None
            path.append(next_node)
            visited.add(next_node)
            current = next_node
        
        # Target'a ulaşılamadı
        return None

    def _is_valid_path(self, path: List[int]) -> bool:
        """Path'in geçerli olup olmadığını kontrol et."""
        if not path or path[0] != self.source or path[-1] != self.target:
            return False
        
        if not self.validator.is_simple_path(path):
            return False
        
        if not self.validator.has_capacity(path, self.required_bandwidth):
            return False
        
        return True

    def fitness(self, chromosome: List[int]) -> float:
        """
        Issue #10: Path için ağırlıklı toplam skorunu hesaplayan fitness fonksiyonu.
        
        Fitness = weighted_sum(delay, reliability_cost, resource_cost)
        Düşük skor = daha iyi path (minimize ediyoruz)
        
        Args:
            chromosome: Path (düğüm listesi)
            
        Returns:
            Fitness skoru (düşük = iyi)
        """
        if not self._is_valid_path(chromosome):
            return float("inf")  # Geçersiz path'ler için sonsuz maliyet
        
        # Metrikleri hesapla
        delay = total_delay(graph=self.graph, path=chromosome)
        rel_cost = reliability_cost(graph=self.graph, path=chromosome)
        res_cost = bandwidth_cost(graph=self.graph, path=chromosome)
        
        # Ağırlıklı toplam
        fitness_score = weighted_sum(delay, rel_cost, res_cost, self.weights)
        
        logger.debug(
            "Fitness for path %s: delay=%.2f, rel=%.4f, res=%.4f, total=%.4f",
            chromosome[:5] if len(chromosome) > 5 else chromosome,
            delay, rel_cost, res_cost, fitness_score
        )
        
        return fitness_score

    def run(self, generations: int = 100) -> Tuple[List[int], float]:
        """
        
        """
        logger.info("Running GA for %s generations", generations)
        
        # Popülasyonu başlat
        population = self.initialize_population()
        
        if not population:
            logger.error("Could not initialize population!")
            return [], float("inf")
        
        # Fitness'leri hesapla
        fitnesses = [self.fitness(chrom) for chrom in population]
        best_idx = min(range(len(population)), key=lambda i: fitnesses[i])
        best_path = population[best_idx]
        best_fitness = fitnesses[best_idx]
        
        logger.info("Initial best fitness: %.4f (path length: %s, population size: %s)", 
                   best_fitness, len(best_path), len(population))
        
        # Küçük popülasyonlar için mutation rate'i artır
        adaptive_mutation_rate = self.mutation_rate
        if len(population) < 10:
            adaptive_mutation_rate = min(0.3, self.mutation_rate * 3)  # 3x artır, max 0.3
            logger.info("Small population detected (%s paths), increasing mutation rate to %.3f", 
                       len(population), adaptive_mutation_rate)
        
        # Ana döngü
        for gen in range(generations):
            # Yeni popülasyon oluştur
            new_population = []
            new_population_paths = set()  # Diversity preservation için
            
            # Top-k elitizm: En iyi k path'i koru (diversity için)
            elite_size = min(5, len(population) // 10)  # Popülasyonun %10'u veya max 5
            elite_size = max(1, elite_size)  # En az 1
            
            # Fitness'e göre sırala ve en iyi k path'i al
            sorted_indices = sorted(range(len(population)), key=lambda i: fitnesses[i])
            for idx in sorted_indices[:elite_size]:
                elite_path = population[idx]
                path_tuple = tuple(elite_path)
                if path_tuple not in new_population_paths:
                    new_population.append(elite_path)
                    new_population_paths.add(path_tuple)
            
            # Popülasyon boyutuna ulaşana kadar yeni bireyler üret
            while len(new_population) < self.population_size:
                # Selection (tournament selection)
                parent1 = self._tournament_selection(population, fitnesses, tournament_size=3)
                parent2 = self._tournament_selection(population, fitnesses, tournament_size=3)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation (adaptive rate kullan)
                if random.random() < adaptive_mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < adaptive_mutation_rate:
                    child2 = self._mutate(child2)
                
                # Geçerli child'ları ekle (diversity kontrolü ile)
                for child in [child1, child2]:
                    if self._is_valid_path(child) and len(new_population) < self.population_size:
                        child_tuple = tuple(child)
                        # Diversity: Benzer path'leri filtrele
                        if child_tuple not in new_population_paths:
                            new_population.append(child)
                            new_population_paths.add(child_tuple)
                        elif len(new_population) < self.population_size * 0.8:
                            # Popülasyon %80'den azsa, duplicate'leri de kabul et
                            new_population.append(child)
            
            # Popülasyonu güncelle
            population = new_population
            fitnesses = [self.fitness(chrom) for chrom in population]
            
            # En iyiyi güncelle
            current_best_idx = min(range(len(population)), key=lambda i: fitnesses[i])
            current_best_fitness = fitnesses[current_best_idx]
            
            if current_best_fitness < best_fitness:
                best_path = population[current_best_idx]
                best_fitness = current_best_fitness
                logger.info(
                    "Generation %s: New best fitness=%.4f (path length=%s, path=%s)",
                    gen + 1, best_fitness, len(best_path), 
                    best_path[:8] if len(best_path) > 8 else best_path
                )
        
        logger.info("GA completed. Best fitness: %.4f, path: %s", best_fitness, best_path)
        return best_path, best_fitness

    def _tournament_selection(
        self, population: List[List[int]], fitnesses: List[float], tournament_size: int = 3
    ) -> List[int]:
        """Tournament selection: Rastgele k birey seç, en iyisini döndür."""
        tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
        winner_idx = tournament_indices[min(range(len(tournament_fitnesses)), key=lambda i: tournament_fitnesses[i])]
        return population[winner_idx]

    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """
        
        """
        if len(parent1) <= 2 or len(parent2) <= 2:
            return parent1.copy(), parent2.copy()
        
        # Crossover point seç
        start = random.randint(1, len(parent1) - 2)
        end = random.randint(start + 1, len(parent1) - 1)
        
        # Child1: Parent1'den segment + Parent2'den kalan
        segment = parent1[start:end]
        child1 = [self.source] + segment + [self.target]
        
        # Parent2'den segment'te olmayan düğümleri ekle
        for node in parent2[1:-1]:  # Source ve target hariç
            if node not in segment and node not in child1:
                # Uygun pozisyona ekle
                insert_pos = random.randint(1, len(child1) - 1)
                child1.insert(insert_pos, node)
        
        # Child2: Parent2'den segment + Parent1'den kalan
        segment2 = parent2[start:min(end, len(parent2))] if end < len(parent2) else parent2[start:]
        child2 = [self.source] + segment2 + [self.target]
        
        for node in parent1[1:-1]:
            if node not in segment2 and node not in child2:
                insert_pos = random.randint(1, len(child2) - 1)
                child2.insert(insert_pos, node)
        
        # Geçerliliği düzelt (path repair)
        child1 = self._repair_path(child1)
        child2 = self._repair_path(child2)
        
        return child1, child2

    def _mutate(self, chromosome: List[int]) -> List[int]:
        """
        
        
        Args:
            chromosome: Mutasyona uğrayacak path
            rate: Mutasyon olasılığı (burada zaten çağrılmadan önce kontrol ediliyor)
            
        Returns:
            Mutasyona uğramış path
        """
        if len(chromosome) <= 2:
            # Çok kısa path, düğüm eklemeyi dene
            if len(chromosome) == 2:
                # [source, target] -> [source, intermediate, target]
                source, target = chromosome[0], chromosome[1]
                # Source'un komşularından birini seç (target'a gidebilen)
                source_neighbors = list(self.graph.neighbors(source))
                valid_intermediates = [
                    n for n in source_neighbors
                    if n != target and self.graph.has_edge(n, target)
                    and self.graph.edges[source, n].get("bandwidth", 0.0) >= self.required_bandwidth
                    and self.graph.edges[n, target].get("bandwidth", 0.0) >= self.required_bandwidth
                ]
                if valid_intermediates:
                    intermediate = random.choice(valid_intermediates)
                    return [source, intermediate, target]
            return chromosome.copy()
        
        mutated = chromosome.copy()
        
        # Kısa path'ler için (3-4 düğüm): Düğüm ekle
        if len(mutated) <= 4 and random.random() < 0.5:
            # Rastgele bir pozisyona düğüm ekle
            insert_pos = random.randint(1, len(mutated) - 1)
            prev_node = mutated[insert_pos - 1]
            next_node = mutated[insert_pos]
            
            # Prev_node'un komşularından birini seç (next_node'a gidebilen)
            prev_neighbors = list(self.graph.neighbors(prev_node))
            valid_insertions = [
                n for n in prev_neighbors
                if n != prev_node and n != next_node
                and self.graph.has_edge(n, next_node)
                and n not in mutated  # Döngü önleme
                and self.graph.edges[prev_node, n].get("bandwidth", 0.0) >= self.required_bandwidth
                and self.graph.edges[n, next_node].get("bandwidth", 0.0) >= self.required_bandwidth
            ]
            
            if valid_insertions:
                new_node = random.choice(valid_insertions)
                mutated.insert(insert_pos, new_node)
                return self._repair_path(mutated)
        
        # Normal mutation: Düğüm değiştir veya kaldır
        pos = random.randint(1, len(mutated) - 2)
        old_node = mutated[pos]
        
        # Önceki ve sonraki düğümlerin komşularını bul
        prev_node = mutated[pos - 1]
        next_node = mutated[pos + 1]
        
        # Önceki düğümün komşularından birini seç (next_node'a gidebilen)
        prev_neighbors = list(self.graph.neighbors(prev_node))
        valid_replacements = [
            n for n in prev_neighbors
            if n != old_node and n not in mutated  # Döngü önleme
            and self.graph.has_edge(n, next_node)
            and self.graph.edges[prev_node, n].get("bandwidth", 0.0) >= self.required_bandwidth
            and self.graph.edges[n, next_node].get("bandwidth", 0.0) >= self.required_bandwidth
        ]
        
        if valid_replacements:
            mutated[pos] = random.choice(valid_replacements)
        else:
            # Geçerli değişim yok, düğümü kaldır (eğer edge varsa)
            if self.graph.has_edge(prev_node, next_node):
                mutated.pop(pos)
        
        # Path repair
        mutated = self._repair_path(mutated)
        
        return mutated

    def _repair_path(self, path: List[int]) -> List[int]:
        """
        Geçersiz path'i düzelt (path repair).
        
        Strateji:
        1. Source ve target'ı koru
        2. Eksik edge'leri shortest path ile doldur
        3. Döngüleri kaldır
        """
        if not path or path[0] != self.source or path[-1] != self.target:
            # Path'i baştan oluştur
            if nx.has_path(self.graph, self.source, self.target):
                return nx.shortest_path(self.graph, self.source, self.target)
            return [self.source, self.target]
        
        repaired = [path[0]]
        
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            
            if self.graph.has_edge(u, v):
                repaired.append(v)
            else:
                # Edge yok, shortest path ile doldur
                if nx.has_path(self.graph, u, v):
                    subpath = nx.shortest_path(self.graph, u, v)
                    repaired.extend(subpath[1:])  # İlk düğümü atla (zaten var)
                else:
                    # Ulaşılamıyor, path'i kır
                    break
        
        # Döngüleri kaldır
        seen = set()
        result = []
        for node in repaired:
            if node not in seen:
                result.append(node)
                seen.add(node)
            else:
                # Döngü bulundu, kır
                break
        
        # Target'a ulaş
        if result[-1] != self.target:
            if nx.has_path(self.graph, result[-1], self.target):
                subpath = nx.shortest_path(self.graph, result[-1], self.target)
                result.extend(subpath[1:])
        
        return result

