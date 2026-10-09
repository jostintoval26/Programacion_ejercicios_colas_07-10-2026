import queue
import random
import time
from faker import Faker

fake = Faker('es_ES')

TOTAL_LLEGADAS = 120        # Pacientes que llegan 
CUPOS_MAX = 100           # cuantos se admiten como maximo, el resto queda no admitido
TIEMPO_LLEGADA = 0.2        # cada cuanto llega un paciente
TIEMPO_REGISTRO = 1.3
RANGO_MED_GEN = (4, 8)      # la consulta general dura entre 4 y 8 s (al azar)
TIEMPO_ESPECIALISTA = 5.12
PUESTOS_REGISTRO = 2        # Entre más puestos, mas pacientes pueden registrarse al mismo tiempo lo que permite que las filas de dr tengan mas pacientes y se pueda medir mejor la saturación de las salas.
FACTOR_TIEMPO = 0           # 0 = sin esperar | 0.1 = 10x mas rapido | 1 = tiempo real


def convetir_a_entero(segundos):
    return round(segundos * 100)


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

atendidos = {doctor: 0 for categoria in doctores.values() for doctor in categoria}
fila_maxima = {doctor: 0 for doctor in atendidos}
consulta = {doctor: None for doctor in atendidos}      # paciente que esta en consulta ahora
fin_consulta = {doctor: 0 for doctor in atendidos}     # cuando termina esa consulta

mostrador = queue.Queue(maxsize=100)
puestos = [None] * PUESTOS_REGISTRO            # cada puesto: {"paciente":..., "fin":...} o None

admitidos = 0
rechazados_cupo = 0          # llegaron cuando ya se habia llenado el cupo diario
rechazados_mostrador = 0     # habia cupo, pero el mostrador estaba lleno en ese momento
bloqueos = 0
tiempos_registro = []
tiempos_total = {"General": [], "Especialista": []}
tiempos_atencion = {"General": [], "Especialista": []}   # duracion de cada consulta

print("         === Bienvenido a SERMESA ===")

reloj = 0
llegados = 0
terminados = 0
proxima_llegada = 0

while terminados + rechazados_cupo + rechazados_mostrador < TOTAL_LLEGADAS:

    # 1) Llegada
    if llegados < TOTAL_LLEGADAS and reloj >= proxima_llegada:
        llegados += 1
        nombre = f"{fake.first_name()} {fake.last_name()}"
        if admitidos >= CUPOS_MAX:
            rechazados_cupo += 1
            print(f"[{reloj/100:7.2f}s] Cupo maximo alcanzado, no se admite a {nombre}")
        else:
            try:
                mostrador.put_nowait({"nombre": nombre, "llegada": reloj})
                admitidos += 1
            except queue.Full:
                rechazados_mostrador += 1
                print(f"[{reloj/100:7.2f}s] Mostrador lleno, se rechaza a {nombre}")
        proxima_llegada = reloj + convetir_a_entero(TIEMPO_LLEGADA)

    # 2) Registro (dura TIEMPO_REGISTRO por paciente)
    for i in range(PUESTOS_REGISTRO):
        if puestos[i] is None and not mostrador.empty():
            puestos[i] = {"paciente": mostrador.get(), "fin": reloj + convetir_a_entero(TIEMPO_REGISTRO)}

        if puestos[i] is not None and reloj >= puestos[i]["fin"]:
            p = puestos[i]["paciente"]
            if "servicio" not in p:   # al terminar el registro se decide: General o Especialista
                p["servicio"] = random.choice(["General", "Especialista"])
            salas = doctores[p["servicio"]]

            # sala mas libre (fila + en consulta); si empatan, el que ha atendido menos
            libres = [doctor for doctor in salas if not salas[doctor].full()]
            if libres:
                mejor_doctor = min(libres, key=lambda dr: (salas[dr].qsize() + (consulta[dr] is not None), atendidos[dr]))
                salas[mejor_doctor].put(p)
                fila_maxima[mejor_doctor] = max(fila_maxima[mejor_doctor], salas[mejor_doctor].qsize())
                tiempos_registro.append(reloj - p["llegada"])
                puestos[i] = None
            elif not p.get("avisado"):   
                p["avisado"] = True
                bloqueos += 1
                print(f"[{reloj/100:7.2f}s] Salas de {p['servicio']} llenas, {p['nombre']} espera en registro...")

    # 3) Doctores
    for categoria, salas in doctores.items():
        for doctor, sala in salas.items():
            if consulta[doctor] is not None and reloj >= fin_consulta[doctor]:
                p = consulta[doctor]
                tiempos_total[categoria].append(reloj - p["llegada"])
                atendidos[doctor] += 1
                terminados += 1
                consulta[doctor] = None
            if consulta[doctor] is None and not sala.empty():
                consulta[doctor] = sala.get()     # FIFO: el primero en entrar es el primero en atenderse
                if categoria == "General":
                    duracion = convetir_a_entero(random.uniform(*RANGO_MED_GEN))
                else:
                    duracion = convetir_a_entero(TIEMPO_ESPECIALISTA)
                fin_consulta[doctor] = reloj + duracion
                tiempos_atencion[categoria].append(duracion)
                # sala.qsize() = cuantos quedan esperando justo cuando empieza esta consulta
                print(f"[{reloj/100:7.2f}s] {doctor} atiende a {consulta[doctor]['nombre']} "
                      f"(dura {duracion/100:.2f} s, en fila: {sala.qsize()})")

    # 4) Avanza el reloj
    if FACTOR_TIEMPO:
        time.sleep(0.01 * FACTOR_TIEMPO)
    reloj += 1


def promedio(lista):
    return sum(lista) / len(lista) / 100 if lista else 0


print("\n       --- Resultados Final ---")
print(f"Tiempo total de la simulacion: {reloj/100:.2f} s\n")
print(f"Pacientes que llegaron: {llegados}")
print(f"Pacientes admitidos: {admitidos}")
print(f"Pacientes atendidos: {terminados}\n")
print("Atendidos por doctor:")
for doctor, cantidad in atendidos.items():
    print(f"  {doctor}: {cantidad}  (Maximo que tuvo en la fila: {fila_maxima[doctor]})")

print(f"\nTiempo promedio en registro: {promedio(tiempos_registro):.2f} s")
print(f"Tiempo promedio de consulta General: {promedio(tiempos_atencion['General']):.2f} s")
print(f"Tiempo promedio de consulta Especialista: {promedio(tiempos_atencion['Especialista']):.2f} s")
print(f"Tiempo promedio General (entre llegadar y finalizar consulta): {promedio(tiempos_total['General']):.2f} s")
print(f"Tiempo promedio Especialista (entre llegadar y finalizar consulta): {promedio(tiempos_total['Especialista']):.2f} s")
print(f"\nSaturacion: Pacientes no admitidos: {rechazados_cupo}")
print(f"Pacientes no admitidos por mostrador lleno: {rechazados_mostrador}")
print(f"Veces que el registro quedo bloqueado por salas llenas: {bloqueos}")