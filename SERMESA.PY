import queue
import random
from faker import Faker

fake = Faker('es_ES')

MAX_PACIENTES = 100
TIEMPO_REGISTRO = 1.3
TIEMPO_MED_GEN = 4.8
TIEMPO_ESPECIALISTA = 5.12

doctores = {
    "General": {
        "Medicina General - Dr. Cruz": queue.Queue(maxsize=10),
        "Medicina General - Dr. Espinoza": queue.Queue(maxsize=10),
        "Medicina General - Dr. Meza": queue.Queue(maxsize=10),
    },
    "Especialista": {
        "Ortopedia - Dr. Prado": queue.Queue(maxsize=4),
        "Ginecologia - Dr. Perez": queue.Queue(maxsize=4),
        "Internista - Dr. Manzanares": queue.Queue(maxsize=4),
    },
}

atendidos = {
    dr: 0 for cat in doctores.values() for dr in cat
}
rechazados = 0

print("         === Bienvenido a SERMESA ===")

for paciente_id in range(1, MAX_PACIENTES + 1):
    nombre = f"{fake.first_name()} {fake.last_name()}"
    servicio = random.choice(["General", "Especialista"])
    salas = doctores[servicio]

    # Sala con menos pacientes; si empatan, el que ha atendido menos
    mejor_dr = min(salas.keys(), key=lambda dr: (salas[dr].qsize(), atendidos[dr]))

    if not salas[mejor_dr].full():
        salas[mejor_dr].put(nombre)
        # Simulacion de cuando se atiende, se sale de cola y se suma a atendidos
        paciente = salas[mejor_dr].get()
        atendidos[mejor_dr] += 1
        print(f"  {mejor_dr} atendio a {paciente}  (En la fila: {salas[mejor_dr].qsize()})")
    else:
        rechazados += 1

print("\n       --- Resultados Final ---")
print("  Atendidos por doctor:")
for dr, cant in atendidos.items():
    print(f"  {dr}: {cant}")

print(f"\nTiempo promedio registro: {TIEMPO_REGISTRO} s")
print(f"Tiempo promedio atencion General: {TIEMPO_MED_GEN} s")
print(f"Tiempo promedio atencion Especialista: {TIEMPO_ESPECIALISTA} s")
print(
    f"\nSaturacion: Limite de 10 por sala. Pacientes no admitidos: {rechazados}"
)