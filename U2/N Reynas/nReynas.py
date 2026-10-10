import random
import time

# Tablero

def crear_tablero_aleatorio(n):
    """Crea un tablero con las filas en orden revuelto."""
    tablero = list(range(n))
    random.shuffle(tablero)
    return tablero


def contar_ataques(tablero):
    """Cuenta cuántas parejas de reinas están en la misma diagonal."""
    ataques = 0

    for col_a in range(len(tablero)):
        for col_b in range(col_a + 1, len(tablero)):
            # Cuántas columnas separan a las dos reinas
            distancia_horizontal = col_b - col_a
            # Cuántas filas las separan
            distancia_vertical = abs(tablero[col_a] - tablero[col_b])

            # Si se separan igual en horizontal y vertical,
            # están en una diagonal y se atacan.
            if distancia_horizontal == distancia_vertical:
                ataques += 1

    return ataques


def dibujar_tablero(tablero):
    """Muestra el tablero en pantalla: R = reina, punto = casilla vacía."""
    n = len(tablero)
    for fila in range(n):
        linea = ""
        for columna in range(n):
            if tablero[columna] == fila:
                linea += "R "
            else:
                linea += ". "
        print(linea)


# Vecinos (los tableros a los que podemos "movernos")
# Un movimiento consiste en intercambiar las filas de dos columnas.
# Con 8 columnas hay 28 intercambios posibles.

def intercambiar(tablero, col_a, col_b):
    """Devuelve una COPIA del tablero con dos columnas intercambiadas."""
    copia = tablero[:]
    guardado = copia[col_a]
    copia[col_a] = copia[col_b]
    copia[col_b] = guardado
    return copia


def generar_vecinos(tablero):
    """Genera todos los tableros que se obtienen con un intercambio.

    Cada vecino es un diccionario con tres datos:
      - "tablero":    cómo queda el tablero
      - "ataques":    cuántos ataques tiene
      - "movimiento": qué par de columnas se intercambió
    """
    vecinos = []
    n = len(tablero)

    for col_a in range(n):
        for col_b in range(col_a + 1, n):
            nuevo_tablero = intercambiar(tablero, col_a, col_b)
            vecino = {
                "tablero": nuevo_tablero,
                "ataques": contar_ataques(nuevo_tablero),
                "movimiento": (col_a, col_b),
            }
            vecinos.append(vecino)

    return vecinos


def obtener_ataques(vecino):
    """Sirve para decirle a sort() que ordene por número de ataques."""
    return vecino["ataques"]


# Regla tabú
# La "memoria prohibida" guarda los últimos movimientos hechos.
# Repetirlos está prohibido, para no dar vueltas en círculo.
# EXCEPCIÓN (aspiración): se permite un movimiento prohibido si
# logra un tablero mejor que el mejor que hemos visto en toda la búsqueda.


def elegir_vecino(vecinos, memoria_prohibida, mejor_ataques_global):
    """Escoge el mejor vecino permitido.

    Devuelve dos cosas: el vecino elegido y una palabra que explica
    por qué se eligió ("normal", "aspiracion" o "bloqueo").
    """
    # Revolvemos primero para que, si hay empates, gane uno al azar.
    # Después ordenamos de menos a más ataques (el orden relativo de
    # los empates se conserva, así que el azar se mantiene).
    random.shuffle(vecinos)
    vecinos.sort(key=obtener_ataques)

    for vecino in vecinos:
        esta_prohibido = vecino["movimiento"] in memoria_prohibida
        rompe_record = vecino["ataques"] < mejor_ataques_global

        if not esta_prohibido:
            return vecino, "normal"
        if rompe_record:
            return vecino, "aspiracion"

    # Si llegamos aquí, TODOS los movimientos estaban prohibidos
    # y ninguno rompía el récord: tomamos el mejor de todos modos.
    return vecinos[0], "bloqueo"


# Algoritmo completo

def busqueda_tabu(tablero_inicial, max_iteraciones, tamano_memoria):
    actual = tablero_inicial[:]
    mejor = actual[:]
    mejor_ataques = contar_ataques(mejor)

    memoria_prohibida = []
    iteraciones = 0
    usos_aspiracion = 0
    usos_bloqueo = 0

    # Repetimos hasta resolver el problema (0 ataques) o agotar el límite.
    while iteraciones < max_iteraciones and mejor_ataques > 0:
        vecinos = generar_vecinos(actual)
        elegido, motivo = elegir_vecino(vecinos, memoria_prohibida, mejor_ataques)

        if motivo == "aspiracion":
            usos_aspiracion += 1
        elif motivo == "bloqueo":
            usos_bloqueo += 1

        # Nos movemos al vecino elegido.
        actual = elegido["tablero"]
        iteraciones += 1

        # Anotamos el movimiento como prohibido; si la memoria se llena,
        # olvidamos el movimiento más viejo (el primero de la lista).
        memoria_prohibida.append(elegido["movimiento"])
        if len(memoria_prohibida) > tamano_memoria:
            memoria_prohibida.pop(0)

        # ¿Es el mejor tablero visto hasta ahora?
        if elegido["ataques"] < mejor_ataques:
            mejor = actual[:]
            mejor_ataques = elegido["ataques"]

    resultado = {
        "tablero": mejor,
        "ataques": mejor_ataques,
        "iteraciones": iteraciones,
        "aspiraciones": usos_aspiracion,
        "bloqueos": usos_bloqueo,
    }
    return resultado

#-------------------------------------

def programa_principal():
    semilla = 35        
    cantidad_reinas = 8
    max_iteraciones = 500
    tamano_memoria = 5      # Cuántos movimientos recientes se recuerdan

    random.seed(semilla)
    tablero_inicial = crear_tablero_aleatorio(cantidad_reinas)

    # Medición de lo que tarda el algoritmo.
    inicio = time.perf_counter()
    resultado = busqueda_tabu(tablero_inicial, max_iteraciones, tamano_memoria)
    fin = time.perf_counter()

    print("Tablero inicial:", tablero_inicial)
    print("Ataques al inicio:", contar_ataques(tablero_inicial))
    print()
    print("Mejor tablero encontrado:", resultado["tablero"])
    print("Ataques restantes:", resultado["ataques"])
    print("Iteraciones realizadas:", resultado["iteraciones"])
    print("Veces que se usó la aspiración:", resultado["aspiraciones"])
    print("Veces que todo estaba prohibido:", resultado["bloqueos"])
    print("Tiempo de ejecución (segundos):", round(fin - inicio, 4))
    print()
    dibujar_tablero(resultado["tablero"])


programa_principal()