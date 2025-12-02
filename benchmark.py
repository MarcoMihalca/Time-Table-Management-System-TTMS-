# benchmark_extended.py
# Benchmark extins pentru algoritmul genetic

import time
from main import (
    genereaza_un_orar_complet,
    selectie_turneu,
    recombinare,
    mutatie,
    calculeaza_fitness,
    NUMAR_GENERATII,
    MARIME_POPULATIE
)

def benchmark_extended():
    print("\n=== BENCHMARK GA (Extins) ===")

    start_time = time.time()

    # liste pentru evolutia fitness-ului
    best_fitness_per_gen = []
    avg_fitness_per_gen = []

    # masuram mutatiile care se intampla efectiv
    total_mutatii = 0

    # populatia initiala
    populatie = [genereaza_un_orar_complet() for _ in range(MARIME_POPULATIE)]

    # rulam generatiile manual pentru a colecta datele
    for gen in range(NUMAR_GENERATII):

        populatie.sort(key=lambda ind: calculeaza_fitness(ind), reverse=True)

        # best fitness din generatie
        best_f = calculeaza_fitness(populatie[0])
        best_fitness_per_gen.append(best_f)

        # fitness mediu din generatie
        avg_f = sum(calculeaza_fitness(ind) for ind in populatie) / len(populatie)
        avg_fitness_per_gen.append(avg_f)

        # elitism
        nr_elite = max(1, MARIME_POPULATIE // 10)
        noua_generatie = populatie[:nr_elite]

        # restul copiilor + mutatii
        while len(noua_generatie) < MARIME_POPULATIE:

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

    # final
    best_individ = populatie[0]
    best_fitness = calculeaza_fitness(best_individ)

    end_time = time.time()
    durata = end_time - start_time
    timp_per_gen = durata / NUMAR_GENERATII

    # baseline random
    baseline_random = calculeaza_fitness(genereaza_un_orar_complet())

    # afisare
    print("\nRezultate Benchmark Extins")
    print("----------------------------------------")
    print(f"Generatii rulate:         {NUMAR_GENERATII}")
    print(f"Marime populatie:         {MARIME_POPULATIE}")
    print(f"Fitness final:            {best_fitness:.4f}")
    print(f"Baseline random:          {baseline_random:.4f}")
    print(f"Timp total executie:      {durata:.4f} secunde")
    print(f"Timp per generatie:       {timp_per_gen:.8f} secunde")
    print(f"Numar total mutatii:      {total_mutatii}")

    print("\nPrimele 5 best fitness:")
    print(best_fitness_per_gen[:5])

    print("\nUltimele 5 best fitness:")
    print(best_fitness_per_gen[-5:])

    print("\nPrimele 5 average fitness:")
    print(avg_fitness_per_gen[:5])

    print("\nUltimele 5 average fitness:")
    print(avg_fitness_per_gen[-5:])

    return best_individ


if __name__ == "__main__":
    benchmark_extended()