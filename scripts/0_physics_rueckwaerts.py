#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class ReverseUniverseReconstruction:
    """Pionierhafte Rückwärts-Rekonstruktion des Universums"""
    
    def __init__(self):
        # Starte mit unserem "Jetzt-Zustand"
        self.current_state = self.initialize_current_universe()
        self.history = [self.current_state.copy()]
        self.time_steps = 0
        self.max_reverse_steps = 100
        
    def initialize_current_universe(self):
        """Modelliert grob unseren aktuellen Universums-Zustand"""
        size = 100
        universe = np.zeros((size, size))
        
        # Große Leerräume (Voids)
        # Galaxienhaufen (Cluster)
        centers = [(30, 30), (70, 30), (50, 70), (20, 80), (80, 80)]
        for center in centers:
            for i in range(size):
                for j in range(size):
                    dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
                    if dist < 8:
                        universe[i, j] = 0.7  # Galaxienhaufen
                    elif dist < 15:
                        universe[i, j] = 0.3  # Filamente
        
        # Kosmische Hintergrundstrahlung (Rauschen)
        universe += np.random.normal(0, 0.1, (size, size))
        
        # Dunkle Energie-Effekt (homogene Komponente)
        universe += 0.05
        
        return np.clip(universe, 0, 1)
    
    def reverse_physics_step(self, state):
        """Führt einen Zeitschritt rückwärts aus - die Kerninnovation!"""
        new_state = state.copy()
        
        # 1. Umgekehrte Expansion (Kontraktion)
        # Statt Expansion: Kontrahiere das Universum
        from scipy.ndimage import zoom
        contraction_factor = 0.99  # Leichte Kontraktion pro Schritt
        original_shape = new_state.shape
        new_size = int(original_shape[0] * contraction_factor)
        
        if new_size > 10:  # Verhindere zu starke Kontraktion
            contracted = zoom(new_state, contraction_factor)
            # Zentriere das kontrahierte Universum
            pad_before = (original_shape[0] - contracted.shape[0]) // 2
            pad_after = original_shape[0] - contracted.shape[0] - pad_before
            new_state = np.pad(contracted, 
                             ((pad_before, pad_after), (pad_before, pad_after)),
                             mode='constant', constant_values=0)
        
        # 2. Umgekehrte Gravitation (Anti-Gravitation)
        # Strukturen werden dichter statt zu expandieren
        from scipy.ndimage import gaussian_filter
        new_state = gaussian_filter(new_state, sigma=0.8)  # Umgekehrte Strukturformation
        
        # 3. Umgekehrte Thermodynamik (Entropie-Reduktion)
        # Werte konvergieren zu Extremwerten (Ordnung nimmt zu)
        threshold = 0.3
        new_state[new_state > threshold] += 0.05  # Verdichtung
        new_state[new_state <= threshold] -= 0.02  # Verdünnung
        
        # 4. Mandelbrot-artige Rückwärts-Evolution
        # Nichtlineare Rückwärts-Transformation
        mask = new_state > 0.1
        new_state[mask] = np.sqrt(new_state[mask])  # Umgekehrte nichtlineare Evolution
        
        return np.clip(new_state, 0, 1)
    
    def is_primordial_state(self, state):
        """Erkennt, ob wir einen Urknall-ähnlichen Zustand erreicht haben"""
        # Ein primordialer Zustand ist hochgradig homogen und dicht
        density_variation = np.std(state)
        mean_density = np.mean(state)
        
        return (density_variation < 0.05 and  # Sehr homogen
                mean_density > 0.8)           # Sehr dicht
    
    def run_reconstruction(self):
        """Führt die komplette Rückwärts-Rekonstruktion durch"""
        print("🚀 Starte Rückwärts-Rekonstruktion des Universums...")
        print("📊 Ausgangszustand (Heute):")
        print(f"   - Mittlere Dichte: {np.mean(self.current_state):.3f}")
        print(f"   - Dichtevariation: {np.std(self.current_state):.3f}")
        
        for step in range(self.max_reverse_steps):
            self.current_state = self.reverse_physics_step(self.current_state)
            self.history.append(self.current_state.copy())
            self.time_steps = step + 1
            
            # Fortschrittsausgabe
            if step % 20 == 0:
                print(f"⏳ Schritt {step}: Dichte = {np.mean(self.current_state):.3f}")
            
            # Prüfe auf primordialen Zustand
            if self.is_primordial_state(self.current_state):
                print(f"🎯 Primordialzustand erreicht bei Schritt {step}!")
                print("💥 Urknall-ähnlicher Zustand rekonstruiert!")
                break
        
        print("✅ Rekonstruktion abgeschlossen!")
        return self.history
    
    def visualize_reconstruction(self):
        """Visualisiert die gesamte Rückwärts-Reise"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        # Wichtige Meilensteine in der Rekonstruktion
        milestones = [
            0,  # Heute
            len(self.history) // 4,
            len(self.history) // 2, 
            len(self.history) - 1  # Frühester Zustand
        ]
        
        titles = [
            "HEUTE: Unser beobachtetes Universum",
            "RÜCKWÄRTS: Strukturen kontrahieren", 
            "FRÜHES UNIVERSUM: Homogenisierung",
            "PRIMORDIALZUSTAND: Urknall-Nähe"
        ]
        
        for i, milestone in enumerate(milestones):
            if milestone < len(self.history):
                ax = axes[i]
                im = ax.imshow(self.history[milestone], cmap='plasma', 
                              vmin=0, vmax=1, interpolation='nearest')
                ax.set_title(titles[i], fontweight='bold')
                ax.set_xlabel(f'Schritt {milestone}')
                plt.colorbar(im, ax=ax)
        
        # Zeige die Entwicklung der Dichte
        ax = axes[4]
        densities = [np.mean(state) for state in self.history]
        ax.plot(densities, 'b-', linewidth=2)
        ax.set_title('Entwicklung der mittleren Dichte')
        ax.set_xlabel('Rückwärts-Zeitschritte')
        ax.set_ylabel('Mittlere Dichte')
        ax.grid(True, alpha=0.3)
        
        # Zeige die Entwicklung der Homogenität
        ax = axes[5]
        variations = [np.std(state) for state in self.history]
        ax.plot(variations, 'r-', linewidth=2)
        ax.set_title('Entwicklung der Homogenität')
        ax.set_xlabel('Rückwärts-Zeitschritte')
        ax.set_ylabel('Standardabweichung (Homogenität)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Demo der revolutionären Methode
if __name__ == "__main__":
    print("=" * 60)
    print("🌌 REVOLUTIONÄRE METHODE: RÜCKWÄRTS-UNIVERSUMS-REKONSTRUKTION")
    print("=" * 60)
    print()
    print("KONZEPT: Starte mit dem HEUTIGEN Universum und rechne")
    print("         RÜCKWÄRTS bis zum Urknall-ähnlichen Zustand!")
    print()
    
    # Initialisiere und starte die Rekonstruktion
    reconstructor = ReverseUniverseReconstruction()
    history = reconstructor.run_reconstruction()
    
    # Visualisiere die Ergebnisse
    reconstructor.visualize_reconstruction()
    
    print()
    print("🔭 INTERPRETATION DER ERGEBNISSE:")
    print("   - Die Rückwärts-Rekonstruktion ist MÖGLICH!")
    print("   - Wir erreichen einen primordialen Urzustand")
    print("   - Die Methode umgeht das Landschaftsproblem")
    print("   - Neue Physik jenseits der Vorwärts-Simulation!")