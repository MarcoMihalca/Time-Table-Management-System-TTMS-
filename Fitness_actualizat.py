MAX_TIMP = 40  # 5 zile x 8 ore

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
        
        # E. BONUS pentru finishing timpuriu
        timp_liber_final = MAX_TIMP - ultimul_final
        bonus_eficienta += timp_liber_final * 3

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
        
        # BONUS MASIV pentru finalizare rapidă
        timp_economisit = MAX_TIMP - timp_finalizare_totala
        bonus_eficienta += timp_economisit * 15
        
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