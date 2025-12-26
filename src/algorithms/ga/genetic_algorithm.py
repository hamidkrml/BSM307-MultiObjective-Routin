"""
Genetik Algoritma - Çok Amaçlı Rotalama
BSM307 - Güz 2025

Issue #9, #10, #11, #12: Complete GA implementation
"""

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
        max_attempts = pop_size * 10  # Her path için maksimum deneme sayısı
        
        # 1. Shortest path'i ekle (deterministic, iyi başlangıç)
        if nx.has_path(self.graph, self.source, self.target):
            try:
                shortest = nx.shortest_path(self.graph, self.source, self.target)
                if self._is_valid_path(shortest):
                    population.append(shortest)
                    logger.debug("Added shortest path to population: %s", shortest)
            except nx.NetworkXNoPath:
                pass
        
        # 2. Rastgele path'ler üret
        attempts = 0
        while len(population) < pop_size and attempts < max_attempts:
            attempts += 1
            path = self._generate_random_path()
            
            if path is not None and self._is_valid_path(path):
                # Duplicate kontrolü
                if path not in population:
                    population.append(path)
                    logger.debug("Added random path %s to population", path)
        
        if len(population) < pop_size:
            logger.warning(
                "Could only generate %s valid paths (requested %s)",
                len(population), pop_size
            )
        
        logger.info("Initialized population with %s valid paths", len(population))
        return population

    def _generate_random_path(self) -> Optional[List[int]]:
        """
        Rastgele bir path üret (DFS veya random walk kullanarak).
        
        Returns:
            Geçerli path veya None
        """
        # Random walk stratejisi
        path = [self.source]
        visited = {self.source}
        max_length = self.graph.number_of_nodes()  # Sonsuz döngüyü önle
        
        current = self.source
        for _ in range(max_length):
            if current == self.target:
                return path
            
            # Rastgele komşu seç
            neighbors = list(self.graph.neighbors(current))
            unvisited_neighbors = [n for n in neighbors if n not in visited]
            
            if not unvisited_neighbors:
                # Tüm komşular ziyaret edilmiş, backtrack yap
                if len(path) > 1:
                    path.pop()
                    visited.remove(current)
                    current = path[-1]
                    continue
                else:
                    return None  # Yol bulunamadı
            
            next_node = random.choice(unvisited_neighbors)
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
        Issue #12: GA ana döngüsü (selection, crossover, mutation, replacement).
        
        Args:
            generations: Generasyon sayısı
            
        Returns:
            (best_path, best_fitness) tuple
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
        
        logger.info("Initial best fitness: %.4f (path length: %s)", best_fitness, len(best_path))
        
        # Ana döngü
        for gen in range(generations):
            # Yeni popülasyon oluştur
            new_population = []
            
            # Elitizm: En iyi bireyi koru
            new_population.append(best_path)
            
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
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2)
                
                # Geçerli child'ları ekle
                if self._is_valid_path(child1) and len(new_population) < self.population_size:
                    new_population.append(child1)
                if self._is_valid_path(child2) and len(new_population) < self.population_size:
                    new_population.append(child2)
            
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
                    "Generation %s: New best fitness=%.4f (path length=%s)",
                    gen + 1, best_fitness, len(best_path)
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
        Issue #11: İki parent path'ten yeni child path'ler üreten crossover.
        
        Strateji: Order crossover (OX) benzeri
        1. Parent1'den bir segment al
        2. Parent2'den kalan düğümleri sırayla ekle
        3. Geçerliliği kontrol et ve düzelt
        
        Args:
            parent1: İlk parent path
            parent2: İkinci parent path
            
        Returns:
            (child1, child2) tuple
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
        Issue #11: Path'i rastgele değiştiren mutasyon operatörü.
        
        Strateji:
        1. Rastgele bir düğüm seç
        2. O düğümü farklı bir geçerli düğümle değiştir
        3. Path geçerliliğini koru
        
        Args:
            chromosome: Mutasyona uğrayacak path
            rate: Mutasyon olasılığı (burada zaten çağrılmadan önce kontrol ediliyor)
            
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
        prev_neighbors = list(self.graph.neighbors(prev_node))
        valid_replacements = [
            n for n in prev_neighbors
            if n != old_node and self.graph.has_edge(n, next_node)
        ]
        
        if valid_replacements:
            mutated[pos] = random.choice(valid_replacements)
        else:
            # Geçerli değişim yok, path'i kısalt veya uzat
            # Basit strateji: Düğümü kaldır (eğer edge varsa)
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
