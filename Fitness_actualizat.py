def calculeaza_fitness(orar):
    penalizare_conflicte = 0
    penalizare_ineficienta = 0
    
    # 1. Calculăm suprapunerile
    for i in range(len(orar)):
        for j in range(i + 1, len(orar)):
            l1, l2 = orar[i], orar[j]
            # Suprapunere timp
            if (l1[3] < l2[4]) and (l2[3] < l1[4]):
                if l1[1] == l2[1]: penalizare_conflicte += 100 # Conflict Elevator
                if l1[2] == l2[2]: penalizare_conflicte += 100 # Conflict Mecanic

    # 2. Luam in calcul pauzele si gap-urile dintre lucrarile mecanicilor
    
    # Grupăm lucrările pe fiecare mecanic ca să îi analizăm programul
    program_mecanici = {0: [], 1: [], 2: []} # Presupunem 3 mecanici (0, 1, 2)
    
    for gena in orar:
        id_mecanic = gena[2]
        program_mecanici[id_mecanic].append(gena)
        
    for m_id, lucrari in program_mecanici.items():
        if not lucrari: continue # Mecanicul nu are nicio lucrare
        
        # Le sortăm cronologic după ora de start
        lucrari.sort(key=lambda x: x[3])
        
        # A. Penalizare: Nu începe la prima oră (Slot 0)
        prima_lucrare_start = lucrari[0][3]
        if prima_lucrare_start > 0:
            # Penalizam fiecare slot de timp cu 2 puncte
            penalizare_ineficienta += prima_lucrare_start * 2
            
        # B. Penalizare: Pauze între lucrări
        for k in range(len(lucrari) - 1):
            timp_final_curenta = lucrari[k][4]
            timp_start_urmatoare = lucrari[k+1][3]
            
            pauza = timp_start_urmatoare - timp_final_curenta
            
            if pauza > 0:
                # Fiecare slot de pauză se penalizează cu 1 punct
                penalizare_ineficienta += pauza * 1

    # Fitness-ul final
    total_penalizare = penalizare_conflicte + penalizare_ineficienta
    
    return 1 / (1 + total_penalizare)