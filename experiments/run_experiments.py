#!/usr/bin/env python3
"""
Main Experiment Script
BSM307 - Güz 2025

PDF gereksinimleri:
- 20 farklı (S, D, B) senaryosu
- Her senaryo için 5 tekrar
- GA ve ACO algoritmaları
- Sonuç toplama ve analiz
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import networkx as nx

from src.network.generator import RandomNetworkGenerator
from experiments.scenario_generator import generate_scenarios_for_experiment
from experiments.experiment_runner import ExperimentRunner, save_results_to_json
from experiments.result_analyzer import ResultAnalyzer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Ana experiment script'i"""
    parser = argparse.ArgumentParser(
        description="BSM307 Multi-Objective Routing Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full experiment (20 scenarios, 5 repetitions)
  python run_experiments.py
  
  # Quick test (2 scenarios, 2 repetitions)
  python run_experiments.py --num-scenarios 2 --repetitions 2
  
  # Custom output directory
  python run_experiments.py --output-dir ./my_results
        """
    )
    
    parser.add_argument(
        '--num-scenarios',
        type=int,
        default=20,
        help='Number of scenarios to generate (default: 20)'
    )
    
    parser.add_argument(
        '--repetitions',
        type=int,
        default=5,
        help='Number of repetitions per scenario (default: 5)'
    )
    
    parser.add_argument(
        '--algorithms',
        nargs='+',
        default=['GA', 'ACO'],
        help='Algorithms to run (default: GA ACO)'
    )
    
    parser.add_argument(
        '--graph-seed',
        type=int,
        default=42,
        help='Seed for graph generation (default: 42)'
    )
    
    parser.add_argument(
        '--scenario-seed',
        type=int,
        default=42,
        help='Seed for scenario generation (default: 42)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiments/results',
        help='Output directory for results (default: experiments/results)'
    )
    
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip result analysis (only run experiments)'
    )
    
    args = parser.parse_args()
    
    # Output directory oluştur
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 80)
    print("BSM307 Multi-Objective Routing - Experiment Runner")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Scenarios: {args.num_scenarios}")
    print(f"  Repetitions: {args.repetitions}")
    print(f"  Algorithms: {', '.join(args.algorithms)}")
    print(f"  Graph Seed: {args.graph_seed}")
    print(f"  Scenario Seed: {args.scenario_seed}")
    print(f"  Output Directory: {output_dir}")
    print()
    
    try:
        # 1. Graph oluştur
        print("=" * 80)
        print("Step 1: Generating Network Graph")
        print("=" * 80)
        logger.info("Generating network graph: nodes=250, p=0.4, seed=%s", args.graph_seed)
        
        generator = RandomNetworkGenerator(
            num_nodes=250,
            edge_prob=0.4,
            seed=args.graph_seed
        )
        graph = generator.generate()
        graph = generator.attach_attributes(graph)
        
        print(f"✅ Graph generated:")
        print(f"   Nodes: {graph.number_of_nodes()}")
        print(f"   Edges: {graph.number_of_edges()}")
        print(f"   Connected: {nx.is_connected(graph)}")
        print()
        
        # 2. Senaryoları üret
        print("=" * 80)
        print("Step 2: Generating Scenarios")
        print("=" * 80)
        logger.info("Generating %s scenarios with seed %s", args.num_scenarios, args.scenario_seed)
        
        scenarios = generate_scenarios_for_experiment(
            graph=graph,
            num_scenarios=args.num_scenarios,
            seed=args.scenario_seed
        )
        
        print(f"✅ Generated {len(scenarios)} scenarios")
        print(f"   First scenario: S={scenarios[0][0]}, D={scenarios[0][1]}, B={scenarios[0][2]:.1f} Mbps")
        print()
        
        # 3. Experiment çalıştır
        print("=" * 80)
        print("Step 3: Running Experiments")
        print("=" * 80)
        logger.info(
            "Running experiments: %s scenarios × %s repetitions × %s algorithms = %s total runs",
            len(scenarios), args.repetitions, len(args.algorithms),
            len(scenarios) * args.repetitions * len(args.algorithms)
        )
        
        runner = ExperimentRunner(
            graph=graph,
            weights=(0.4, 0.3, 0.3),
            num_repetitions=args.repetitions
        )
        
        results = runner.run_all_scenarios(
            scenarios=scenarios,
            algorithms=args.algorithms
        )
        
        print(f"\n✅ Experiments completed: {len(results)} total results")
        success_count = sum(1 for r in results if r.success)
        print(f"   Success: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        print()
        
        # 4. Sonuçları kaydet
        print("=" * 80)
        print("Step 4: Saving Results")
        print("=" * 80)
        
        results_file = output_dir / f"results_{timestamp}.json"
        save_results_to_json(results, str(results_file))
        print(f"✅ Results saved to: {results_file}")
        print()
        
        # 5. Analiz (opsiyonel)
        if not args.skip_analysis:
            print("=" * 80)
            print("Step 5: Analyzing Results")
            print("=" * 80)
            
            analyzer = ResultAnalyzer(results)
            analyzer.print_summary_report()
            
            # CSV export
            csv_file = output_dir / f"summary_{timestamp}.csv"
            analyzer.export_to_csv(str(csv_file))
            print(f"\n✅ Summary exported to: {csv_file}")
            print()
        
        # Özet
        print("=" * 80)
        print("Experiment Completed Successfully!")
        print("=" * 80)
        print(f"\nResults:")
        print(f"  JSON: {results_file}")
        if not args.skip_analysis:
            print(f"  CSV:  {csv_file}")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
        return 1
        
    except Exception as e:
        logger.exception("Experiment failed with error: %s", e)
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

