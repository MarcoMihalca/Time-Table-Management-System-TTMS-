import random

MECANICI = ["Mecanic A", "Mecanic B", "Mecanic C"]
ELEVATOARE = ["Elevator 1", "Elevator 2"]

# 2 sloturi = 1 ora
LUCRARI = [
    {"nume": "Schimb Ulei",   "durata": 2}, 
    {"nume": "Distribuție",   "durata": 4},
    {"nume": "Diagnoză",      "durata": 1},
    {"nume": "Plăcuțe Frână", "durata": 3}
]

MAX_TIMP = 16  # 8 ore de lucru * 2 = 16 sloturi

def creeaza_orar_random():
    orar = []
    
    for lucrare in LUCRARI:
        mecanic_ales = random.choice(MECANICI)
        elevator_ales = random.choice(ELEVATOARE)
    
        timp_ramas = MAX_TIMP - lucrare["durata"]
        
        start = random.randint(0, timp_ramas)
        final = start + lucrare["durata"]
        
        programare = {
            "lucrare": lucrare["nume"],
            "mecanic": mecanic_ales,
            "elevator": elevator_ales,
            "start": start,
            "final": final
        }
        orar.append(programare)
        
    return orar

print("--- GENERARE POPULAȚIE INIȚIALĂ (3 Orare Aleatorii) ---\n")

for i in range(3):
    print(f"PROPUNEREA DE ORAR #{i + 1}:")
    
    orar_generat = creeaza_orar_random()
    
    for p in orar_generat:
        # Facem conversie de la sloturi la ore reale
        # Slot 0 = 8:00
        ora_reala_start = 8 + (p['start'] / 2)
        ora_reala_final = 8 + (p['final'] / 2)
        
        print(f"- {p['lucrare']}: {p['mecanic']} pe {p['elevator']} "
              f"(Ora {ora_reala_start} -> {ora_reala_final})")
    
    print("-" * 40)