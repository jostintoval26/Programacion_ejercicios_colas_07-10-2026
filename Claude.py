import queue
import random
from faker import Faker

fake = Faker('es_ES')

MAX_PACIENTES = 100
TIEMPO_REGISTRO = 1.3
RANGO_MED_GEN = (4, 8)          # la consulta de medicina general dura entre 4 y 8 s (al azar)
TIEMPO_ESPECIALISTA = 5.12

doctores = {
    "General": {
        "MedicoGen_DrCruz": queue.Queue(maxsize=10),
        "MedicoGen_DREspinoza": queue.Queue(maxsize=10),
        "MedicoGen_DrMeza": queue.Queue(maxsize=10),
    },
    "Especialista": {
        "Ortopedia_DrPrado": queue.Queue(maxsize=4),
        "Ginecologia_DrPerez": queue.Queue(maxsize=4),
        "Internista_DrManzanares": queue.Queue(maxsize=4),
    },
}

atendidos = {
    dr: 0 for cat in doctores.values() for dr in cat
}
tiempo_ocupado = {dr: 0.0 for dr in atendidos}     # segundos totales que trabajo cada doctor
tiempos_registro = []
tiempos_atencion = {"General": [], "Especialista": []}
rechazados = 0


def duracion_consulta(servicio):
    if servicio == "General":
        return random.uniform(*RANGO_MED_GEN)
    return TIEMPO_ESPECIALISTA


print("         === Bienvenido a SERMESA ===")

for paciente_id in range(1, MAX_PACIENTES + 1):
    nombre = f"{fake.first_name()} {fake.last_name()}"
    servicio = random.choice(["General", "Especialista"])
    salas = doctores[servicio]

    # Sala con menos pacientes; si empatan, el que ha atendido menos
    mejor_dr = min(salas.keys(), key=lambda dr: (salas[dr].qsize(), atendidos[dr]))

    if not salas[mejor_dr].full():
        tiempos_registro.append(TIEMPO_REGISTRO)
        salas[mejor_dr].put(nombre)

        # Simulacion de cuando se atiende: sale de cola, dura su tiempo y se suma a atendidos
        paciente = salas[mejor_dr].get()
        duracion = duracion_consulta(servicio)
        atendidos[mejor_dr] += 1
        tiempo_ocupado[mejor_dr] += duracion
        tiempos_atencion[servicio].append(duracion)
        print(f"  {mejor_dr} atendio a {paciente} (duro {duracion:.2f} s)")
    else:
        rechazados += 1


def promedio(lista):
    return sum(lista) / len(lista) if lista else 0


print("\n       --- Resultados Final ---")
print("  Atendidos por doctor:")
for dr, cant in atendidos.items():
    print(f"  {dr}: {cant} pacientes, {tiempo_ocupado[dr]:.2f} s trabajando")

print(f"\nTiempo promedio registro: {promedio(tiempos_registro):.2f} s")
g = tiempos_atencion["General"]
print(f"Tiempo promedio atencion General: {promedio(g):.2f} s (min {min(g):.2f} s, max {max(g):.2f} s)")
print(f"Tiempo promedio atencion Especialista: {promedio(tiempos_atencion['Especialista']):.2f} s")
print(
    f"\nSaturacion: Limite de 10 por sala. Pacientes no admitidos: {rechazados}"
)