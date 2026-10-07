import queue

# Ejercicio 1.
#ventanilla = queue.Queue(maxsize=3)

#ventanilla.put("Cliente 1: Ana")
#ventanilla.put("Cliente 2: Carlos")
#ventanilla.put("Cliente 3: Elena")

#print(f"Tamano de la cola: {ventanilla.qsize()}")

#while not ventanilla.empty():
#    atentido = ventanilla.get()
#    print(f"    Atendiendo a: {atentido}")
#    ventanilla.task_done()


# Ejercicio 2
urgencias = queue.PriorityQueue()
urgencias.put((3, "Reporte de rutina"))
urgencias.put((1, "Falla critica en servidor principal."))
urgencias.put((2, "Actualizacion de software."))

print("--- Procesando Tickets de soporte ---")

while not urgencias.empty():
    prioridad, tarea = urgencias.get()
    print(f"Prioridad [{prioridad}] -> {tarea}")
    urgencias.task_done()