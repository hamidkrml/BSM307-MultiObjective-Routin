#!/usr/bin/env python3
"""
BSM307 UI Launcher
Simple script to launch the interactive UI
Docker uyumlu: MPLBACKEND environment variable ile backend seçimi
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import run_app
from src.network.generator import RandomNetworkGenerator

if __name__ == "__main__":
    print("=" * 70)
    print("BSM307 Multi-Objective Routing - Interactive UI")
    print("=" * 70)
    
    # Environment variables (Docker uyumluluğu)
    seed = int(os.environ.get("EXPERIMENT_SEED", "42"))
    num_nodes = int(os.environ.get("NUM_NODES", "250"))
    edge_prob = float(os.environ.get("EDGE_PROB", "0.4"))
    backend = os.environ.get("MPLBACKEND", "TkAgg")
    
    print(f"\n📋 Configuration:")
    print(f"   Seed: {seed}")
    print(f"   Nodes: {num_nodes}")
    print(f"   Edge Probability: {edge_prob}")
    print(f"   Matplotlib Backend: {backend}")
    
    print("\n🔄 Generating network...")
    
    # Generate network
    generator = RandomNetworkGenerator(num_nodes=num_nodes, edge_prob=edge_prob, seed=seed)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    print(f"✅ Network generated: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Docker'da headless mode kontrolü
    if backend == "Agg":
        print("\n⚠️  Headless mode detected (MPLBACKEND=Agg)")
        print("   UI requires GUI backend (TkAgg). Switching to demo mode...")
        print("   For interactive UI, use: MPLBACKEND=TkAgg")
        print("\n   Running demo.py instead...\n")
        from demo import main
        sys.exit(main())
    
    print("\n🚀 Launching Interactive UI...")
    print("   - Use text boxes to set Source, Target, Bandwidth, Algorithm")
    print("   - Use sliders to adjust weights")
    print("   - Click 'Calculate Path' to find route")
    print("\n")
    
    # Launch UI
    run_app(graph, seed=seed)

