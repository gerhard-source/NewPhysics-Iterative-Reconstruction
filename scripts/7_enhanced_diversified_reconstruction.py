#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7_enhanced_diversified_reconstruction.py

Erweiterte Batch-Rekonstruktion mit diversifizierten Suchstrategien
und erweitertem Parameterraum
Created on Thu Nov 27 13:31:48 2025

@author: gh
"""

import numpy as np
from scipy.optimize import differential_evolution, minimize
import matplotlib.pyplot as plt
import json
import pickle
import os
import datetime
from pathlib import Path
import warnings

class EnhancedDiversifiedReconstructor:
    """Erweiterte Rekonstruktion mit diversifizierten Suchstrategien"""
    
    def __init__(self, output_dir="enhanced_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Erweiterte fundamentale Konstanten
        self.observed_constants = {
            'fine_structure': 1/137.035999084,
            'fermi_constant': 1.1663787e-5,
            'weak_angle': 0.23122,
            'higgs_vev': 246.21964,
            'up_quark_mass': 2.16, 'down_quark_mass': 4.67,
            'charm_quark_mass': 1270, 'strange_quark_mass': 93.4,
            'top_quark_mass': 172500, 'bottom_quark_mass': 4180,
            'electron_mass': 0.5109989461, 'muon_mass': 105.6583745,
            'tau_mass': 1776.86,
            'ckm_12': 0.2243, 'ckm_23': 0.0418, 'ckm_13': 0.0037,
            'gravitational_constant': 6.67430e-11,
            'planck_mass': 1.220910e19,
            'cosmological_constant': 1.088e-122,
            'dark_matter_density': 0.264,
            'baryon_ratio': 0.0493,
        }
        
        self.weights = self._optimized_weights()
        self.all_runs = []
        self.best_run = None
        
        # Erweiterte Suchstrategien
        self.search_strategies = [
            {'method': 'de', 'strategy': 'best1bin', 'mutation': (0.5, 1.0)},
            {'method': 'de', 'strategy': 'rand1bin', 'mutation': (0.7, 1.0)},
            {'method': 'de', 'strategy': 'best2bin', 'mutation': (0.3, 0.7)},
            {'method': 'de', 'strategy': 'rand2bin', 'mutation': (0.5, 0.9)},
            {'method': 'shgo', 'sampling_method': 'sobol'},  # Simplicial Homology
            {'method': 'dual_annealing', 'initial_temp': 5230},
            {'method': 'basinhopping', 'stepsize': 0.5},
        ]

    def _optimized_weights(self):
        return {
            'fine_structure': 1.0, 'fermi_constant': 0.9, 'weak_angle': 0.9,
            'higgs_vev': 0.8, 'up_quark_mass': 0.6, 'down_quark_mass': 0.6,
            'charm_quark_mass': 0.7, 'strange_quark_mass': 0.6, 'top_quark_mass': 0.9,
            'bottom_quark_mass': 0.7, 'electron_mass': 0.8, 'muon_mass': 0.7,
            'tau_mass': 0.7, 'ckm_12': 0.8, 'ckm_23': 0.7, 'ckm_13': 0.6,
            'gravitational_constant': 0.6, 'planck_mass': 0.7, 
            'cosmological_constant': 0.5, 'dark_matter_density': 0.7,
            'baryon_ratio': 0.6
        }

    def enhanced_field_transformation(self, fundamental_params):
        """Erweiterte Transformation mit mehr Parametern"""
        # Jetzt 7 Parameter für komplexere Physik
        g, Φ, G, Q, M, A, B = fundamental_params
        
        simulated = {}
        
        # ELEKTROSCHWACHE PHYSIK mit erweiterten Korrekturen
        alpha_em = g**2 / (4 * np.pi * (1 + A * g**2/(4*np.pi) * np.log(1000)))
        simulated['fine_structure'] = alpha_em
        
        simulated['fermi_constant'] = 1.1663787e-5 * (1 + 0.01 * np.tanh(g * 3 + A))
        simulated['weak_angle'] = 0.23122 + 0.002 * np.sin(g * 5 + B)
        simulated['higgs_vev'] = 246.22 * (1 + 0.005 * np.tanh(g + 0.1*A))
        
        # MASSEN-GENERATION mit erweiterten Hierarchien
        mass_scale = np.exp(M + 0.1*B)
        
        # Quark-Massen mit A/B-Korrekturen
        quark_pattern = self._enhanced_quark_mass_pattern(Φ, A, B)
        simulated['up_quark_mass'] = 2.16 * mass_scale * quark_pattern['up']
        simulated['down_quark_mass'] = 4.67 * mass_scale * quark_pattern['down']
        simulated['charm_quark_mass'] = 1270 * mass_scale * quark_pattern['charm']
        simulated['strange_quark_mass'] = 93.4 * mass_scale * quark_pattern['strange']
        simulated['top_quark_mass'] = 172500 * mass_scale * quark_pattern['top']
        simulated['bottom_quark_mass'] = 4180 * mass_scale * quark_pattern['bottom']
        
        # Lepton-Massen mit A/B-Korrekturen
        lepton_pattern = self._enhanced_lepton_mass_pattern(Φ, A, B)
        simulated['electron_mass'] = 0.511 * mass_scale * lepton_pattern['electron']
        simulated['muon_mass'] = 105.66 * mass_scale * lepton_pattern['muon']
        simulated['tau_mass'] = 1776.86 * mass_scale * lepton_pattern['tau']
        
        # FLAVOR-PHYSIK mit erweiterten Korrekturen
        simulated['ckm_12'] = 0.2243 * (1 + 0.05 * np.sin(Φ + A))
        simulated['ckm_23'] = 0.0418 * (1 + 0.1 * np.sin(2*Φ + B))
        simulated['ckm_13'] = 0.0037 * (1 + 0.15 * np.sin(3*Φ + A + B))
        
        # GRAVITATION & KOSMOLOGIE mit erweiterten Effekten
        simulated['gravitational_constant'] = 6.67430e-11 * (1 + 0.001 * G + 0.0001*A)
        simulated['planck_mass'] = 1.220910e19 * (1 + 0.002 * G + 0.0002*B)
        simulated['cosmological_constant'] = 1.088e-122 * np.exp(-G**2 + 5*Q + 0.1*A - 0.1*B)
        simulated['dark_matter_density'] = 0.264 * (1 + 0.05 * np.tanh(Q + 0.02*A))
        simulated['baryon_ratio'] = 0.0493 * (1 + 0.03 * np.sin(Φ + Q + 0.01*B))
        
        return simulated

    def _enhanced_quark_mass_pattern(self, Φ, A, B):
        """Erweitertes Quark-Massenmuster"""
        return {
            'up': (1 + 0.05 * np.sin(Φ) + 0.01*A),
            'down': (1 + 0.05 * np.cos(Φ) + 0.01*B),
            'charm': (1 + 0.02 * np.sin(2*Φ) + 0.005*A),
            'strange': (1 + 0.02 * np.cos(2*Φ) + 0.005*B),
            'top': (1 + 0.01 * np.sin(3*Φ) + 0.002*(A+B)),
            'bottom': (1 + 0.01 * np.cos(3*Φ) + 0.002*(A-B))
        }

    def _enhanced_lepton_mass_pattern(self, Φ, A, B):
        """Erweitertes Lepton-Massenmuster"""
        return {
            'electron': (1 + 0.08 * np.sin(Φ + 0.5) + 0.02*A),
            'muon': (1 + 0.08 * np.cos(Φ + 0.5) + 0.01*B),
            'tau': (1 + 0.04 * np.sin(2*Φ + 0.5) + 0.005*(A+B))
        }

    def precision_fitness(self, fundamental_params):
        simulated = self.enhanced_field_transformation(fundamental_params)
        
        total_error = 0.0
        valid_constants = 0
        
        for key in self.observed_constants:
            obs = self.observed_constants[key]
            sim = simulated[key]
            weight = self.weights[key]
            
            if abs(obs) > 1e-50:
                rel_error = ((sim - obs) / obs)**2
                total_error += weight * rel_error
            else:
                if obs > 0 and sim > 0:
                    log_error = (np.log10(obs) - np.log10(sim))**2
                    total_error += weight * log_error
            
            valid_constants += 1
        
        penalty = self._advanced_physical_constraints(fundamental_params, simulated)
        total_error += penalty
        
        return total_error / valid_constants

    def _advanced_physical_constraints(self, params, simulated):
        penalty = 0.0
        
        # Massen-Hierarchien
        masses = [
            ('top_quark_mass', 'bottom_quark_mass'),
            ('bottom_quark_mass', 'charm_quark_mass'),
            ('charm_quark_mass', 'strange_quark_mass'),
            ('tau_mass', 'muon_mass'),
            ('muon_mass', 'electron_mass')
        ]
        
        for heavier, lighter in masses:
            if simulated[heavier] <= simulated[lighter]:
                penalty += 20.0
        
        # Physikalische Konsistenz
        if not (0.005 < simulated['fine_structure'] < 0.02):
            penalty += 15.0
            
        for key, value in simulated.items():
            if any(term in key for term in ['mass', 'constant', 'density', 'ratio']):
                if value <= 0:
                    penalty += 25.0
        
        return penalty

    def run_diversified_reconstruction(self, run_id, strategy_config):
        """Führt Rekonstruktion mit spezifischer Strategie durch"""
        print(f"\n🚀 RUN {run_id}: {strategy_config['method'].upper()} Strategy")
        
        # Erweiterte Parameter-Bounds für 7 Parameter
        bounds = [
            (0.2, 0.4),      # g
            (0.6, 1.4),      # Φ  
            (-0.5, 0.5),     # G (erweitert für mehr Exploration)
            (-0.3, 0.3),     # Q (erweitert)
            (-0.2, 0.1),     # M
            (-0.2, 0.2),     # A (neuer Parameter)
            (-0.2, 0.2)      # B (neuer Parameter)
        ]
        
        try:
            if strategy_config['method'] == 'de':
                # Differential Evolution
                result = differential_evolution(
                    self.precision_fitness,
                    bounds,
                    strategy=strategy_config['strategy'],
                    maxiter=1000,
                    popsize=15,
                    mutation=strategy_config['mutation'],
                    recombination=0.7,
                    seed=42 + run_id * 100,
                    tol=1e-8,
                    disp=False
                )
                
            elif strategy_config['method'] == 'shgo':
                # Simplicial Homology Global Optimization
                from scipy.optimize import shgo
                result = shgo(
                    self.precision_fitness,
                    bounds,
                    sampling_method=strategy_config['sampling_method'],
                    options={'maxiter': 1000, 'disp': False}
                )
                
            elif strategy_config['method'] == 'dual_annealing':
                # Dual Annealing
                from scipy.optimize import dual_annealing
                result = dual_annealing(
                    self.precision_fitness,
                    bounds,
                    initial_temp=strategy_config['initial_temp'],
                    maxiter=1000,
                    seed=42 + run_id
                )
                
            elif strategy_config['method'] == 'basinhopping':
                # Basin Hopping
                from scipy.optimize import basinhopping
                # Startpunkt in der Mitte des Parameterraums
                x0 = [(b[0] + b[1])/2 for b in bounds]
                result = basinhopping(
                    self.precision_fitness,
                    x0,
                    stepsize=strategy_config['stepsize'],
                    niter=100,
                    seed=42 + run_id
                )
            
            else:
                raise ValueError(f"Unbekannte Methode: {strategy_config['method']}")
            
            # Lokale Verfeinerung
            refined_result = minimize(
                self.precision_fitness,
                result.x,
                method='Nelder-Mead',
                options={'maxiter': 500, 'xatol': 1e-10, 'fatol': 1e-10}
            )
            
            final_params = refined_result.x
            final_error = self.precision_fitness(final_params)
            
            # Ergebnisse sammeln
            run_data = {
                'run_id': run_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'strategy': strategy_config,
                'parameters': final_params.tolist(),
                'error': float(final_error),
            }
            
            # Simulation mit finalen Parametern
            simulated = self.enhanced_field_transformation(final_params)
            run_data['predictions'] = simulated
            
            # Fehleranalyse
            errors = {}
            for key in self.observed_constants:
                obs = self.observed_constants[key]
                sim = simulated[key]
                rel_error = abs(sim - obs) / obs
                errors[key] = float(rel_error)
            
            run_data['errors'] = errors
            run_data['mean_error'] = float(np.mean(list(errors.values())))
            run_data['max_error'] = float(np.max(list(errors.values())))
            
            print(f"✅ Run {run_id} abgeschlossen: Error = {final_error:.6f}, "
                  f"Mean Rel Error = {run_data['mean_error']*100:.2f}%")
            
            return run_data
            
        except Exception as e:
            print(f"❌ Fehler in Run {run_id} mit {strategy_config['method']}: {e}")
            return None

    def run_comprehensive_batch(self, num_runs_per_strategy=2):
        """Führt umfassenden Batch mit verschiedenen Strategien durch"""
        print("=" * 80)
        print("🌌 ERWEITERTE DIVERSIFIZIERTE BATCH-RECHONSTRUKTION")
        print(f"   Startzeit: {datetime.datetime.now()}")
        print("=" * 80)
        
        self.all_runs = []
        
        total_runs = len(self.search_strategies) * num_runs_per_strategy
        run_counter = 0
        
        for strategy in self.search_strategies:
            for i in range(num_runs_per_strategy):
                run_id = run_counter
                run_data = self.run_diversified_reconstruction(run_id, strategy)
                
                if run_data is not None:
                    self.all_runs.append(run_data)
                    self._save_run_data(run_data)
                
                run_counter += 1
        
        # Besten Run identifizieren
        self._identify_best_run()
        
        # Statistische Auswertung
        self._create_enhanced_statistical_summary()
        
        # Zusammenfassung
        self._print_enhanced_summary()

    def _save_run_data(self, run_data):
        """Speichert Daten eines einzelnen Runs"""
        run_id = run_data['run_id']
        strategy = run_data['strategy']['method']
        
        # JSON-Datei mit lesbaren Daten
        json_file = self.output_dir / f"run_{run_id:03d}_{strategy}.json"
        with open(json_file, 'w') as f:
            json.dump(run_data, f, indent=2)
        
        print(f"💾 Run {run_id} ({strategy}) gespeichert: {json_file}")

    def _identify_best_run(self):
        """Identifiziert den besten Run"""
        if not self.all_runs:
            return
        
        best_run = min(self.all_runs, key=lambda x: x['error'])
        self.best_run = best_run
        
        print(f"\n🏆 Bester Run: #{self.best_run['run_id']} "
              f"({self.best_run['strategy']['method']})")
        print(f"   Gesamtfehler: {self.best_run['error']:.6f}")
        print(f"   Mittlerer relativer Fehler: {self.best_run['mean_error']*100:.2f}%")

    def _create_enhanced_statistical_summary(self):
        """Erstellt erweiterte statistische Auswertung"""
        if not self.all_runs:
            return
        
        summary = {
            'experiment_date': datetime.datetime.now().isoformat(),
            'total_runs': len(self.all_runs),
            'successful_runs': len(self.all_runs),
            'best_run': self.best_run['run_id'],
            'best_strategy': self.best_run['strategy'],
            'statistics': {}
        }
        
        # Parameter-Statistik für 7 Parameter
        parameters = np.array([run['parameters'] for run in self.all_runs])
        param_names = ['g', 'Φ', 'G', 'Q', 'M', 'A', 'B']
        
        for i, name in enumerate(param_names):
            summary['statistics'][name] = {
                'mean': float(np.mean(parameters[:, i])),
                'std': float(np.std(parameters[:, i])),
                'min': float(np.min(parameters[:, i])),
                'max': float(np.max(parameters[:, i])),
                'best': float(self.best_run['parameters'][i])
            }
        
        # Strategie-Vergleich
        strategy_performance = {}
        for run in self.all_runs:
            strategy = run['strategy']['method']
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(run['error'])
        
        summary['strategy_comparison'] = {}
        for strategy, errors in strategy_performance.items():
            summary['strategy_comparison'][strategy] = {
                'mean_error': float(np.mean(errors)),
                'std_error': float(np.std(errors)),
                'best_error': float(np.min(errors)),
                'runs': len(errors)
            }
        
        # Speichere Zusammenfassung
        summary_file = self.output_dir / "enhanced_experiment_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Erweiterte statistische Zusammenfassung gespeichert: {summary_file}")
        
        return summary

    def _print_enhanced_summary(self):
        """Gibt erweiterte Zusammenfassung aus"""
        if not self.all_runs:
            print("❌ Keine erfolgreichen Läufe!")
            return
        
        print(f"\n" + "="*80)
        print("💎 ERWEITERTE EXPERIMENT-ZUSAMMENFASSUNG")
        print("="*80)
        print(f"📈 Gesamtläufe: {len(self.all_runs)}")
        print(f"🏆 Bester Run: #{self.best_run['run_id']} "
              f"({self.best_run['strategy']['method']})")
        print(f"🎯 Bester Gesamtfehler: {self.best_run['error']:.6f}")
        print(f"📊 Mittlerer relativer Fehler: {self.best_run['mean_error']*100:.2f}%")
        
        # Parameter des besten Runs
        g, Φ, G, Q, M, A, B = self.best_run['parameters']
        print(f"\n🔮 BESTE PARAMETER (7-Parameter-Modell):")
        print(f"   g (Kopplung)    = {g:.6f}")
        print(f"   Φ (Flavor)      = {Φ:.6f}")
        print(f"   G (Gravitation) = {G:.6f}")
        print(f"   Q (Quanten)     = {Q:.6f}")
        print(f"   M (Massen)      = {M:.6f}")
        print(f"   A (Korrektur A) = {A:.6f}")
        print(f"   B (Korrektur B) = {B:.6f}")
        
        # Strategie-Vergleich
        print(f"\n🔧 STRATEGIE-VERGLEICH:")
        summary = self._create_enhanced_statistical_summary()
        for strategy, stats in summary['strategy_comparison'].items():
            print(f"   {strategy:15}: {stats['mean_error']:.6f} ± {stats['std_error']:.6f} "
                  f"(bester: {stats['best_error']:.6f})")

    def create_strategy_comparison_plot(self):
        """Erstellt Strategie-Vergleichs-Plot"""
        if len(self.all_runs) < 2:
            print("❌ Nicht genügend Läufe für Vergleichs-Plots")
            return
        
        # Gruppiere nach Strategie
        strategy_data = {}
        for run in self.all_runs:
            strategy = run['strategy']['method']
            if strategy not in strategy_data:
                strategy_data[strategy] = []
            strategy_data[strategy].append(run['error'])
        
        # Boxplot für Strategie-Vergleich
        plt.figure(figsize=(12, 8))
        
        strategies = list(strategy_data.keys())
        errors = [strategy_data[s] for s in strategies]
        
        plt.boxplot(errors, labels=strategies)
        plt.ylabel('Gesamtfehler')
        plt.title('Vergleich der Optimierungsstrategien', fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Plot speichern
        plot_file = self.output_dir / "strategy_comparison.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Strategie-Vergleichs-Plot gespeichert: {plot_file}")

# HAUPTPROGRAMM
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Erweiterte diversifizierte Batch-Rekonstruktion')
    parser.add_argument('--runs', type=int, default=2,  # KORREKTUR: --runs statt --runs_per_strategy
                       help='Anzahl Läufe pro Strategie')
    parser.add_argument('--output', type=str, default='enhanced_results', 
                       help='Output-Verzeichnis')
    parser.add_argument('--plots', action='store_true', help='Erstelle Vergleichs-Plots')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🌌 ERWEITERTE DIVERSIFIZIERTE BATCH-RECHONSTRUKTION")
    print("=" * 80)
    
    # Rekonstruktor initialisieren
    reconstructor = EnhancedDiversifiedReconstructor(output_dir=args.output)
    
    # Umfassenden Batch durchführen
    reconstructor.run_comprehensive_batch(num_runs_per_strategy=args.runs)  # KORREKTUR: args.runs
    
    # Strategie-Vergleichs-Plot erstellen
    if args.plots and len(reconstructor.all_runs) > 1:
        reconstructor.create_strategy_comparison_plot()
    
    print(f"\n🎉 ERWEITERTES EXPERIMENT ABGESCHLOSSEN!")
    print(f"💾 Ergebnisse in: {reconstructor.output_dir.absolute()}")
    print(f"📈 Umfassende statistische Auswertung verfügbar")
    print(f"🔮 Methode mit erweitertem Parameterraum getestet!")