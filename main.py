import random
# Definim lucrările service-ului
# Durata 1 = 30 minute
LUCRARI_DB = [
    {"id": 0, "nume": "Schimb Ulei",   "durata": 2},
    {"id": 1, "nume": "Frane Fata",    "durata": 4},
    {"id": 2, "nume": "Schimb Roti",   "durata": 2},
    {"id": 3, "nume": "Motor General", "durata": 6},
    {"id": 4, "nume": "Reglaj Faruri", "durata": 1},
    {"id": 5, "nume": "Inspectie ITP", "durata": 3}
]

# Resursele disponibile
NUMAR_LUCRARI = len(LUCRARI_DB)
NUMAR_ELEVATOARE = 3
NUMAR_MECANICI = 3
MAX_TIMP = 16  # Programul are 16 de sloturi (9:00 - 17:00)

# Parametrii algoritmului
MARIME_POPULATIE = 20
NUMAR_GENERATII = 50000
SANSA_MUTATIE = 0.2  # 20% sansa sa modificăm o lucrare

# Generam gene si indivizi
def genereaza_o_programare(id_lucrare):
    """
    Creează o alocare validă pentru o singură lucrare.
    Alege un mecanic, un elevator și o oră care să încapă în program.
    """
    lucrare = LUCRARI_DB[id_lucrare]
    durata = lucrare["durata"]
    
    # Alegem o oră de start random, dar sa nu depasim finalul zilei
    start_maxim_posibil = MAX_TIMP - durata
    start = random.randint(0, start_maxim_posibil)
    final = start + durata
    
    elevator = random.randint(0, NUMAR_ELEVATOARE - 1)
    mecanic = random.randint(0, NUMAR_MECANICI - 1)
    
    # Returnam o lista care reprezinta gena individului
    return [id_lucrare, elevator, mecanic, start, final]

def genereaza_un_orar_complet():
    """
    Un individ (in cazul nostru un orar) este o listă cu programarile pentru TOATE lucrarile.
    """
    orar = []
    for i in range(NUMAR_LUCRARI):
        programare = genereaza_o_programare(i)
        orar.append(programare)
    return orar

#  Calculam functia de fitness
def calculeaza_fitness(orar):
    """
    Verifică dacă există greșeli (suprapuneri).
    Cu cât sunt mai puține greșeli, cu atât nota e mai mare.
    """
    penalizare = 0

    # Comparăm fiecare lucrare cu toate celelalte
    for i in range(len(orar)):
        for j in range(i + 1, len(orar)):
            lucrare1 = orar[i]
            lucrare2 = orar[j]
            
            # Verificăm daca se suprapun în timp
            start1, final1 = lucrare1[3], lucrare1[4]
            start2, final2 = lucrare2[3], lucrare2[4]
            
            se_suprapun_timp = (start1 < final2) and (start2 < final1)
            
            if se_suprapun_timp:
                # Daca se suprapun, verificăm dacă folosesc aceleași resurse
                elevator1, elevator2 = lucrare1[1], lucrare2[1]
                mecanic1, mecanic2 = lucrare1[2], lucrare2[2]
                
                if elevator1 == elevator2:
                    penalizare += 10  # Greșeală majora: Elevator dublat
                if mecanic1 == mecanic2:
                    penalizare += 10  # Greșeală majora: Mecanic dublat

    # Formula: 1 împărțit la (1 + greșeli).
    # 0 greșeli => Fitness 1.0 (Perfect)
    # Multe greșeli => Fitness cu atat mai aproape de 0.0
    return 1 / (1 + penalizare)

# Operatorii genetici

# Selectia indivizilor pentru procesul de generare a restul populatiei / generatiilor
def selectie_turneu(populatie):
    """ Alege 2 orare la întâmplare și îl returnează pe cel mai bun. """
    candidat1 = random.choice(populatie)
    candidat2 = random.choice(populatie)
    
    if calculeaza_fitness(candidat1) > calculeaza_fitness(candidat2):
        return candidat1
    else:
        return candidat2

def recombinare(parinte1, parinte2):
    """ Combină jumatate din orarul Parintelui 1 cu jumătate din orarul Parintelui 2. """
    punct_taiere = random.randint(1, NUMAR_LUCRARI - 1)
    copil = parinte1[:punct_taiere] + parinte2[punct_taiere:]
    return copil

def mutatie(orar):
    """ 
    Are o șansă mică să reprogrameze complet o lucrare din orar.
    Asta ajută daca algoritmul se blocheaza in minime locale.
    """
    orar_nou = list(orar) # Facem o copie ca să nu stricam originalul
    
    for i in range(len(orar_nou)):
        sansa = random.random()
        
        if sansa < SANSA_MUTATIE:
            # Reprogramăm lucrarea 'i' de la zero (altă oră, alt mecanic)
            id_lucrare = orar_nou[i][0]
            orar_nou[i] = genereaza_o_programare(id_lucrare)
            
    return orar_nou


# Algoritmul principal
def ruleaza_algoritm_genetic():
    # 1. Creăm populația initiala (20 de orare aleatorii)
    populatie = [genereaza_un_orar_complet() for _ in range(MARIME_POPULATIE)]

    print("Start Evoluție: ", NUMAR_GENERATII, "generații...")

    for generatie in range(NUMAR_GENERATII):
        
        # Sortam orarele de la cel mai bun la cel mai slab
        populatie.sort(key=lambda x: calculeaza_fitness(x), reverse=True)
        
        # ELITISM: Păstrăm primii 2 cei mai buni (10% din 20)
        nr_elite = 2
        noua_generatie = populatie[:nr_elite]

        # Restul de 18 ii creăm prin împerechere
        while len(noua_generatie) < MARIME_POPULATIE:
            # Alegem doi părinți
            tata = selectie_turneu(populatie)
            mama = selectie_turneu(populatie)
            
            # Facem un copil
            copil = recombinare(tata, mama)
            
            # Aplicăm mutatia
            copil = mutatie(copil)
            
            noua_generatie.append(copil)

        # Trecem la generația următoare
        populatie = noua_generatie

    # La final, îl returnam pe cel mai bun (primul din listă, deoarece este sortată)
    return populatie[0]

# Rezultatele finale
cel_mai_bun_orar = ruleaza_algoritm_genetic()
nota_finala = calculeaza_fitness(cel_mai_bun_orar)

print("\n" + "="*50)
print(f"REZULTAT FINAL (Fitness: {nota_finala:.4f})")
if nota_finala == 1.0:
    print("STATUS: PERFECT! Nu avem suprapuneri.")
else:
    print("STATUS: Mai sunt conflicte.")
print("="*50)

print(f"{'LUCRARE':<15} | {'ELEVATOR':<10} | {'MECANIC':<10} | {'ORELE (Sloturi)'}")
print("-" * 55)

for programare in cel_mai_bun_orar:
    id_l = programare[0]
    nume = LUCRARI_DB[id_l]["nume"]
    elev = programare[1]
    mec = programare[2]
    start, final = programare[3], programare[4]
    
    print(f"{nume:<15} | E{elev:<9} | M{mec:<9} | {start:02d} -> {final:02d}")