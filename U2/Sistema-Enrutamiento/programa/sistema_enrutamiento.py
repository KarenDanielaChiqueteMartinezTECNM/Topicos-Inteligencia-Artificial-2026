# Sistema de enrutamiento para tiendas de Culiacán
# Hecho con elementos básicos de Python: listas, ciclos, condicionales y funciones sencillas.
# Solo usa módulos que vienen con Python.

import csv
import random
import math
import time

# Ajustes para repetir el mismo experimento
SEMILLA = 20261016
NUMERO_DE_CENTROS = 10
TIENDAS_POR_RUTA = 9
NUMERO_DE_INTENTOS = 80000
MAX_INTENTOS_SIN_MEJORA = 10000
VELOCIDAD_PROMEDIO = 30.0


def leer_matriz(nombre_archivo):
    """Abre un CSV y convierte sus números en una matriz de listas."""
    matriz = []
    archivo = open(nombre_archivo, "r", encoding="utf-8-sig", newline="")
    lector = csv.reader(archivo)
    encabezado = next(lector)  # Salta los nombres Nodo_1, Nodo_2, etc.

    for fila in lector:
        fila_de_numeros = []
        for valor in fila:
            fila_de_numeros.append(float(valor))
        matriz.append(fila_de_numeros)

    archivo.close()
    return matriz


def leer_tiendas(nombre_archivo):
    """Lee nombres, tipos y coordenadas de cada punto."""
    nombres = []
    tipos = []
    latitudes = []
    longitudes = []

    archivo = open(nombre_archivo, "r", encoding="utf-8-sig", newline="")
    lector = csv.reader(archivo)
    encabezado = next(lector)

    for fila in lector:
        tipos.append(fila[0])
        nombres.append(fila[1])
        latitudes.append(float(fila[2]))
        longitudes.append(float(fila[3]))

    archivo.close()
    return nombres, tipos, latitudes, longitudes


def costo_de_una_ruta(ruta, centro, matriz_costos):
    """Suma el costo desde el centro, pasando por las tiendas y regresando."""
    costo = 0.0
    punto_anterior = centro

    for tienda in ruta:
        costo = costo + matriz_costos[punto_anterior][tienda]
        punto_anterior = tienda

    costo = costo + matriz_costos[punto_anterior][centro]
    return costo


def costo_de_todas_las_rutas(rutas, centros, matriz_costos):
    """Suma el costo de las diez rutas."""
    costo_total = 0.0
    numero_de_ruta = 0

    while numero_de_ruta < len(rutas):
        centro = centros[numero_de_ruta]
        costo_total = costo_total + costo_de_una_ruta(
            rutas[numero_de_ruta], centro, matriz_costos
        )
        numero_de_ruta = numero_de_ruta + 1

    return costo_total


def crear_rutas_iniciales(centros, tiendas, matriz_costos):
    """Asigna tiendas por costo de ida y vuelta y ordena cada ruta."""
    rutas = []
    for centro in centros:
        rutas.append([])

    tienda_asignada = []
    for tienda in tiendas:
        tienda_asignada.append(False)

    cantidad_asignada = 0
    while cantidad_asignada < len(tiendas):
        mejor_ruta = -1
        mejor_tienda = -1
        menor_costo = None

        # Busca la pareja centro-tienda más barata que todavía tenga espacio.
        for numero_de_ruta in range(len(centros)):
            if len(rutas[numero_de_ruta]) < TIENDAS_POR_RUTA:
                centro = centros[numero_de_ruta]
                for lugar in range(len(tiendas)):
                    if tienda_asignada[lugar] == False:
                        tienda = tiendas[lugar]
                        costo_ida_y_vuelta = (matriz_costos[centro][tienda]
                                              + matriz_costos[tienda][centro])
                        if menor_costo is None or costo_ida_y_vuelta < menor_costo:
                            menor_costo = costo_ida_y_vuelta
                            mejor_ruta = numero_de_ruta
                            mejor_tienda = lugar

        rutas[mejor_ruta].append(tiendas[mejor_tienda])
        tienda_asignada[mejor_tienda] = True
        cantidad_asignada = cantidad_asignada + 1

    # Intenta mejorar la asignación intercambiando tiendas entre dos centros.
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for ruta_1 in range(len(rutas)):
            for ruta_2 in range(ruta_1 + 1, len(rutas)):
                centro_1 = centros[ruta_1]
                centro_2 = centros[ruta_2]
                for lugar_1 in range(len(rutas[ruta_1])):
                    for lugar_2 in range(len(rutas[ruta_2])):
                        tienda_1 = rutas[ruta_1][lugar_1]
                        tienda_2 = rutas[ruta_2][lugar_2]
                        costo_actual = (matriz_costos[centro_1][tienda_1]
                                        + matriz_costos[tienda_1][centro_1]
                                        + matriz_costos[centro_2][tienda_2]
                                        + matriz_costos[tienda_2][centro_2])
                        costo_cambiado = (matriz_costos[centro_1][tienda_2]
                                          + matriz_costos[tienda_2][centro_1]
                                          + matriz_costos[centro_2][tienda_1]
                                          + matriz_costos[tienda_1][centro_2])
                        if costo_cambiado < costo_actual:
                            rutas[ruta_1][lugar_1] = tienda_2
                            rutas[ruta_2][lugar_2] = tienda_1
                            hubo_cambio = True

    # Ordena cada ruta visitando primero la tienda más cercana disponible.
    for numero_de_ruta in range(len(rutas)):
        centro = centros[numero_de_ruta]
        ruta_sin_orden = rutas[numero_de_ruta][:]
        ruta_ordenada = []
        punto_actual = centro

        while len(ruta_sin_orden) > 0:
            tienda_mas_cercana = ruta_sin_orden[0]
            for tienda in ruta_sin_orden:
                if matriz_costos[punto_actual][tienda] < matriz_costos[punto_actual][tienda_mas_cercana]:
                    tienda_mas_cercana = tienda

            ruta_ordenada.append(tienda_mas_cercana)
            ruta_sin_orden.remove(tienda_mas_cercana)
            punto_actual = tienda_mas_cercana

        rutas[numero_de_ruta] = ruta_ordenada

    return rutas


def copiar_rutas(rutas):
    """Crea una copia de las rutas para probar un cambio sin perder la original."""
    copia = []
    for ruta in rutas:
        copia.append(ruta[:])
    return copia


def hacer_un_cambio(rutas, generador):
    """Cambia el orden de una ruta o intercambia tiendas entre dos rutas."""
    nuevas_rutas = copiar_rutas(rutas)
    numero_de_ruta = generador.randrange(len(nuevas_rutas))
    tipo_de_cambio = generador.random()

    if tipo_de_cambio < 0.45:
        # 2-opt: da vuelta a un tramo de la ruta.
        primero = generador.randrange(TIENDAS_POR_RUTA)
        segundo = generador.randrange(TIENDAS_POR_RUTA)
        while primero == segundo:
            segundo = generador.randrange(TIENDAS_POR_RUTA)
        if primero > segundo:
            temporal = primero
            primero = segundo
            segundo = temporal
        # Da vuelta el tramo cambiando sus extremos poco a poco.
        while primero < segundo:
            tienda_temporal = nuevas_rutas[numero_de_ruta][primero]
            nuevas_rutas[numero_de_ruta][primero] = nuevas_rutas[numero_de_ruta][segundo]
            nuevas_rutas[numero_de_ruta][segundo] = tienda_temporal
            primero = primero + 1
            segundo = segundo - 1

    elif tipo_de_cambio < 0.70:
        # Mueve una tienda a otra posición de la misma ruta.
        primero = generador.randrange(TIENDAS_POR_RUTA)
        segundo = generador.randrange(TIENDAS_POR_RUTA)
        while primero == segundo:
            segundo = generador.randrange(TIENDAS_POR_RUTA)
        tienda = nuevas_rutas[numero_de_ruta].pop(primero)
        nuevas_rutas[numero_de_ruta].insert(segundo, tienda)

    else:
        # Intercambia una tienda entre dos centros; cada ruta sigue con nueve.
        otra_ruta = generador.randrange(len(nuevas_rutas))
        while otra_ruta == numero_de_ruta:
            otra_ruta = generador.randrange(len(nuevas_rutas))
        lugar_1 = generador.randrange(TIENDAS_POR_RUTA)
        lugar_2 = generador.randrange(TIENDAS_POR_RUTA)
        tienda_temporal = nuevas_rutas[numero_de_ruta][lugar_1]
        nuevas_rutas[numero_de_ruta][lugar_1] = nuevas_rutas[otra_ruta][lugar_2]
        nuevas_rutas[otra_ruta][lugar_2] = tienda_temporal

    return nuevas_rutas


def buscar_mejores_rutas(rutas_iniciales, centros, matriz_costos):
    """Prueba cambios y conserva la mejor solución con Recocido Simulado."""
    random.seed(SEMILLA)
    generador = random
    ruta_actual = copiar_rutas(rutas_iniciales)
    mejor_ruta = copiar_rutas(rutas_iniciales)
    costo_actual = costo_de_todas_las_rutas(ruta_actual, centros, matriz_costos)
    mejor_costo = costo_actual

    temperatura = 0.22
    temperatura_final = 0.00005
    factor_de_enfriamiento = (temperatura_final / temperatura) ** (1.0 / NUMERO_DE_INTENTOS)
    historial = []
    movimientos_aceptados = 0
    intentos_sin_mejora = 0

    for intento in range(1, NUMERO_DE_INTENTOS + 1):
        rutas_propuestas = hacer_un_cambio(ruta_actual, generador)
        costo_propuesto = costo_de_todas_las_rutas(
            rutas_propuestas, centros, matriz_costos
        )
        diferencia = costo_propuesto - costo_actual

        # Si mejora se acepta. Si empeora, a veces se acepta para explorar más rutas.
        aceptar_cambio = False
        if diferencia <= 0:
            aceptar_cambio = True
        else:
            numero_aleatorio = generador.random()
            probabilidad = math.exp(-diferencia / temperatura)
            if numero_aleatorio < probabilidad:
                aceptar_cambio = True

        if aceptar_cambio:
            ruta_actual = rutas_propuestas
            costo_actual = costo_propuesto
            movimientos_aceptados = movimientos_aceptados + 1

        if costo_actual < mejor_costo:
            mejor_ruta = copiar_rutas(ruta_actual)
            mejor_costo = costo_actual
            intentos_sin_mejora = 0
        else:
            intentos_sin_mejora = intentos_sin_mejora + 1

        temperatura = temperatura * factor_de_enfriamiento

        if intento % 1000 == 0 or intentos_sin_mejora >= MAX_INTENTOS_SIN_MEJORA:
            historial.append([intento, mejor_costo])

        # Si la mejor solución no cambia durante mucho tiempo, se termina antes.
        if intentos_sin_mejora >= MAX_INTENTOS_SIN_MEJORA:
            break

    return mejor_ruta, historial, movimientos_aceptados


def distancia_de_una_ruta(ruta, centro, matriz_distancias):
    """Suma la distancia de ida, las visitas y el regreso al centro."""
    distancia = 0.0
    punto_anterior = centro

    for tienda in ruta:
        distancia = distancia + matriz_distancias[punto_anterior][tienda]
        punto_anterior = tienda

    distancia = distancia + matriz_distancias[punto_anterior][centro]
    return distancia


def guardar_resultados(rutas, rutas_iniciales, centros, nombres,
                       matriz_costos, matriz_distancias, historial):
    """Guarda comparación, rutas y progreso como archivos CSV."""
    costo_inicial = costo_de_todas_las_rutas(rutas_iniciales, centros, matriz_costos)
    costo_final = costo_de_todas_las_rutas(rutas, centros, matriz_costos)
    distancia_inicial = 0.0
    distancia_final = 0.0

    for numero_de_ruta in range(len(rutas)):
        distancia_inicial = distancia_inicial + distancia_de_una_ruta(
            rutas_iniciales[numero_de_ruta], centros[numero_de_ruta], matriz_distancias
        )
        distancia_final = distancia_final + distancia_de_una_ruta(
            rutas[numero_de_ruta], centros[numero_de_ruta], matriz_distancias
        )

    archivo = open("comparacion_resultados.csv", "w", encoding="utf-8-sig", newline="")
    escritor = csv.writer(archivo)
    escritor.writerow(["Escenario", "Distancia (unidades de distancia)",
                       "Costo (unidades de costo)", "Reduccion de costo (%)"])
    escritor.writerow(["Rutas iniciales", distancia_inicial, costo_inicial, 0])
    reduccion = (costo_inicial - costo_final) / costo_inicial * 100
    escritor.writerow(["Recocido simulado", distancia_final, costo_final, reduccion])
    archivo.close()

    archivo = open("rutas_optimizadas.csv", "w", encoding="utf-8-sig", newline="")
    escritor = csv.writer(archivo)
    escritor.writerow(["Centro", "Tiendas visitadas", "Secuencia",
                       "Distancia (unidades de distancia)",
                       "Costo (unidades de costo)"])

    for numero_de_ruta in range(len(rutas)):
        centro = centros[numero_de_ruta]
        secuencia = [nombres[centro]]
        for tienda in rutas[numero_de_ruta]:
            secuencia.append(nombres[tienda])
        secuencia.append(nombres[centro])
        escritor.writerow([
            nombres[centro], len(rutas[numero_de_ruta]),
            " -> ".join(secuencia),
            distancia_de_una_ruta(rutas[numero_de_ruta], centro, matriz_distancias),
            costo_de_una_ruta(rutas[numero_de_ruta], centro, matriz_costos)
        ])
    archivo.close()

    archivo = open("progreso.csv", "w", encoding="utf-8-sig", newline="")
    escritor = csv.writer(archivo)
    escritor.writerow(["Intento", "Mejor costo (unidades de costo)"])
    for dato in historial:
        escritor.writerow(dato)
    archivo.close()

    return costo_inicial, costo_final, distancia_inicial, distancia_final


def revisar_rutas(rutas, tiendas):
    """Comprueba que cada tienda aparezca una vez y haya nueve por ruta."""
    visitadas = []
    for ruta in rutas:
        if len(ruta) != TIENDAS_POR_RUTA:
            return False
        for tienda in ruta:
            visitadas.append(tienda)

    if len(visitadas) != len(tiendas):
        return False
    for primera in range(len(visitadas)):
        for segunda in range(primera + 1, len(visitadas)):
            if visitadas[primera] == visitadas[segunda]:
                return False
    return True


def principal():
    print("Leyendo los archivos CSV...")
    matriz_distancias = leer_matriz("matriz_distancias.csv")
    matriz_costos = leer_matriz("matriz_costos_combustible.csv")
    nombres, tipos, latitudes, longitudes = leer_tiendas("datos_distribucion_tiendas.csv")

    centros = []
    tiendas = []
    for numero in range(len(tipos)):
        if tipos[numero] == "Centro de Distribución":
            centros.append(numero)
        else:
            tiendas.append(numero)

    print("Creando las rutas iniciales...")
    rutas_iniciales = crear_rutas_iniciales(centros, tiendas, matriz_costos)
    print("Probando cambios con Recocido Simulado...")
    tiempo_inicio = time.time()
    mejores_rutas, historial, aceptados = buscar_mejores_rutas(
        rutas_iniciales, centros, matriz_costos
    )
    tiempo_final = time.time() - tiempo_inicio

    if revisar_rutas(mejores_rutas, tiendas):
        print("Prueba correcta: las 90 tiendas están incluidas una sola vez.")
    else:
        print("Error: revisa las rutas porque falta una tienda o hay una repetida.")
        return

    costo_inicial, costo_final, distancia_inicial, distancia_final = guardar_resultados(
        mejores_rutas, rutas_iniciales, centros, nombres,
        matriz_costos, matriz_distancias, historial
    )

    print("\nRESULTADOS")
    print("Costo inicial: {:.2f} unidades de costo".format(costo_inicial))
    print("Costo final: {:.2f} unidades de costo".format(costo_final))
    print("Reducción: {:.2f}%".format((costo_inicial - costo_final) / costo_inicial * 100))
    print("Distancia inicial: {:.2f} unidades de distancia".format(distancia_inicial))
    print("Distancia final: {:.2f} unidades de distancia".format(distancia_final))
    print("Intentos máximos: {:,}".format(NUMERO_DE_INTENTOS))
    print("Intentos realizados: {:,}".format(historial[-1][0]))
    print("Movimientos aceptados: {}".format(aceptados))
    print("Tiempo de ejecución: {:.2f} segundos".format(tiempo_final))
    print("Se guardaron comparacion_resultados.csv, rutas_optimizadas.csv y progreso.csv.")


principal()
