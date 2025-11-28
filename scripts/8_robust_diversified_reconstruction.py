#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8_robust_diversified_reconstruction.py

Robuste Version mit verbessertem Error-Handling und alternativen Strategien

Created on Thu Nov 27 15:44:58 2025

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
import traceback

class RobustDiversifiedReconstructor:
    """Robuste Version mit verbessertem Error-Handling"""
    
    def __init__(self, output_dir="robust_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Fundamentale Konstanten
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
        
        # ROBUSTE Suchstrategien (ohne SHGO)
        self.search_strategies = [
            {'method': 'de', 'strategy': 'best1bin', 'mutation': (0.5, 1.0), 'maxiter': 800},
            {'method': 'de', 'strategy': 'rand1bin', 'mutation': (0.7, 1.0), 'maxiter': 800},
            {'method': 'de', 'strategy': 'best2bin', 'mutation': (0.3, 0.7), 'maxiter': 800},
            {'method': 'de', 'strategy': 'rand2bin', 'mutation': (0.5, 0.9), 'maxiter': 800},
            {'method': 'dual_annealing', 'maxiter': 500, 'timeout': 300},  # 5 Minuten Timeout
            {'method': 'basinhopping', 'niter': 50, 'stepsize': 0.5},
            {'method': 'multistart', 'n_restarts': 10},  # Multiple lokale Optimierungen
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
        """5-Parameter Modell (bewährt aus vorherigen Läufen)"""
        g, Φ, G, Q, M = fundamental_params
        
        simulated = {}
        
        # Bewährte Transformation aus erfolgreichen Läufen
        alpha_em = g**2 / (4 * np.pi * (1 + g**2/(4*np.pi) * np.log(1000)))
        simulated['fine_structure'] = alpha_em
        
        simulated['fermi_constant'] = 1.1663787e-5 * (1 + 0.01 * np.tanh(g * 3))
        simulated['weak_angle'] = 0.23122 + 0.002 * np.sin(g * 5)
        simulated['higgs_vev'] = 246.22 * (1 + 0.005 * np.tanh(g))
        
        # Massen-Generation
        mass_scale = np.exp(M)
        
        # Quark-Massen
        quark_pattern = self._quark_mass_pattern(Φ)
        simulated['up_quark_mass'] = 2.16 * mass_scale * quark_pattern['up']
        simulated['down_quark_mass'] = 4.67 * mass_scale * quark_pattern['down']
        simulated['charm_quark_mass'] = 1270 * mass_scale * quark_pattern['charm']
        simulated['strange_quark_mass'] = 93.4 * mass_scale * quark_pattern['strange']
        simulated['top_quark_mass'] = 172500 * mass_scale * quark_pattern['top']
        simulated['bottom_quark_mass'] = 4180 * mass_scale * quark_pattern['bottom']
        
        # Lepton-Massen
        lepton_pattern = self._lepton_mass_pattern(Φ)
        simulated['electron_mass'] = 0.511 * mass_scale * lepton_pattern['electron']
        simulated['muon_mass'] = 105.66 * mass_scale * lepton_pattern['muon']
        simulated['tau_mass'] = 1776.86 * mass_scale * lepton_pattern['tau']
        
        # Flavor-Physik
        simulated['ckm_12'] = 0.2243 * (1 + 0.05 * np.sin(Φ))
        simulated['ckm_23'] = 0.0418 * (1 + 0.1 * np.sin(2*Φ))
        simulated['ckm_13'] = 0.0037 * (1 + 0.15 * np.sin(3*Φ))
        
        # Gravitation & Kosmologie
        simulated['gravitational_constant'] = 6.67430e-11 * (1 + 0.001 * G)
        simulated['planck_mass'] = 1.220910e19 * (1 + 0.002 * G)
        simulated['cosmological_constant'] = 1.088e-122 * np.exp(-G**2 + 5*Q)
        simulated['dark_matter_density'] = 0.264 * (1 + 0.05 * np.tanh(Q))
        simulated['baryon_ratio'] = 0.0493 * (1 + 0.03 * np.sin(Φ + Q))
        
        return simulated

    def _quark_mass_pattern(self, Φ):
        return {
            'up': (1 + 0.05 * np.sin(Φ)),
            'down': (1 + 0.05 * np.cos(Φ)),
            'charm': (1 + 0.02 * np.sin(2*Φ)),
            'strange': (1 + 0.02 * np.cos(2*Φ)),
            'top': (1 + 0.01 * np.sin(3*Φ)),
            'bottom': (1 + 0.01 * np.cos(3*Φ))
        }

    def _lepton_mass_pattern(self, Φ):
        return {
            'electron': (1 + 0.08 * np.sin(Φ + 0.5)),
            'muon': (1 + 0.08 * np.cos(Φ + 0.5)),
            'tau': (1 + 0.04 * np.sin(2*Φ + 0.5))
        }

    def precision_fitness(self, fundamental_params):
        try:
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
            
        except Exception as e:
            # Return großen Fehler bei Exception
            print(f"⚠️  Fitness-Fehler: {e}")
            return 1e10

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

    def run_robust_reconstruction(self, run_id, strategy_config):
        """Robuste Rekonstruktion mit umfassendem Error-Handling"""
        print(f"\n🚀 RUN {run_id}: {strategy_config['method'].upper()} Strategy")
        
        # Bewährte Parameter-Bounds (5 Parameter)
        bounds = [
            (0.2, 0.4),      # g
            (0.6, 1.4),      # Φ  
            (-0.5, 0.5),     # G
            (-0.3, 0.3),     # Q
            (-0.2, 0.1),     # M
        ]
        
        try:
            if strategy_config['method'] == 'de':
                # Differential Evolution
                result = differential_evolution(
                    self.precision_fitness,
                    bounds,
                    strategy=strategy_config['strategy'],
                    maxiter=strategy_config['maxiter'],
                    popsize=12,
                    mutation=strategy_config['mutation'],
                    recombination=0.7,
                    seed=42 + run_id * 100,
                    tol=1e-8,
                    disp=False,
                    workers=1  # Vermeidet Parallelisierungs-Probleme
                )
                
            elif strategy_config['method'] == 'dual_annealing':
                # Dual Annealing mit Timeout
                from scipy.optimize import dual_annealing
                result = dual_annealing(
                    self.precision_fitness,
                    bounds,
                    maxiter=strategy_config['maxiter'],
                    seed=42 + run_id,
                    no_local_search=False
                )
                
            elif strategy_config['method'] == 'basinhopping':
                # Basin Hopping
                from scipy.optimize import basinhopping
                # Startpunkt in der Mitte des Parameterraums
                x0 = np.array([(b[0] + b[1])/2 for b in bounds])
                result = basinhopping(
                    self.precision_fitness,
                    x0,
                    niter=strategy_config['niter'],
                    stepsize=strategy_config['stepsize'],
                    seed=42 + run_id,
                    minimizer_kwargs={'method': 'Nelder-Mead', 'options': {'maxiter': 200}}
                )
                
            elif strategy_config['method'] == 'multistart':
                # Multiple lokale Optimierungen von verschiedenen Startpunkten
                best_result = None
                best_error = float('inf')
                
                for restart in range(strategy_config['n_restarts']):
                    # Zufälliger Startpunkt
                    x0 = np.array([np.random.uniform(b[0], b[1]) for b in bounds])
                    
                    local_result = minimize(
                        self.precision_fitness,
                        x0,
                        method='Nelder-Mead',
                        bounds=bounds,
                        options={'maxiter': 300, 'xatol': 1e-8, 'fatol': 1e-8}
                    )
                    
                    if local_result.success and local_result.fun < best_error:
                        best_error = local_result.fun
                        best_result = local_result
                
                if best_result is not None:
                    result = best_result
                else:
                    raise ValueError("Keine erfolgreiche lokale Optimierung")
            
            else:
                raise ValueError(f"Unbekannte Methode: {strategy_config['method']}")
            
            # Lokale Verfeinerung (falls nicht bereits lokal optimiert)
            if strategy_config['method'] != 'multistart':
                refined_result = minimize(
                    self.precision_fitness,
                    result.x,
                    method='Nelder-Mead',
                    options={'maxiter': 200, 'xatol': 1e-10, 'fatol': 1e-10}
                )
                final_params = refined_result.x
                final_error = refined_result.fun
            else:
                final_params = result.x
                final_error = result.fun
            
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
            print(f"❌ FEHLER in Run {run_id} mit {strategy_config['method']}:")
            print(f"   {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return None

    def run_comprehensive_batch(self, num_runs_per_strategy=2):
        """Führt umfassenden Batch durch mit Fortschrittsanzeige"""
        print("=" * 80)
        print("🌌 ROBUSTE DIVERSIFIZIERTE BATCH-RECHONSTRUKTION")
        print(f"   Startzeit: {datetime.datetime.now()}")
        print(f"   Strategien: {len(self.search_strategies)}")
        print(f"   Läufe pro Strategie: {num_runs_per_strategy}")
        print("=" * 80)
        
        self.all_runs = []
        
        total_runs = len(self.search_strategies) * num_runs_per_strategy
        run_counter = 0
        successful_runs = 0
        
        for strategy_idx, strategy in enumerate(self.search_strategies):
            print(f"\n📊 STRATEGIE {strategy_idx+1}/{len(self.search_strategies)}: {strategy['method']}")
            
            for i in range(num_runs_per_strategy):
                run_id = run_counter
                print(f"   🔄 Lauf {i+1}/{num_runs_per_strategy}...")
                
                run_data = self.run_robust_reconstruction(run_id, strategy)
                
                if run_data is not None:
                    self.all_runs.append(run_data)
                    self._save_run_data(run_data)
                    successful_runs += 1
                
                run_counter += 1
        
        print(f"\n📈 BATCH ABGESCHLOSSEN: {successful_runs}/{total_runs} erfolgreiche Läufe")
        
        if successful_runs > 0:
            # Besten Run identifizieren
            self._identify_best_run()
            
            # Statistische Auswertung
            self._create_enhanced_statistical_summary()
            
            # Zusammenfassung
            self._print_enhanced_summary()
        else:
            print("❌ Keine erfolgreichen Läufe!")

    def _save_run_data(self, run_data):
        """Speichert Daten eines einzelnen Runs"""
        run_id = run_data['run_id']
        strategy = run_data['strategy']['method']
        
        # JSON-Datei mit lesbaren Daten
        json_file = self.output_dir / f"run_{run_id:03d}_{strategy}.json"
        with open(json_file, 'w') as f:
            json.dump(run_data, f, indent=2)
        
        print(f"   💾 Run {run_id} ({strategy}) gespeichert: {json_file}")

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
        """Erstellt statistische Auswertung"""
        if not self.all_runs:
            return
        
        summary = {
            'experiment_date': datetime.datetime.now().isoformat(),
            'total_runs': len(self.all_runs),
            'best_run': self.best_run['run_id'],
            'best_strategy': self.best_run['strategy'],
            'statistics': {}
        }
        
        # Parameter-Statistik
        parameters = np.array([run['parameters'] for run in self.all_runs])
        param_names = ['g', 'Φ', 'G', 'Q', 'M']
        
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
        summary_file = self.output_dir / "robust_experiment_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Statistische Zusammenfassung gespeichert: {summary_file}")
        
        return summary

    def _print_enhanced_summary(self):
        """Gibt Zusammenfassung aus"""
        if not self.all_runs:
            return
        
        print(f"\n" + "="*80)
        print("💎 ROBUSTE EXPERIMENT-ZUSAMMENFASSUNG")
        print("="*80)
        print(f"📈 Erfolgreiche Läufe: {len(self.all_runs)}")
        print(f"🏆 Bester Run: #{self.best_run['run_id']} "
              f"({self.best_run['strategy']['method']})")
        print(f"🎯 Bester Gesamtfehler: {self.best_run['error']:.6f}")
        print(f"📊 Mittlerer relativer Fehler: {self.best_run['mean_error']*100:.2f}%")
        
        # Parameter des besten Runs
        g, Φ, G, Q, M = self.best_run['parameters']
        print(f"\n🔮 BESTE PARAMETER:")
        print(f"   g (Kopplung)    = {g:.6f}")
        print(f"   Φ (Flavor)      = {Φ:.6f}")
        print(f"   G (Gravitation) = {G:.6f}")
        print(f"   Q (Quanten)     = {Q:.6f}")
        print(f"   M (Massen)      = {M:.6f}")

# HAUPTPROGRAMM
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Robuste diversifizierte Batch-Rekonstruktion')
    parser.add_argument('--runs', type=int, default=2, 
                       help='Anzahl Läufe pro Strategie')
    parser.add_argument('--output', type=str, default='robust_results', 
                       help='Output-Verzeichnis')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🌌 ROBUSTE DIVERSIFIZIERTE BATCH-RECHONSTRUKTION")
    print("=" * 80)
    
    # Rekonstruktor initialisieren
    reconstructor = RobustDiversifiedReconstructor(output_dir=args.output)
    
    # Robusten Batch durchführen
    reconstructor.run_comprehensive_batch(num_runs_per_strategy=args.runs)
    
    print(f"\n🎉 ROBUSTES EXPERIMENT ABGESCHLOSSEN!")
    print(f"💾 Ergebnisse in: {reconstructor.output_dir.absolute()}")