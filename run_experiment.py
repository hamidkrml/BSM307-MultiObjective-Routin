#!/usr/bin/env python3
"""
Hızlı Experiment Çalıştırıcı
BSM307 - Güz 2025

Bu script experiment'leri kolayca çalıştırmanızı sağlar.
"""

import sys
import os
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# experiments modülünü import et
sys.path.insert(0, str(project_root / "experiments"))

if __name__ == "__main__":
    print("=" * 80)
    print("BSM307 - Hızlı Experiment Çalıştırıcı")
    print("=" * 80)
    print()
    print("Bu script experiment'leri çalıştırır.")
    print()
    print("Kullanım seçenekleri:")
    print()
    print("1. Hızlı test (2 senaryo, 1 tekrar):")
    print("   python run_experiment.py --quick")
    print()
    print("2. Tam experiment (20 senaryo, 5 tekrar):")
    print("   python run_experiment.py --full")
    print()
    print("3. Özelleştirilmiş:")
    print("   python run_experiment.py --scenarios 5 --repetitions 2")
    print()
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) > 1:
        if "--quick" in sys.argv:
            print("🚀 Hızlı test başlatılıyor...")
            os.system("python experiments/run_experiments.py --num-scenarios 2 --repetitions 1")
        elif "--full" in sys.argv:
            print("🚀 Tam experiment başlatılıyor...")
            os.system("python experiments/run_experiments.py")
        else:
            # Diğer argümanları direkt experiment runner'a ilet
            args = " ".join(sys.argv[1:])
            cmd = f"python experiments/run_experiments.py {args}"
            print(f"🚀 Experiment başlatılıyor: {cmd}")
            os.system(cmd)
    else:
        # Varsayılan: hızlı test
        print("Varsayılan: Hızlı test başlatılıyor...")
        print("(Tam experiment için: python run_experiment.py --full)")
        print()
        os.system("python experiments/run_experiments.py --num-scenarios 2 --repetitions 1")

