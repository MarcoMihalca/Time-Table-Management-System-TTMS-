# benchmark_extended.py
# Benchmark extins pentru algoritmul genetic

import time
import sys
from main import (
    genereaza_un_orar_complet,
    selectie_turneu,
    recombinare,
    mutatie,
    calculeaza_fitness,
    NUMAR_GENERATII,
    MARIME_POPULATIE,
    LUCRARI_DB
)

def benchmark_extended(gen_count=None, pop_size=None):
    # Folosim parametrii specificați sau pe cei din main
    gens = gen_count if gen_count else NUMAR_GENERATII
    pops = pop_size if pop_size else MARIME_POPULATIE
    
    print(f"\n=== BENCHMARK GA ({gens:,} generații, {pops} populatie) ===")

    start_time = time.time()

    # liste pentru evolutia fitness-ului
    best_fitness_per_gen = []
    avg_fitness_per_gen = []

    # masuram mutatiile care se intampla efectiv
    total_mutatii = 0
    
    # track conflicts over time
    conflicts_per_gen = []

    # populatia initiala
    populatie = [genereaza_un_orar_complet() for _ in range(pops)]

    # rulam generatiile manual pentru a colecta datele
    for gen in range(gens):

        populatie.sort(key=lambda ind: calculeaza_fitness(ind), reverse=True)

        # best fitness din generatie
        best_f = calculeaza_fitness(populatie[0])
        best_fitness_per_gen.append(best_f)

        # fitness mediu din generatie
        avg_f = sum(calculeaza_fitness(ind) for ind in populatie) / len(populatie)
        avg_fitness_per_gen.append(avg_f)
        
        # Count conflicts in best individual
        best_ind = populatie[0]
        conflicts = 0
        for i in range(len(best_ind)):
            for j in range(i + 1, len(best_ind)):
                l1, l2 = best_ind[i], best_ind[j]
                if (l1[3] < l2[4]) and (l2[3] < l1[4]):
                    if l1[1] == l2[1] or l1[2] == l2[2]:
                        conflicts += 1
        conflicts_per_gen.append(conflicts)

        # elitism
        nr_elite = max(1, pops // 10)
        noua_generatie = populatie[:nr_elite]

        # restul copiilor + mutatii
        while len(noua_generatie) < pops:

            p1 = selectie_turneu(populatie)
            p2 = selectie_turneu(populatie)

            copil = recombinare(p1, p2)
            copil_initial = copil.copy()

            copil = mutatie(copil)

            # daca s-a schimbat, inseamna ca s-a aplicat mutatie
            if copil != copil_initial:
                total_mutatii += 1

            noua_generatie.append(copil)

        populatie = noua_generatie
        
        # Progress update (adaptive based on number of generations)
        step = max(1, gens // 10)  # 10 updates
        if (gen + 1) % step == 0 or gen == 0:
            print(f"  Gen {gen+1}/{gens}: Best={best_f:.2f}, Avg={avg_f:.2f}, Conflicts={conflicts}")

    # final
    best_individ = populatie[0]
    best_fitness = calculeaza_fitness(best_individ)

    end_time = time.time()
    durata = end_time - start_time
    timp_per_gen = durata / gens

    # baseline random
    baseline_random = calculeaza_fitness(genereaza_un_orar_complet())

    # afisare
    print("\nRezultate Benchmark Extins")
    print("="*70)
    print("PARAMETRI ALGORITM")
    print("="*70)
    print(f"Generatii rulate:           {gens:,}")
    print(f"Marime populatie:           {pops}")
    print(f"Elitism:                    {max(1, pops // 10)} indivizi")
    print(f"Rata mutatie efectiva:      {(total_mutatii / (gens * pops) * 100):.1f}%")
    
    print("\n" + "="*70)
    print("PERFORMANTA")
    print("="*70)
    print(f"Fitness final:              {best_fitness:.2f}/100")
    print(f"Fitness random (baseline):  {baseline_random:.2f}/100")
    if baseline_random > 0:
        print(f"Imbunatatire:               {((best_fitness/baseline_random - 1) * 100):.1f}%")
    print(f"Conflicte finale:           {conflicts_per_gen[-1]}")
    print(f"Timp total executie:        {durata:.2f} secunde ({durata/60:.1f} min)")
    print(f"Timp per generatie:         {timp_per_gen*1000:.3f} ms")
    print(f"Generatii per secunda:      {1/timp_per_gen:.1f}")
    print(f"Numar total mutatii:        {total_mutatii:,}")

    print("\n" + "="*70)
    print("EVOLUTIE FITNESS")
    print("="*70)
    # Adaptive milestones based on generation count
    if gens <= 1000:
        milestones = [0, 100, 500, gens-1]
    elif gens <= 10000:
        milestones = [0, 100, 1000, 5000, gens-1]
    else:
        milestones = [0, 100, 1000, 10000, 50000, gens-1]
    
    for m in milestones:
        if m < len(best_fitness_per_gen):
            print(f"  Gen {m:6d}:  Best={best_fitness_per_gen[m]:6.2f}  Avg={avg_fitness_per_gen[m]:6.2f}  Conflicts={conflicts_per_gen[m]}")

    print("\n" + "="*70)
    print("ANALIZA CONVERGENTA")
    print("="*70)
    print(f"  Fitness initial:          {best_fitness_per_gen[0]:.2f}")
    print(f"  Fitness final:            {best_fitness_per_gen[-1]:.2f}")
    print(f"  Crestere totala:          +{(best_fitness_per_gen[-1] - best_fitness_per_gen[0]):.2f}")
    print(f"  Crestere procentuala:     +{((best_fitness_per_gen[-1]/best_fitness_per_gen[0] - 1) * 100):.1f}%")
    
    # Convergence check
    last_100_best = best_fitness_per_gen[-100:]
    variance = max(last_100_best) - min(last_100_best)
    print(f"  Variatie ultimele 100 gen: {variance:.4f}")
    if variance < 0.5:
        print(f"  Status: ✓ CONVERGENT (stabil)")
    else:
        print(f"  Status: → IN EVOLUTIE (inca se imbunatateste)")
    
    # Generatie la care s-a atins fitness maxim
    max_gen = best_fitness_per_gen.index(max(best_fitness_per_gen))
    print(f"  Peak fitness atins:       Gen {max_gen} ({best_fitness_per_gen[max_gen]:.2f})")
    
    # Conflict-free generations
    conflict_free_gens = [i for i, c in enumerate(conflicts_per_gen) if c == 0]
    if conflict_free_gens:
        print(f"  Prima solutie fara conflicte: Gen {conflict_free_gens[0]}")
        print(f"  Solutii fara conflicte:   {len(conflict_free_gens)}/{gens} generatii")
    else:
        print(f"  Solutii fara conflicte:   0 (nu s-a gasit)")
    
    print("\n" + "="*70)
    print("CEL MAI BUN ORAR GASIT")
    print("="*70)
    print(f"{'LUCRARE':<17} | {'ELEVATOR':<10} | {'MECANIC':<10} | {'INTERVAL'}")
    print("-" * 70)
    
    for programare in best_individ:
        id_l = programare[0]
        nume = LUCRARI_DB[id_l]["nume"]
        elev = programare[1]
        mec = programare[2]
        start, final = programare[3], programare[4]
        
        print(f"{nume:<17} | E{elev:<9} | M{mec:<9} | Slot {start:02d} -> {final:02d}")
    
    print("="*70)

    return best_individ


if __name__ == "__main__":
    # Verificăm argumentele din linia de comandă
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "quick":
            print("Modul QUICK: 5000 generații")
            benchmark_extended(gen_count=5000, pop_size=50)
        elif mode == "medium":
            print("Modul MEDIUM: 20000 generații")
            benchmark_extended(gen_count=20000, pop_size=50)
        elif mode == "full":
            print("Modul FULL: 100000 generații")
            benchmark_extended(gen_count=100000, pop_size=50)
        else:
            print(f"Mod necunoscut: {mode}")
            print("Utilizare: python benchmark.py [quick|medium|full]")
            print("Rulare cu parametrii default...")
            benchmark_extended()
    else:
        # Default: folosește parametrii din main.py
        benchmark_extended()