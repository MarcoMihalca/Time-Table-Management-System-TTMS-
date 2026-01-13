import random
import time
import sys
from datetime import datetime
import copy


listaLucrari = [
    {"id": 0, "nume": "Schimb Ulei",        "durata": 1},
    {"id": 1, "nume": "Frane Fata",         "durata": 2},
    {"id": 2, "nume": "Schimb Roti",        "durata": 1},
    {"id": 3, "nume": "Motor General",      "durata": 4},
    {"id": 4, "nume": "Reglaj Faruri",      "durata": 1},
    {"id": 5, "nume": "Inspectie ITP",      "durata": 2},
    {"id": 6, "nume": "Revizie Completa",   "durata": 6},
    {"id": 7, "nume": "Schimb Baterie",     "durata": 1},
    {"id": 8, "nume": "Aer Conditionat",    "durata": 2},
    {"id": 9, "nume": "Sistem Electric",    "durata": 3},
    {"id": 10, "nume": "Transmisie",        "durata": 5},
    {"id": 11, "nume": "Suspensii",         "durata": 3},
    {"id": 12, "nume": "Evacuare",          "durata": 2},
    {"id": 13, "nume": "Injectoare",        "durata": 3},
    {"id": 14, "nume": "Turbo",             "durata": 4},
    {"id": 15, "nume": "Ambreiaj",          "durata": 4},
    {"id": 16, "nume": "Frane Spate",       "durata": 2},
    {"id": 17, "nume": "Distributie",       "durata": 5},
    {"id": 18, "nume": "Radiatoare",        "durata": 2},
    {"id": 19, "nume": "Diagnoza OBD",      "durata": 1}
]

nrLucrari = len(listaLucrari) #momenan lista de lucrari este prestabilita, pot adauga functie random pentru generarea seturilor de lucrari
nrElevatoare = 3
nrMecanici = 3
timpMaxim = 40
orePeZi = 8

# Parametrii algoritm genetic
MARIME_POPULATIE = 200
NUMAR_GENERATII = 1001
SANSA_MUTATIE = 0.1

#ia o lucrare din lista si ii aloca elevator, mecanic, si start random + calculaza Tfinal
def gena(idLucrare):
    lucrare = listaLucrari[idLucrare]
    durata = lucrare["durata"] #preia durata din dict
    start_maxim_posibil = timpMaxim - durata #calcuzuleaza cel mai tarziu timp de start
    start = random.randint(0, start_maxim_posibil) # timp de pornire 
    final = start + durata # timp de terminrare 
    elevator = random.randint(0, nrElevatoare - 1) # alocacare elevator 
    mecanic = random.randint(0, nrMecanici - 1) # alocare mecanic
    return [idLucrare, elevator, mecanic, start, final] # returneaza gena ca o lista

# creeaza orarul complet pe baza listei date de lucrari
def cromozom():
    orar = []
    for i in range(nrLucrari):
        programare = gena(i)
        orar.append(programare)
    return orar

def calculeaza_fitness(orar):
    penalizare = 0
    bonus = 0
    
    #verifica confliect intre mecanici sau elevatoare, nu se poate lucra la 2 masini simultan 
    for i in range(len(orar)):
        for j in range(i + 1, len(orar)):
            l1, l2 = orar[i], orar[j]
            if (l1[3] < l2[4]) and (l2[3] < l1[4]):
                if l1[1] == l2[1]: 
                    penalizare += 100
                if l1[2] == l2[2]: 
                    penalizare += 100

    
    program_mecanici = {0: [], 1: [], 2: []} # dictionar pentru mecanici
    # adauga fiecare lucrare la mecanicul corespunzator
    for gena in orar:
        id_mecanic = gena[2]
        program_mecanici[id_mecanic].append(gena)
    
    total_lucrari_efectuate = 0
    mecanic_activi = 0
    
    for idMecanic, lucrari in program_mecanici.items():
        if not lucrari: 
            continue
        
        mecanic_activi += 1
        total_lucrari_efectuate += len(lucrari)
        
        lucrari.sort(key=lambda x: x[3])
        
        primulStart = lucrari[0][3]
        ultimulFinal = lucrari[-1][4]
        
        # ]penalizare pentru timp pierdut start tarziu
        if primulStart > 0:
            penalizare += primulStart * 5
            
        # Bonus start devreme
        if primulStart == 0:
            bonus += 50
           
        # penalizare timp mort 
        for k in range(len(lucrari) - 1):
            gap = lucrari[k+1][3] - lucrari[k][4] #calculez timpi morti start lucrare k+1 - final lucrare k
            if gap > 0:
                penalizare += gap * 5
        
        # Bonus compactitate
        totalTimpOcupat = sum(l[4] - l[3] for l in lucrari)
        intervalTotal = ultimulFinal - primulStart
        if intervalTotal > 0:
            densitate = totalTimpOcupat / intervalTotal
            bonus += densitate * 100

        # Penalizare ore pierdute sfarsit zi
        zilePlanificate = timpMaxim // orePeZi
        ultimaZiMecanic = ultimulFinal // orePeZi
        ora_finala_in_zi = ultimulFinal % orePeZi
        zile_economisite = zilePlanificate - ultimaZiMecanic
        if zile_economisite > 0:
            bonus += zile_economisite * 100
        # Bonus extra dacă s-a terminat exact la finalul ultimei zile
        if ora_finala_in_zi == 0:
            bonus += 30
        

    # 3. ANALIZA ELEVATOARE
    program_elevatoare = {0: [], 1: [], 2: []}
    for gena in orar:
        id_elevator = gena[1]
        program_elevatoare[id_elevator].append(gena)
    
    for e_id, lucrari in program_elevatoare.items():
        if not lucrari:
            continue    

        lucrari.sort(key=lambda x: x[3])

        for k in range(len(lucrari) - 1):
            gap = lucrari[k+1][3] - lucrari[k][4]
            if gap > 0:
                penalizare += gap * 2
        
        bonus += len(lucrari) * 10

    # 4. METRICI GLOBALE
    if orar:
        bonus += total_lucrari_efectuate * 30
        timp_finalizare_totala = max(gena[4] for gena in orar)
        ultima_zi_global = timp_finalizare_totala // 8
        
        zile_economisate_global = 4 - ultima_zi_global
        if zile_economisate_global > 0:
            bonus += zile_economisate_global * 300
        
        ore_economisate_in_ultima_zi = ((ultima_zi_global + 1) * 8) - timp_finalizare_totala
        if ore_economisate_in_ultima_zi > 0:
            bonus += ore_economisate_in_ultima_zi * 20
        
        if mecanic_activi == 3:
            bonus += 100
    
    if penalizare == 0:
        scor_brut = 2000 + bonus
    else:
        scor_brut = (1000 + bonus) / (1 + penalizare * 0.005)

    max_possible_score = 3000
    fitness = max(0, min(100, (scor_brut / max_possible_score) * 100))
    return fitness

def selectie_turneu(populatie, fitness_cache):
    a, b = random.sample(populatie, 2)
    return a if fitness_cache[id(a)] > fitness_cache[id(b)] else b

def recombinare(p1, p2):
    k = random.randint(1, nrLucrari - 1)
    copil = copy.deepcopy(p1[:k] + p2[k:])
    return copil

def mutatie(orar):
    orarNou = list(orar)
    for i in range(len(orarNou)):
        sansa = random.random()
        
        if sansa < SANSA_MUTATIE:
            idLucrare = orarNou[i][0]
            orarNou[i] = gena(idLucrare)
    return orarNou

def get_zi_index(slot):
    return slot // 8

def ora_to_string(slot):
    zi = get_zi_index(slot)
    ora_in_zi = slot % 8
    zile = ["Luni", "Marti", "Miercuri", "Joi", "Vineri"]
    return f"{zile[zi]} {9+ora_in_zi:02d}:00"

def afiseaza_orar(orar, fitness):
    print("\n" + "="*80)
    print(f"REZULTAT FINAL (Fitness: {fitness:.2f}/100)")
    if fitness >= 95:
        print("STATUS: *** PERFECT! Orar optim fara conflicte.")
    elif fitness >= 80:
        print("STATUS: ** EXCELENT! Orar eficient.")
    elif fitness >= 60:
        print("STATUS: * BUN. Poate fi imbunatatit.")
    else:
        print("STATUS: X Conflicte sau ineficiente majore.")
    print("="*80)

    orar_sortat = sorted(orar, key=lambda x: (get_zi_index(x[3]), x[3]))

    print(f"{'LUCRARE':<20} | {'ELEVATOR':<10} | {'MECANIC':<10} | {'INTERVAL':<30}")
    print("-" * 80)

    zi_curenta = -1
    for programare in orar_sortat:
        id_l = programare[0]
        nume = listaLucrari[id_l]["nume"]
        elev = programare[1]
        mec = programare[2]
        start, final = programare[3], programare[4]
        
        zi = get_zi_index(start)
        if zi != zi_curenta:
            if zi_curenta != -1:
                print("-" * 80)
            zile = ["LUNI", "MARTI", "MIERCURI", "JOI", "VINERI"]
            print(f"\n>>> {zile[zi]} <<<")
            zi_curenta = zi
        
        interval = f"{ora_to_string(start)} -> {ora_to_string(final)}"
        print(f"{nume:<20} | E{elev:<9} | M{mec:<9} | {interval}")

def ruleaza_cu_benchmark():
    print(f"\n=== BENCHMARK GA ({NUMAR_GENERATII:,} generatii, {MARIME_POPULATIE} populatie) ===\n")
   

    start_time = time.time()
    best_fitness_per_gen = []
    conflicts_per_gen = []
    
    populatie = [cromozom() for _ in range(MARIME_POPULATIE)]
    
    for gen in range(NUMAR_GENERATII):
        fitnessCalc = {id(ind): calculeaza_fitness(ind) for ind in populatie}
        populatie.sort(key=lambda x: fitnessCalc[id(x)], reverse=True)
        best_f = fitnessCalc[id(populatie[0])]
        best_fitness_per_gen.append(best_f)

        # Numara conflictele
        best_ind = populatie[0]
        conflicts = 0
        for i in range(len(best_ind)):
            for j in range(i + 1, len(best_ind)):
                l1, l2 = best_ind[i], best_ind[j]
                if (l1[3] < l2[4]) and (l2[3] < l1[4]):
                    if l1[1] == l2[1] or l1[2] == l2[2]:
                        conflicts += 1
        conflicts_per_gen.append(conflicts)
        
        # Evolutie
        nrElit = 4
        nouaGen = populatie[:nrElit]
        
        while len(nouaGen) < MARIME_POPULATIE:
            tata = selectie_turneu(populatie, fitnessCalc)
            mama = selectie_turneu(populatie, fitnessCalc)
            copil = recombinare(tata, mama)
            copil = mutatie(copil)
            nouaGen.append(copil)
        
        populatie = nouaGen
        
        # Progress update
        step = max(1, NUMAR_GENERATII // 10)
        if (gen + 1) % step == 0 or gen == 0:
            print(f"  Gen {gen+1:5d}/{NUMAR_GENERATII}: Fitness={best_f:6.2f}, Conflicts={conflicts}")
    
    best_orar = populatie[0]
    best_fitness = fitnessCalc[id(populatie[0])]
    
    end_time = time.time()
    durata = end_time - start_time
    
    # Afisare statistici
    print("\n" + "="*70)
    print("STATISTICI BENCHMARK")
    print("="*70)
    print(f"Timp executie:              {durata:.2f} sec ({durata/60:.1f} min)")
    print(f"Timp per generatie:         {(durata/NUMAR_GENERATII)*1000:.2f} ms")
    print(f"Fitness initial:            {best_fitness_per_gen[0]:.2f}")
    print(f"Fitness final:              {best_fitness:.2f}")
    print(f"Imbunatatire:               +{(best_fitness - best_fitness_per_gen[0]):.2f} ({((best_fitness/best_fitness_per_gen[0] - 1) * 100):.1f}%)")
    print(f"Conflicte initiale:         {conflicts_per_gen[0]}")
    print(f"Conflicte finale:           {conflicts_per_gen[-1]}")
    
    conflict_free = [i for i, c in enumerate(conflicts_per_gen) if c == 0]
    if conflict_free:
        print(f"Prima solutie fara conflict: Gen {conflict_free[0]}")
    else:
        print(f"Solutii fara conflicte:     Nicio solutie gasita")
    
    print("="*70)
    
    return best_orar, best_fitness

if __name__ == "__main__":
    best_orar, fitness = ruleaza_cu_benchmark()
    afiseaza_orar(best_orar, fitness)
