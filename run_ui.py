#!/usr/bin/env python3
"""
BSM307 UI Launcher
Simple script to launch the interactive UI
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
    print("\nGenerating network...")
    
    # Generate network
    generator = RandomNetworkGenerator(num_nodes=250, edge_prob=0.4, seed=42)
    graph = generator.generate()
    graph = generator.attach_attributes(graph)
    
    print(f"✅ Network generated: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print("\n🚀 Launching UI...")
    print("   - Use text boxes to set Source, Target, Bandwidth, Algorithm")
    print("   - Use sliders to adjust weights")
    print("   - Click 'Calculate Path' to find route")
    print("\n")
    
    # Launch UI
    run_app(graph, seed=42)

