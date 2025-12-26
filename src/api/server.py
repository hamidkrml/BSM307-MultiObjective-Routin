"""
FastAPI Web Server - BSM307 Multi-Objective Routing
Docker uyumlu web API backend
"""

import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import networkx as nx

from ..network.generator import RandomNetworkGenerator
from ..algorithms.ga.genetic_algorithm import GeneticAlgorithm
from ..algorithms.aco.ant_colony import AntColonyOptimizer
from ..metrics.delay import total_delay
from ..metrics.reliability import reliability_cost
from ..metrics.resource_cost import bandwidth_cost, weighted_sum
from ..routing.path_validator import PathValidator
from ..utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="BSM307 Multi-Objective Routing API",
    description="Web API for multi-objective routing with GA, ACO algorithms",
    version="1.0.0"
)

# CORS middleware (web frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler kullan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph instance (cache)
_graph: Optional[nx.Graph] = None
_graph_seed: Optional[int] = None


def get_or_create_graph(num_nodes: int = 250, edge_prob: float = 0.4, seed: int = 42) -> nx.Graph:
    """Graph'i cache'den al veya yeni oluştur"""
    global _graph, _graph_seed
    
    if _graph is None or _graph_seed != seed:
        logger.info("Generating new network: nodes=%s, p=%s, seed=%s", num_nodes, edge_prob, seed)
        generator = RandomNetworkGenerator(num_nodes=num_nodes, edge_prob=edge_prob, seed=seed)
        _graph = generator.generate()
        _graph = generator.attach_attributes(_graph)
        _graph_seed = seed
        logger.info("Network generated: %s nodes, %s edges", _graph.number_of_nodes(), _graph.number_of_edges())
    
    return _graph


@app.get("/", response_class=HTMLResponse)
async def root():
    """Ana sayfa - HTML frontend"""
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BSM307 Çok Amaçlı Yönlendirme</title>
    <link rel="icon" href="data:,">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .control-group {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
        }
        small {
            margin-top: 3px;
            display: block;
        }
        input, select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: white;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }
        input:hover, select:hover {
            border-color: #667eea;
        }
        .slider-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="range"] {
            flex: 1;
        }
        .slider-value {
            min-width: 50px;
            text-align: right;
            font-weight: 600;
            color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            grid-column: 1 / -1;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            position: relative;
            overflow: hidden;
        }
        button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        button:hover::before {
            width: 300px;
            height: 300px;
        }
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        button:active {
            transform: translateY(-1px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .result-item {
            margin-bottom: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            animation: slideIn 0.4s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .result-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        .result-item h3 {
            color: #333;
            margin-bottom: 12px;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .result-item p {
            color: #555;
            margin: 8px 0;
            line-height: 1.6;
        }
        .result-item strong {
            color: #667eea;
            font-weight: 600;
        }
        .error {
            background: linear-gradient(135deg, #fee 0%, #fdd 100%);
            border-left-color: #f44336;
            color: #c00;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        .loading::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        .path-display {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            padding: 12px 15px;
            border-radius: 8px;
            word-break: break-all;
            border: 1px solid #ddd;
            font-size: 13px;
            line-height: 1.6;
        }
        .metric-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }
        .metric-delay { background: #e3f2fd; color: #1976d2; }
        .metric-reliability { background: #f3e5f5; color: #7b1fa2; }
        .metric-resource { background: #fff3e0; color: #e65100; }
        .metric-weighted { background: #e8f5e9; color: #2e7d32; }
        .graph-container {
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            animation: fadeIn 0.6s ease-in;
        }
        .graph-container h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #graph-canvas {
            width: 100%;
            height: 700px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.05);
        }
        .legend {
            display: flex;
            gap: 20px;
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid #333;
        }
    </style>
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🚀 BSM307 Çok Amaçlı Yönlendirme</h1>
        <p class="subtitle">GA ve ACO algoritmaları ile çok amaçlı rota optimizasyonu</p>
        
        <div class="controls">
            <div class="control-group">
                <label>Kaynak Düğüm: <span id="source-range" style="color: #666; font-size: 0.9em;">(0-249)</span></label>
                <input type="number" id="source" value="0" min="0" step="1">
            </div>
            <div class="control-group">
                <label>Hedef Düğüm: <span id="target-range" style="color: #666; font-size: 0.9em;">(0-249)</span></label>
                <input type="number" id="target" value="100" min="0" step="1">
            </div>
            <div class="control-group">
                <label>Bant Genişliği (Mbps):</label>
                <input type="number" id="bandwidth" value="500" min="100" max="1000" step="50">
                <small style="color: #666;">Aralık: 100-1000 Mbps (PDF: 100-1000)</small>
            </div>
            <div class="control-group">
                <label>Algoritma:</label>
                <select id="algorithm">
                    <option value="GA">Genetik Algoritma (GA)</option>
                    <option value="ACO">Karınca Kolonisi Optimizasyonu (ACO)</option>
                </select>
            </div>
            <div class="slider-group">
                <label>Gecikme Ağırlığı: <span class="slider-value" id="delay-value">0.4</span></label>
                <div class="slider-container">
                    <input type="range" id="delay-weight" min="0" max="1" step="0.1" value="0.4">
                </div>
            </div>
            <div class="slider-group">
                <label>Güvenilirlik Ağırlığı: <span class="slider-value" id="reliability-value">0.3</span></label>
                <div class="slider-container">
                    <input type="range" id="reliability-weight" min="0" max="1" step="0.1" value="0.3">
                </div>
            </div>
            <div class="slider-group">
                <label>Kaynak Ağırlığı: <span class="slider-value" id="resource-value">0.3</span></label>
                <div class="slider-container">
                    <input type="range" id="resource-weight" min="0" max="1" step="0.1" value="0.3">
                </div>
            </div>
            <button id="calculate-btn">Yol Hesapla (Seçili Algoritma)</button>
            <button id="compare-btn" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);">🔀 Her İki Algoritmayı Karşılaştır</button>
            <button id="experiment-btn" onclick="window.location.href='/experiment'" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">🧪 Experiment UI'ye Git</button>
        </div>
        
        <div id="results" class="results">
            <div id="results-content"></div>
            <div id="graph-container" class="graph-container" style="display: none;">
                <h3>📊 Ağ Görselleştirmesi</h3>
                <div id="graph-canvas"></div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: green;"></div>
                        <span>Kaynak Düğüm</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: blue;"></div>
                        <span>Hedef Düğüm</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: red;"></div>
                        <span>Yol Düğümleri</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ccc;"></div>
                        <span>Diğer Düğümler</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Graph bilgilerini yükle ve node limitlerini ayarla
        async function loadGraphInfo() {
            try {
                const response = await fetch('/api/graph/info');
                const data = await response.json();
                const maxNode = data.max_node_id || 249;
                const totalNodes = data.nodes || 250;
                
                // Label'ları güncelle
                document.getElementById('source-range').textContent = `(0-${maxNode}, Toplam: ${totalNodes})`;
                document.getElementById('target-range').textContent = `(0-${maxNode}, Toplam: ${totalNodes})`;
                
                // Placeholder'ları güncelle
                document.getElementById('source').placeholder = `0-${maxNode}`;
                document.getElementById('target').placeholder = `0-${maxNode}`;
                
                // Max değerlerini setAttribute ile güncelle (pattern hatası için)
                document.getElementById('source').setAttribute('max', maxNode);
                document.getElementById('target').setAttribute('max', maxNode);
                
                // Default target'ı güncelle (eğer çok büyükse)
                if (parseInt(document.getElementById('target').value) > maxNode) {
                    document.getElementById('target').value = Math.min(100, maxNode);
                }
            } catch (error) {
                console.error('Failed to load graph info:', error);
            }
        }
        
        // Sayfa yüklendiğinde graph bilgilerini al
        loadGraphInfo();
        
        // Slider value updates
        document.getElementById('delay-weight').addEventListener('input', (e) => {
            document.getElementById('delay-value').textContent = e.target.value;
        });
        document.getElementById('reliability-weight').addEventListener('input', (e) => {
            document.getElementById('reliability-value').textContent = e.target.value;
        });
        document.getElementById('resource-weight').addEventListener('input', (e) => {
            document.getElementById('resource-value').textContent = e.target.value;
        });
        
        // Fonksiyonları tanımla
        async function calculatePath() {
            const btn = document.getElementById('calculate-btn');
            const results = document.getElementById('results');
            const content = document.getElementById('results-content');
            
            btn.disabled = true;
            results.classList.add('show');
            content.innerHTML = '<div class="loading">⏳ Yol hesaplanıyor...</div>';
            
            // Input değerlerini güvenli şekilde parse et
            const sourceInput = document.getElementById('source').value;
            const targetInput = document.getElementById('target').value;
            
            const source = parseInt(sourceInput) || 0;
            const target = parseInt(targetInput) || 100;
            
            // Max node kontrolü (güvenli şekilde)
            let maxNode = 249;
            try {
                const maxAttr = document.getElementById('source').getAttribute('max');
                if (maxAttr) maxNode = parseInt(maxAttr) || 249;
            } catch (e) {
                // Fallback
            }
            
            if (isNaN(source) || source < 0 || source > maxNode) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>Kaynak düğüm 0 ile ${maxNode} arasında olmalıdır (girilen: ${sourceInput})</p></div>`;
                btn.disabled = false;
                return;
            }
            if (isNaN(target) || target < 0 || target > maxNode) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>Hedef düğüm 0 ile ${maxNode} arasında olmalıdır (girilen: ${targetInput})</p></div>`;
                btn.disabled = false;
                return;
            }
            
            const params = {
                source: source,
                target: target,
                bandwidth: parseFloat(document.getElementById('bandwidth').value) || 500,
                algorithm: document.getElementById('algorithm').value,
                weights: {
                    delay: parseFloat(document.getElementById('delay-weight').value) || 0.4,
                    reliability: parseFloat(document.getElementById('reliability-weight').value) || 0.3,
                    resource: parseFloat(document.getElementById('resource-weight').value) || 0.3
                }
            };
            
            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    const errorDetail = data.detail || data.error || 'Bilinmeyen hata';
                    content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>${errorDetail}</p></div>`;
                } else if (data.error) {
                    content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>${data.error}</p></div>`;
                } else {
                    const pathStr = data.path.join(' → ');
                    content.innerHTML = `
                        <div class="result-item">
                            <h3>✅ Yol Bulundu (${data.algorithm})</h3>
                            <p><strong>Yol:</strong> <span class="path-display">${pathStr}</span></p>
                            <p><strong>Uzunluk:</strong> ${data.path.length - 1} atlama</p>
                        </div>
                        <div class="result-item">
                            <h3>📊 Metrikler</h3>
                            <p><strong>Gecikme:</strong> ${data.metrics.delay.toFixed(2)} ms <span class="metric-badge metric-delay">DÜŞÜK DAHA İYİ</span></p>
                            <p><strong>Güvenilirlik Maliyeti:</strong> ${data.metrics.reliability_cost.toFixed(4)} <span class="metric-badge metric-reliability">DÜŞÜK DAHA İYİ</span></p>
                            <p><strong>Kaynak Maliyeti:</strong> ${data.metrics.resource_cost.toFixed(4)} <span class="metric-badge metric-resource">DÜŞÜK DAHA İYİ</span></p>
                            <p><strong>Ağırlıklı Maliyet:</strong> ${data.metrics.weighted_cost.toFixed(4)} <span class="metric-badge metric-weighted">TOPLAM MALİYET</span></p>
                        </div>
                    `;
                    
                    // Graf görselleştirmesi (PDF gereksinimi)
                    if (data.graph) {
                        visualizeGraph(data.graph, data.path, params.source, params.target);
                    }
                }
            } catch (error) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
            }
        }
        
        // İki algoritmayı karşılaştır (PDF gereksinimi)
        async function compareAlgorithms() {
            const btn = document.getElementById('compare-btn');
            const calcBtn = document.getElementById('calculate-btn');
            const results = document.getElementById('results');
            const content = document.getElementById('results-content');
            const graphContainer = document.getElementById('graph-container');
            
            btn.disabled = true;
            calcBtn.disabled = true;
            results.classList.add('show');
            content.innerHTML = '<div class="loading">⏳ GA ve ACO algoritmaları karşılaştırılıyor...</div>';
            graphContainer.style.display = 'none';
            
            // Input değerlerini güvenli şekilde parse et
            const sourceInput = document.getElementById('source').value;
            const targetInput = document.getElementById('target').value;
            
            const source = parseInt(sourceInput) || 0;
            const target = parseInt(targetInput) || 100;
            
            // Max node kontrolü (güvenli şekilde)
            let maxNode = 249;
            try {
                const maxAttr = document.getElementById('source').getAttribute('max');
                if (maxAttr) maxNode = parseInt(maxAttr) || 249;
            } catch (e) {
                // Fallback
            }
            
            if (isNaN(source) || source < 0 || source > maxNode) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>Kaynak düğüm 0 ile ${maxNode} arasında olmalıdır (girilen: ${sourceInput})</p></div>`;
                btn.disabled = false;
                calcBtn.disabled = false;
                return;
            }
            if (isNaN(target) || target < 0 || target > maxNode) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>Hedef düğüm 0 ile ${maxNode} arasında olmalıdır (girilen: ${targetInput})</p></div>`;
                btn.disabled = false;
                calcBtn.disabled = false;
                return;
            }
            
            const params = {
                source: source,
                target: target,
                bandwidth: parseFloat(document.getElementById('bandwidth').value) || 500,
                weights: {
                    delay: parseFloat(document.getElementById('delay-weight').value) || 0.4,
                    reliability: parseFloat(document.getElementById('reliability-weight').value) || 0.3,
                    resource: parseFloat(document.getElementById('resource-weight').value) || 0.3
                }
            };
            
            try {
                // GA sonucu
                const gaParams = { ...params, algorithm: 'GA' };
                const gaResponse = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(gaParams)
                });
                const gaData = await gaResponse.json();
                
                // ACO sonucu
                const acoParams = { ...params, algorithm: 'ACO' };
                const acoResponse = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(acoParams)
                });
                const acoData = await acoResponse.json();
                
                if (!gaResponse.ok || !acoResponse.ok) {
                    content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>Bir veya her iki algoritma başarısız oldu</p></div>`;
                    return;
                }
                
                // Karşılaştırma sonuçları
                const gaPathStr = gaData.path.join(' → ');
                const acoPathStr = acoData.path.join(' → ');
                
                let betterAlgorithm = '';
                if (gaData.metrics.weighted_cost < acoData.metrics.weighted_cost) {
                    betterAlgorithm = 'GA daha iyi';
                } else if (acoData.metrics.weighted_cost < gaData.metrics.weighted_cost) {
                    betterAlgorithm = 'ACO daha iyi';
                } else {
                    betterAlgorithm = 'İkisi de eşit';
                }
                
                content.innerHTML = `
                    <div class="result-item">
                        <h3>🔀 Algoritma Karşılaştırması</h3>
                        <p><strong>${betterAlgorithm}</strong> (düşük maliyet daha iyi)</p>
                    </div>
                    <div class="result-item" style="border-left-color: #4caf50;">
                        <h3>🧬 GA Sonuçları</h3>
                        <p><strong>Yol:</strong> <span class="path-display">${gaPathStr}</span></p>
                        <p><strong>Uzunluk:</strong> ${gaData.path.length - 1} atlama</p>
                        <p><strong>Gecikme:</strong> ${gaData.metrics.delay.toFixed(2)} ms</p>
                        <p><strong>Güvenilirlik Maliyeti:</strong> ${gaData.metrics.reliability_cost.toFixed(4)}</p>
                        <p><strong>Kaynak Maliyeti:</strong> ${gaData.metrics.resource_cost.toFixed(4)}</p>
                        <p><strong>Ağırlıklı Maliyet:</strong> ${gaData.metrics.weighted_cost.toFixed(4)}</p>
                    </div>
                    <div class="result-item" style="border-left-color: #ff9800;">
                        <h3>🐜 ACO Sonuçları</h3>
                        <p><strong>Yol:</strong> <span class="path-display">${acoPathStr}</span></p>
                        <p><strong>Uzunluk:</strong> ${acoData.path.length - 1} atlama</p>
                        <p><strong>Gecikme:</strong> ${acoData.metrics.delay.toFixed(2)} ms</p>
                        <p><strong>Güvenilirlik Maliyeti:</strong> ${acoData.metrics.reliability_cost.toFixed(4)}</p>
                        <p><strong>Kaynak Maliyeti:</strong> ${acoData.metrics.resource_cost.toFixed(4)}</p>
                        <p><strong>Ağırlıklı Maliyet:</strong> ${acoData.metrics.weighted_cost.toFixed(4)}</p>
                    </div>
                `;
                
                // İki grafı yan yana göster (GA path'i göster, daha sonra ACO'yu da ekleyebiliriz)
                if (gaData.graph) {
                    visualizeComparison(gaData.graph, gaData.path, acoData.path, params.source, params.target);
                }
                
            } catch (error) {
                content.innerHTML = `<div class="result-item error"><h3>❌ Hata</h3><p>${error.message}</p></div>`;
            } finally {
                btn.disabled = false;
                calcBtn.disabled = false;
            }
        }
        
        // Graf görselleştirme fonksiyonu (Cytoscape.js - daha performanslı ve canlı)
        function visualizeGraph(graphData, path, source, target) {
            const container = document.getElementById('graph-canvas');
            const graphContainer = document.getElementById('graph-container');
            graphContainer.style.display = 'block';
            
            // Container'ı temizle
            container.innerHTML = '';
            
            // Path node'larını belirle
            const pathSet = new Set(path);
            const pathEdgesSet = new Set();
            for (let i = 0; i < path.length - 1; i++) {
                pathEdgesSet.add(`${path[i]}-${path[i+1]}`);
                pathEdgesSet.add(`${path[i+1]}-${path[i]}`); // Undirected
            }
            
            // Cytoscape elements oluştur (doğru format)
            const elements = [];
            
            // Nodes (data objesinde tip bilgisi tut)
            graphData.nodes.forEach(nodeId => {
                const nodeData = {
                    id: String(nodeId),
                    label: String(nodeId)
                };
                
                // Node tipini belirle (selector'lar için)
                if (nodeId === source) {
                    nodeData.type = 'source';
                } else if (nodeId === target) {
                    nodeData.type = 'target';
                } else if (pathSet.has(nodeId)) {
                    nodeData.type = 'path';
                } else {
                    nodeData.type = 'normal';
                }
                
                elements.push({ data: nodeData });
            });
            
            // Edges: Tüm edge'leri ekle
            graphData.edges.forEach((edge, idx) => {
                const [u, v] = edge;
                const edgeKey = `${u}-${v}`;
                const isPathEdge = pathEdgesSet.has(edgeKey);
                
                elements.push({
                    data: {
                        id: `e${idx}`,
                        source: String(u),
                        target: String(v),
                        isPath: isPathEdge ? 'true' : 'false'
                    }
                });
            });
            
            // Cytoscape instance oluştur
            const cy = cytoscape({
                container: container,
                elements: elements,
                style: [
                    {
                        selector: 'node',
                        style: {
                            'label': 'data(label)',
                            'text-wrap': 'wrap',
                            'text-max-width': 50,
                            'background-color': '#b3d9ff',
                            'border-color': '#0066cc',
                            'border-width': 2,
                            'width': 20,
                            'height': 20,
                            'font-size': '8px',  // Daha küçük font
                            'color': '#333',
                            'text-valign': 'center',
                            'text-halign': 'center'
                        }
                    },
                    {
                        selector: 'node[type="source"]',
                        style: {
                            'background-color': '#66ff66',
                            'border-color': '#00cc00',
                            'width': 40,
                            'height': 40,
                            'font-size': '8px',  // Daha küçük font  // Daha küçük font
                            'font-weight': 'bold',
                            'color': '#fff'
                        }
                    },
                    {
                        selector: 'node[type="target"]',
                        style: {
                            'background-color': '#4da6ff',
                            'border-color': '#0052cc',
                            'width': 40,
                            'height': 40,
                            'font-size': '8px',  // Daha küçük font  // Daha küçük font
                            'font-weight': 'bold',
                            'color': '#fff'
                        }
                    },
                    {
                        selector: 'node[type="path"]',
                        style: {
                            'background-color': '#ff6666',
                            'border-color': '#cc0000',
                            'width': 28,
                            'height': 28,
                            'font-size': '9px',  // Daha küçük font
                            'font-weight': 'bold',
                            'color': '#fff'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 1.5,  // Normal edge'ler daha kalın
                            'line-color': '#d0d0d0',
                            'target-arrow-shape': 'none',
                            'opacity': 0.3,
                            'curve-style': 'bezier'
                        }
                    },
                    {
                        selector: 'edge[isPath="true"]',
                        style: {
                            'width': 8,  // Path edge'leri daha kalın ve belirgin
                            'line-color': '#ff3333',
                            'opacity': 1.0,
                            'z-index': 10,
                            'line-cap': 'round'  // Yuvarlatılmış uçlar
                        }
                    },
                    {
                        selector: 'node:selected',
                        style: {
                            'border-width': 4,
                            'border-color': '#ff00ff'
                        }
                    }
                ],
                layout: {
                    // Pozisyonları sabit tutmak için preset kullan (graphData.positions)
                    name: 'preset',
                    positions: (node) => {
                        const p = graphData.positions[String(node.id())] || [Math.random(), Math.random()];
                        return { x: p[0] * 1200, y: p[1] * 1200 };
                    },
                    fit: false,
                    animate: false
                },
                minZoom: 0.1,
                maxZoom: 4,
                wheelSensitivity: 0.2,
                userPanningEnabled: true,  // Pan özelliğini aktif et
                userZoomingEnabled: true   // Zoom özelliğini aktif et
            });
            
            // Event handlers
            cy.on('tap', 'node', function(evt) {
                const node = evt.target;
                console.log('Node clicked:', node.id());
            });
            
            // Node sürükleme özelliğini aktif et
            cy.on('drag', 'node', function(evt) {
                const node = evt.target;
                // Sürükleme sırasında node'u unlock yap
                node.unlock();
            });
            
            // Store original sizes for hover effects
            const originalSizes = {};
            cy.nodes().forEach(node => {
                const width = node.style('width');
                originalSizes[node.id()] = typeof width === 'number' ? width : 20;
            });
            
            cy.on('mouseover', 'node', function(evt) {
                const node = evt.target;
                const originalSize = originalSizes[node.id()] || 20;
                node.style('width', originalSize * 1.3);
                node.style('height', originalSize * 1.3);
                container.style.cursor = 'pointer';
            });
            
            cy.on('mouseout', 'node', function(evt) {
                const node = evt.target;
                const originalSize = originalSizes[node.id()] || 20;
                node.style('width', originalSize);
                node.style('height', originalSize);
                container.style.cursor = 'default';
            });
            
            // Layout yok; preset ile sabit pozisyon. Sadece ilk çizimde fit yap (padding'li)
            cy.once('render', function() {
                cy.fit(undefined, 80);
            });
        }
        
        // Karşılaştırma görselleştirmesi (Cytoscape.js - sadece path'leri göster, daha temiz)
        function visualizeComparison(graphData, gaPath, acoPath, source, target) {
            const container = document.getElementById('graph-canvas');
            const graphContainer = document.getElementById('graph-container');
            graphContainer.style.display = 'block';
            
            // Container'ı temizle
            container.innerHTML = '';
            
            const gaPathSet = new Set(gaPath);
            const acoPathSet = new Set(acoPath);
            const allPathNodes = new Set([...gaPath, ...acoPath]);
            
            // Path edge'lerini belirle
            const gaEdges = new Set();
            const acoEdges = new Set();
            for (let i = 0; i < gaPath.length - 1; i++) {
                gaEdges.add(`${gaPath[i]}-${gaPath[i+1]}`);
                gaEdges.add(`${gaPath[i+1]}-${gaPath[i]}`);
            }
            for (let i = 0; i < acoPath.length - 1; i++) {
                acoEdges.add(`${acoPath[i]}-${acoPath[i+1]}`);
                acoEdges.add(`${acoPath[i+1]}-${acoPath[i]}`);
            }
            
            const elements = [];
            
            // Sadece path node'larını ekle (daha temiz görünüm)
            allPathNodes.forEach(nodeId => {
                const nodeData = {
                    id: String(nodeId),
                    label: String(nodeId)
                };
                
                // Node tipini belirle
                if (nodeId === source) {
                    nodeData.type = 'source';
                } else if (nodeId === target) {
                    nodeData.type = 'target';
                } else if (gaPathSet.has(nodeId) && acoPathSet.has(nodeId)) {
                    nodeData.type = 'both';
                } else if (gaPathSet.has(nodeId)) {
                    nodeData.type = 'ga';
                } else if (acoPathSet.has(nodeId)) {
                    nodeData.type = 'aco';
                }
                
                elements.push({ data: nodeData });
            });
            
            // Path edge'lerini ekle
            graphData.edges.forEach((edge, idx) => {
                const [u, v] = edge;
                const edgeKey = `${u}-${v}`;
                const isGAEdge = gaEdges.has(edgeKey);
                const isACOEdge = acoEdges.has(edgeKey);
                
                if (isGAEdge || isACOEdge) {
                    const edgeData = {
                        id: `e${idx}`,
                        source: String(u),
                        target: String(v)
                    };
                    
                    if (isGAEdge && isACOEdge) {
                        edgeData.type = 'both';
                    } else if (isGAEdge) {
                        edgeData.type = 'ga';
                    } else {
                        edgeData.type = 'aco';
                    }
                    
                    elements.push({ data: edgeData });
                }
            });
            
            // Cytoscape instance
            const cy = cytoscape({
                container: container,
                elements: elements,
                style: [
                    {
                        selector: 'node',
                        style: {
                            'label': 'data(label)',
                            'text-wrap': 'wrap',
                            'text-max-width': 50,
                            'border-width': 2
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'target-arrow-shape': 'none',
                            'width': 6,  // Daha kalın edge'ler
                            'opacity': 0.9,
                            'curve-style': 'bezier',
                            'line-cap': 'round'
                        }
                    },
                    {
                        selector: 'edge[type="both"]',
                        style: {
                            'line-color': '#cc66ff',
                            'width': 10  // Ortak path daha kalın
                        }
                    },
                    {
                        selector: 'edge[type="ga"]',
                        style: {
                            'line-color': '#66ff66',
                            'width': 7
                        }
                    },
                    {
                        selector: 'edge[type="aco"]',
                        style: {
                            'line-color': '#ff9966',
                            'width': 7
                        }
                    }
                ],
                layout: {
                    // Pozisyonları sabit tutmak için preset kullan (graphData.positions)
                    name: 'preset',
                    positions: (node) => {
                        const p = graphData.positions[String(node.id())] || [Math.random(), Math.random()];
                        return { x: p[0] * 1200, y: p[1] * 1200 };
                    },
                    fit: false,
                    animate: false
                },
                minZoom: 0.05,
                maxZoom: 4,
                wheelSensitivity: 0.2,
                userPanningEnabled: true,  // Pan özelliğini aktif et
                userZoomingEnabled: true   // Zoom özelliğini aktif et
            });
            
            // Event handlers
            cy.on('tap', 'node', function(evt) {
                const node = evt.target;
                console.log('Node clicked:', node.id());
            });
            
            // Node sürükleme özelliğini aktif et
            cy.on('drag', 'node', function(evt) {
                const node = evt.target;
                // Sürükleme sırasında node'u unlock yap
                node.unlock();
            });
            
            // Store original sizes for hover effects
            const originalSizes2 = {};
            cy.nodes().forEach(node => {
                const width = node.style('width');
                originalSizes2[node.id()] = typeof width === 'number' ? width : 25;
            });
            
            cy.on('mouseover', 'node', function(evt) {
                const node = evt.target;
                const originalSize = originalSizes2[node.id()] || 25;
                node.style('width', originalSize * 1.3);
                node.style('height', originalSize * 1.3);
                container.style.cursor = 'pointer';
            });
            
            cy.on('mouseout', 'node', function(evt) {
                const node = evt.target;
                const originalSize = originalSizes2[node.id()] || 25;
                node.style('width', originalSize);
                node.style('height', originalSize);
                container.style.cursor = 'default';
            });
            
            // Preset layout ile çizim yapıldı; ilk render'da hafif fit
            cy.once('render', function() {
                cy.fit(undefined, 80);
            });
            
            // Legend güncelle
            const legend = document.querySelector('.legend');
            legend.innerHTML = `
                <div class="legend-item">
                    <div class="legend-color" style="background: #66ff66;"></div>
                    <span>Kaynak Düğüm</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #4da6ff;"></div>
                    <span>Hedef Düğüm</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #66ff66;"></div>
                    <span>GA Yolu (Yeşil)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff9966;"></div>
                    <span>ACO Yolu (Turuncu)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #cc66ff;"></div>
                    <span>Her İki Yol (Mor)</span>
                </div>
            `;
        }
        
        // Event listener'ları ekle (script sonunda, DOM hazır)
        try {
            const calcBtn = document.getElementById('calculate-btn');
            const compareBtn = document.getElementById('compare-btn');
            
            if (calcBtn) {
                calcBtn.addEventListener('click', calculatePath);
                console.log('✓ Calculate button listener attached');
            } else {
                console.error('Calculate button not found');
            }
            
            if (compareBtn) {
                compareBtn.addEventListener('click', compareAlgorithms);
                console.log('✓ Compare button listener attached');
            } else {
                console.error('Compare button not found');
            }
        } catch (e) {
            console.error('Error attaching event listeners:', e);
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/experiment", response_class=HTMLResponse)
async def experiment_page():
    """Experiment sayfası - HTML frontend"""
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BSM307 - Experiment Arayüzü</title>
    <link rel="icon" href="data:,">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .control-group {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
        }
        input, select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: white;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }
        .slider-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="range"] {
            flex: 1;
        }
        .slider-value {
            min-width: 50px;
            text-align: right;
            font-weight: 600;
            color: #10b981;
        }
        button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }
        button:hover:not(:disabled) {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .back-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            min-height: 200px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .result-item {
            margin-bottom: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 5px solid #10b981;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #10b981;
        }
        .loading::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        .info-box {
            background: #f0fdf4;
            border: 2px solid #10b981;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .info-box h3 {
            color: #059669;
            margin-bottom: 10px;
        }
        .info-box p {
            color: #555;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 BSM307 Experiment Arayüzü</h1>
        <p class="subtitle">Çoklu senaryo testleri ve sonuç analizi</p>
        
        <div class="info-box">
            <h3>📋 Bilgi</h3>
            <p><strong>Ağ:</strong> <span id="graph-info">Yükleniyor...</span></p>
            <p><strong>Açıklama:</strong> Bu arayüz 20 farklı senaryo ile GA ve ACO algoritmalarını test eder. Her senaryo 5 tekrar çalıştırılır (toplam 200 experiment).</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Senaryo Sayısı:</label>
                <input type="number" id="num-scenarios" value="20" min="1" max="100" step="1">
                <small style="color: #666; margin-top: 5px;">PDF gereksinimi: 20 senaryo</small>
            </div>
            <div class="control-group">
                <label>Tekrar Sayısı:</label>
                <input type="number" id="num-repetitions" value="5" min="1" max="20" step="1">
                <small style="color: #666; margin-top: 5px;">PDF gereksinimi: 5 tekrar</small>
            </div>
            <div class="slider-group">
                <label>Gecikme Ağırlığı: <span class="slider-value" id="delay-value">0.4</span></label>
                <div class="slider-container">
                    <input type="range" id="delay-weight" min="0" max="1" step="0.1" value="0.4">
                </div>
            </div>
            <div class="slider-group">
                <label>Güvenilirlik Ağırlığı: <span class="slider-value" id="reliability-value">0.3</span></label>
                <div class="slider-container">
                    <input type="range" id="reliability-weight" min="0" max="1" step="0.1" value="0.3">
                </div>
            </div>
            <div class="slider-group">
                <label>Kaynak Ağırlığı: <span class="slider-value" id="resource-value">0.3</span></label>
                <div class="slider-container">
                    <input type="range" id="resource-weight" min="0" max="1" step="0.1" value="0.3">
                </div>
            </div>
            <button id="run-btn" onclick="runExperiment()">🚀 Experiment'i Çalıştır</button>
            <button class="back-btn" onclick="window.location.href='/'">← Ana UI'ye Dön</button>
        </div>
        
        <div id="results" class="results">
            <div id="results-content"></div>
        </div>
    </div>
    
    <script>
        // Graph bilgilerini yükle
        async function loadGraphInfo() {
            try {
                const response = await fetch('/api/graph/info');
                const data = await response.json();
                document.getElementById('graph-info').textContent = 
                    `${data.nodes} düğüm, ${data.edges} kenar (Seed: ${data.seed})`;
            } catch (error) {
                console.error('Failed to load graph info:', error);
                document.getElementById('graph-info').textContent = 'Bilinmiyor';
            }
        }
        loadGraphInfo();
        
        // Slider value updates
        document.getElementById('delay-weight').addEventListener('input', (e) => {
            document.getElementById('delay-value').textContent = e.target.value;
        });
        document.getElementById('reliability-weight').addEventListener('input', (e) => {
            document.getElementById('reliability-value').textContent = e.target.value;
        });
        document.getElementById('resource-weight').addEventListener('input', (e) => {
            document.getElementById('resource-value').textContent = e.target.value;
        });
        
        // Experiment çalıştır
        async function runExperiment() {
            const btn = document.getElementById('run-btn');
            const results = document.getElementById('results');
            const content = document.getElementById('results-content');
            
            btn.disabled = true;
            results.classList.add('show');
            content.innerHTML = '<div class="loading">⏳ Experiment başlatılıyor...</div>';
            
            const params = {
                num_scenarios: parseInt(document.getElementById('num-scenarios').value) || 20,
                num_repetitions: parseInt(document.getElementById('num-repetitions').value) || 5,
                weights: {
                    delay: parseFloat(document.getElementById('delay-weight').value) || 0.4,
                    reliability: parseFloat(document.getElementById('reliability-weight').value) || 0.3,
                    resource: parseFloat(document.getElementById('resource-weight').value) || 0.3
                }
            };
            
            // Normalize weights
            const total = params.weights.delay + params.weights.reliability + params.weights.resource;
            if (total > 0) {
                params.weights.delay /= total;
                params.weights.reliability /= total;
                params.weights.resource /= total;
            }
            
            try {
                const response = await fetch('/api/experiment/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    content.innerHTML = `<div class="result-item" style="border-left-color: #ef4444;">
                        <h3>❌ Hata</h3>
                        <p>${data.detail || data.error || 'Bilinmeyen hata'}</p>
                    </div>`;
                } else {
                    const totalExp = params.num_scenarios * params.num_repetitions * 2;
                    content.innerHTML = `
                        <div class="result-item">
                            <h3>✅ Experiment Tamamlandı!</h3>
                            <p><strong>Başarı:</strong> ${data.success_count}/${data.total_count} (${data.success_rate.toFixed(1)}%)</p>
                            <p><strong>Toplam Experiment:</strong> ${totalExp} (${params.num_scenarios} senaryo × ${params.num_repetitions} tekrar × 2 algoritma)</p>
                            <p><strong>Sonuç Dosyası:</strong> ${data.results_file || 'Kaydedildi'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                content.innerHTML = `<div class="result-item" style="border-left-color: #ef4444;">
                    <h3>❌ Hata</h3>
                    <p>${error.message}</p>
                </div>`;
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/experiment/run")
async def run_experiment(request: Dict[str, Any]):
    """
    Experiment çalıştır endpoint
    
    Request body:
    {
        "num_scenarios": int,
        "num_repetitions": int,
        "weights": {
            "delay": float,
            "reliability": float,
            "resource": float
        }
    }
    """
    try:
        from pathlib import Path
        from datetime import datetime
        import sys
        
        # Project root'u bul
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from experiments.experiment_runner import ExperimentRunner, save_results_to_json
        from experiments.scenario_generator import generate_scenarios_for_experiment
        
        num_scenarios = int(request.get("num_scenarios", 20))
        num_repetitions = int(request.get("num_repetitions", 5))
        weights_dict = request.get("weights", {"delay": 0.4, "reliability": 0.3, "resource": 0.3})
        
        # Weights normalize et
        wd = float(weights_dict.get("delay", 0.4))
        wr = float(weights_dict.get("reliability", 0.3))
        wc = float(weights_dict.get("resource", 0.3))
        total = wd + wr + wc
        if total > 0:
            wd /= total
            wr /= total
            wc /= total
        weights = (wd, wr, wc)
        
        graph = get_or_create_graph()
        
        # Senaryoları üret
        scenarios = generate_scenarios_for_experiment(
            graph=graph,
            num_scenarios=num_scenarios,
            seed=_graph_seed or 42
        )
        
        # Experiment runner
        runner = ExperimentRunner(
            graph=graph,
            weights=weights,
            num_repetitions=num_repetitions
        )
        
        # Experiment'leri çalıştır
        results = runner.run_all_scenarios(
            scenarios=scenarios,
            algorithms=["GA", "ACO"]
        )
        
        # İstatistikler
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        # Sonuçları kaydet
        output_dir = project_root / "experiments" / "results"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = output_dir / f"results_{timestamp}.json"
        
        save_results_to_json(results, str(results_file))
        
        return {
            "success": True,
            "success_count": success_count,
            "total_count": total_count,
            "success_rate": success_rate,
            "results_file": results_file.name,
            "results_path": str(results_file)
        }
    
    except Exception as e:
        logger.error("Error running experiment: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "BSM307 Routing API"}


@app.get("/api/graph/info")
async def graph_info():
    """Graph bilgilerini döndür"""
    graph = get_or_create_graph()
    max_node_id = graph.number_of_nodes() - 1
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "seed": _graph_seed,
        "max_node_id": max_node_id
    }


@app.post("/api/calculate")
async def calculate_path(request: Dict[str, Any]):
    """
    Path hesapla endpoint
    
    Request body:
    {
        "source": int,
        "target": int,
        "bandwidth": float,
        "algorithm": "GA" | "ACO",
        "weights": {
            "delay": float,
            "reliability": float,
            "resource": float
        }
    }
    """
    try:
        source = int(request.get("source", 0))
        target = int(request.get("target", 100))
        bandwidth = float(request.get("bandwidth", 500.0))
        algorithm = request.get("algorithm", "GA").upper()
        weights_dict = request.get("weights", {"delay": 0.4, "reliability": 0.3, "resource": 0.3})
        
        # Weights normalize et
        wd = float(weights_dict.get("delay", 0.4))
        wr = float(weights_dict.get("reliability", 0.3))
        wc = float(weights_dict.get("resource", 0.3))
        total = wd + wr + wc
        if total > 0:
            wd /= total
            wr /= total
            wc /= total
        weights = (wd, wr, wc)
        
        graph = get_or_create_graph()
        
        # Node validasyonu (0-based indexing, max node ID = num_nodes - 1)
        max_node_id = graph.number_of_nodes() - 1
        if source < 0 or source > max_node_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Source node {source} is invalid. Valid range: 0-{max_node_id}"
            )
        if target < 0 or target > max_node_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Target node {target} is invalid. Valid range: 0-{max_node_id}"
            )
        if source == target:
            raise HTTPException(status_code=400, detail="Source and target cannot be the same")
        
        # Node'ların graph'ta olup olmadığını kontrol et
        if source not in graph:
            raise HTTPException(status_code=400, detail=f"Source node {source} is not in graph")
        if target not in graph:
            raise HTTPException(status_code=400, detail=f"Target node {target} is not in graph")
        
        # Path kontrolü
        if not nx.has_path(graph, source, target):
            raise HTTPException(status_code=400, detail=f"No path between {source} and {target}")
        
        # Bandwidth validation (PDF: 100-1000 Mbps)
        if bandwidth < 100 or bandwidth > 1000:
            raise HTTPException(
                status_code=400, 
                detail=f"Bandwidth {bandwidth} Mbps is invalid. Valid range: 100-1000 Mbps (PDF requirement)."
            )
        
        # Algorithm çalıştır (PDF gereksinimleri: farklı seed'ler farklı sonuçlar için)
        # GA ve ACO farklı seed kullanarak farklı sonuçlar üretir
        if algorithm == "GA":
            ga = GeneticAlgorithm(
                graph=graph,
                source=source,
                target=target,
                weights=weights,
                required_bandwidth=bandwidth,
                population_size=50,  # Artırıldı
                crossover_rate=0.8,
                mutation_rate=0.1,  # Artırıldı (daha fazla çeşitlilik)
                seed=42  # GA için seed
            )
            path, cost = ga.run(generations=50)
        elif algorithm == "ACO":
            aco = AntColonyOptimizer(
                graph=graph,
                source=source,
                target=target,
                weights=weights,
                required_bandwidth=bandwidth,
                num_ants=30,
                alpha=1.5,  # Farklı parametreler (GA'dan farklı)
                beta=2.5,   # Farklı parametreler
                evaporation_rate=0.15,  # Farklı parametreler
                seed=123  # ACO için FARKLI seed (farklı sonuçlar için)
            )
            path, cost = aco.run(iterations=50)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")
        
        # Path kontrolü (algoritma path bulamadıysa)
        if not path or len(path) < 2:
            raise HTTPException(
                status_code=404,
                detail=f"Algorithm {algorithm} could not find a valid path from {source} to {target} with bandwidth {bandwidth} Mbps. Try reducing bandwidth or different source/target nodes."
            )
        
        # Metrikleri hesapla
        delay = total_delay(graph=graph, path=path)
        rel_cost = reliability_cost(graph=graph, path=path)
        res_cost = bandwidth_cost(graph=graph, path=path)
        
        # Graph layout pozisyonları (görselleştirme için)
        import json
        pos = nx.spring_layout(graph, seed=42, k=0.5, iterations=50)
        # NetworkX pos dict'i JSON serializable yap
        positions = {str(k): [float(v[0]), float(v[1])] for k, v in pos.items()}
        
        # Graph edges (görselleştirme için)
        edges = [[int(u), int(v)] for u, v in graph.edges()]
        
        return {
            "path": path,
            "algorithm": algorithm,
            "metrics": {
                "delay": delay,
                "reliability_cost": rel_cost,
                "resource_cost": res_cost,
                "weighted_cost": cost
            },
            "graph": {
                "nodes": list(graph.nodes()),
                "edges": edges,
                "positions": positions,
                "num_nodes": graph.number_of_nodes(),
                "num_edges": graph.number_of_edges()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error calculating path: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    logger.info("Starting FastAPI server on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port)

