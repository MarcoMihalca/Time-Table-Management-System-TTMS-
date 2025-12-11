import random
# Definim lucrările service-ului
# Durata 1 = 1 oră (5 zile x 8 ore = 40 ore totale)
LUCRARI_DB = [
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

# Resursele disponibile
NUMAR_LUCRARI = len(LUCRARI_DB)
NUMAR_ELEVATOARE = 3
NUMAR_MECANICI = 3
MAX_TIMP = 40  # 5 zile x 8 ore/zi = 40 ore totale

# Parametrii algoritmului
MARIME_POPULATIE = 50
NUMAR_GENERATII = 2000
SANSA_MUTATIE = 0.3  # 30% sansa sa modificăm o lucrare

# Generam gene si indivizi
def genereaza_o_programare(id_lucrare):
    """
    Creează o alocare validă pentru o singură lucrare.
    Alege un mecanic, un elevator și o oră care să încapă în program.
    ВАЖНО: Lucrarea trebuie să se încheie în aceeași zi (nu poate trece peste noapte).
    """
    lucrare = LUCRARI_DB[id_lucrare]
    durata = lucrare["durata"]
    
    # Alegem o zi random (0-4: Luni-Vineri)
    zi = random.randint(0, 4)
    zi_start_slot = zi * 8  # Ora 09:00 a zilei respective
    zi_end_slot = (zi + 1) * 8  # Ora 17:00 (finalul zilei)
    
    # Calculăm ora de start maximă astfel încât lucrarea să se încheie în aceeași zi
    ore_disponibile_in_zi = 8  # 09:00 - 17:00
    if durata > ore_disponibile_in_zi:
        # Dacă lucrarea e prea lungă pentru o zi, o împărțim pe mai multe zile
        # dar pentru simplitate, o punem să înceapă la 09:00
        start = zi_start_slot
        final = start + durata
    else:
        # Lucrarea încape într-o singură zi
        start_maxim_in_zi = zi_end_slot - durata
        start = random.randint(zi_start_slot, start_maxim_in_zi)
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
    Funcție fitness optimizată pentru:
    - Zero conflicte (elevator & mecanic)
    - Timp minim pierdut (fără gap-uri)
    - Maximum lucrări în minimum timp
    """
    penalizare_conflicte = 0
    penalizare_timp_pierdut = 0
    bonus_eficienta = 0
    bonus_compactitate = 0
    
    # 1. CONFLICTE CRITICE - Trebuie eliminate complet
    for i in range(len(orar)):
        for j in range(i + 1, len(orar)):
            l1, l2 = orar[i], orar[j]
            # Verificăm suprapunere în timp
            if (l1[3] < l2[4]) and (l2[3] < l1[4]):
                # Conflict Elevator - PENALIZARE MASIVĂ
                if l1[1] == l2[1]: 
                    penalizare_conflicte += 500
                # Conflict Mecanic - PENALIZARE MASIVĂ  
                if l1[2] == l2[2]: 
                    penalizare_conflicte += 500

    # 2. ANALIZA MECANICI - Compactitate & Eficiență
    program_mecanici = {0: [], 1: [], 2: []}
    
    for gena in orar:
        id_mecanic = gena[2]
        program_mecanici[id_mecanic].append(gena)
    
    total_lucrari_efectuate = 0
    mecanic_activi = 0
    
    for m_id, lucrari in program_mecanici.items():
        if not lucrari: 
            continue
        
        mecanic_activi += 1
        total_lucrari_efectuate += len(lucrari)
        
        # Sortăm cronologic
        lucrari.sort(key=lambda x: x[3])
        
        primul_start = lucrari[0][3]
        ultimul_final = lucrari[-1][4]
        
        # A. Penalizare SEVERĂ pentru start târziu
        if primul_start > 0:
            penalizare_timp_pierdut += primul_start * 10
            
        # B. Penalizare SEVERĂ pentru gap-uri
        total_gaps = 0
        for k in range(len(lucrari) - 1):
            gap = lucrari[k+1][3] - lucrari[k][4]
            if gap > 0:
                penalizare_timp_pierdut += gap * 8
                total_gaps += gap
        
        # C. BONUS MAJOR pentru program compact (fără gap-uri)
        timp_ocupat_efectiv = sum(l[4] - l[3] for l in lucrari)
        interval_total = ultimul_final - primul_start
        
        if interval_total > 0:
            densitate = timp_ocupat_efectiv / interval_total
            # Densitate 1.0 = perfect compact (fără gap-uri)
            bonus_compactitate += densitate * 100
        
        # D. BONUS pentru start devreme
        if primul_start == 0:
            bonus_eficienta += 50
        
        # E. Penalizare pentru ore pierdute la sfârșitul fiecărei zile
        # Găsim toate zilele în care mecanicul lucrează
        zile_active = set()
        for l in lucrari:
            zi_start = l[3] // 8
            zi_final = l[4] // 8
            zile_active.add(zi_start)
            if zi_final != zi_start:
                zile_active.add(zi_final)
        
        for zi in zile_active:
            # Lucrări care se termină în acea zi
            lucrari_terminand_in_zi = [l for l in lucrari if l[4] // 8 == zi]
            if lucrari_terminand_in_zi:
                # Găsim când se termină ultima lucrare din acea zi
                max_final_in_zi = max(l[4] for l in lucrari_terminand_in_zi)
                sfarsit_zi = (zi + 1) * 8  # Ora 17:00
                
                ore_pierdute = sfarsit_zi - max_final_in_zi
                if ore_pierdute > 0 and ore_pierdute < 8:
                    # Penalizare SEVERĂ pentru ore pierdute la sfârșit de zi
                    penalizare_timp_pierdut += ore_pierdute * 8
        
        # F. BONUS MASIV pentru terminare cât mai devreme în săptămână
        ultima_zi = ultimul_final // 8
        zile_economisate = 4 - ultima_zi  # 4 = Vineri (0=Luni, 1=Marti, 2=Miercuri, 3=Joi, 4=Vineri)
        if zile_economisate > 0:
            # Recompensă mare dacă termină Luni/Marți/Miercuri/Joi în loc de Vineri
            bonus_eficienta += zile_economisate * 100
        
        # G. BONUS pentru terminare la sfârșit de zi (program compact)
        if ultimul_final % 8 == 0:
            bonus_eficienta += 30

    # 3. ANALIZA ELEVATOARE - Utilizare intensă
    program_elevatoare = {0: [], 1: [], 2: []}
    
    for gena in orar:
        id_elevator = gena[1]
        program_elevatoare[id_elevator].append(gena)
    
    for e_id, lucrari in program_elevatoare.items():
        if not lucrari:
            continue
            
        lucrari.sort(key=lambda x: x[3])
        
        # Penalizare pentru gap-uri elevator
        for k in range(len(lucrari) - 1):
            gap = lucrari[k+1][3] - lucrari[k][4]
            if gap > 0:
                penalizare_timp_pierdut += gap * 3
        
        # BONUS pentru utilizare intensă
        bonus_eficienta += len(lucrari) * 10

    # 4. METRICI GLOBALE - Finishing în timp minim
    if orar:
        # Timpul când se termină ULTIMA lucrare
        timp_finalizare_totala = max(gena[4] for gena in orar)
        ultima_zi_global = timp_finalizare_totala // 8
        
        # BONUS URIAȘ pentru finalizare înainte de Vineri
        # 0=Luni, 1=Marți, 2=Miercuri, 3=Joi, 4=Vineri
        zile_economisate_global = 4 - ultima_zi_global
        if zile_economisate_global > 0:
            bonus_eficienta += zile_economisate_global * 200
        
        # BONUS pentru finalizare în ore
        ore_economisate_in_ultima_zi = ((ultima_zi_global + 1) * 8) - timp_finalizare_totala
        bonus_eficienta += ore_economisate_in_ultima_zi * 10
        
        # BONUS EXTRA pentru toate lucrările
        bonus_eficienta += total_lucrari_efectuate * 30
        
        # BONUS pentru distribuție echilibrată (3 mecanici activi)
        if mecanic_activi == 3:
            bonus_eficienta += 100

    # 5. CALCUL FINAL - Normalizat la scală 1-100
    total_penalizare = penalizare_conflicte + penalizare_timp_pierdut
    total_bonus = bonus_eficienta + bonus_compactitate
    
    # Scor brut
    if total_penalizare == 0:
        # Perfect: scor maxim
        scor_brut = 1000 + total_bonus
    else:
        # Cu penalizări
        scor_brut = total_bonus / (1 + total_penalizare * 0.01)
    
    # Normalizare la 1-100
    # Scor maxim teoretic: ~2000-3000 (perfect schedule)
    # Scor minim: ~10-50 (conflicte majore)
    scor_normalizat = min(100, max(1, (scor_brut / 30)))
    
    return scor_normalizat

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

print("\n" + "="*80)
print(f"REZULTAT FINAL (Fitness: {nota_finala:.2f}/100)")
if nota_finala >= 95:
    print("STATUS: ★★★ PERFECT! Orar optim fără conflicte.")
elif nota_finala >= 80:
    print("STATUS: ★★ EXCELENT! Orar eficient.")
elif nota_finala >= 60:
    print("STATUS: ★ BUN. Poate fi îmbunătățit.")
else:
    print("STATUS: ✗ Conflicte sau ineficiențe majore.")
print("="*80)

def ora_to_string(slot):
    """Convertește slot-ul în format Zi-Ora (ex: Luni 09:00)"""
    zi = slot // 8
    ora_in_zi = slot % 8
    zile = ["Luni", "Marti", "Miercuri", "Joi", "Vineri"]
    if zi >= len(zile):
        zi = len(zile) - 1  # Capăm la Vineri dacă depășește
    return f"{zile[zi]} {9+ora_in_zi:02d}:00"

def get_zi_index(slot):
    """Returnează indexul zilei pentru sortare"""
    return slot // 8

# Sortăm după zi și apoi după ora de start
cel_mai_bun_orar_sortat = sorted(cel_mai_bun_orar, key=lambda x: (get_zi_index(x[3]), x[3]))

print(f"{'LUCRARE':<20} | {'ELEVATOR':<10} | {'MECANIC':<10} | {'INTERVAL':<30}")
print("-" * 80)

zi_curenta = -1
for programare in cel_mai_bun_orar_sortat:
    id_l = programare[0]
    nume = LUCRARI_DB[id_l]["nume"]
    elev = programare[1]
    mec = programare[2]
    start, final = programare[3], programare[4]
    
    # Adăugăm separator între zile
    zi = get_zi_index(start)
    if zi != zi_curenta:
        if zi_curenta != -1:
            print("-" * 80)
        zile = ["LUNI", "MARTI", "MIERCURI", "JOI", "VINERI"]
        print(f"\n>>> {zile[zi]} <<<")
        zi_curenta = zi
    
    interval = f"{ora_to_string(start)} -> {ora_to_string(final)}"
    print(f"{nume:<20} | E{elev:<9} | M{mec:<9} | {interval}")