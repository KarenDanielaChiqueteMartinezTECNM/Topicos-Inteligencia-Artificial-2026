# Sistema de rutas para tiendas

Este proyecto prueba el algoritmo de Recocido Simulado para organizar las entregas a 90 tiendas desde 10 centros de distribución. Cada ruta visita nueve tiendas y regresa al centro que le corresponde. La búsqueda intenta reducir el costo total estimado de los recorridos.

## Qué contiene

- `programa/`: código de Python y los tres archivos CSV que usa como entrada.
- `resultados/`: archivos CSV de una ejecución de ejemplo.

El programa usa módulos que vienen con Python; no hay que instalar paquetes adicionales.

## Cómo ejecutarlo

Necesitas Python 3. Abre una terminal y entra a la carpeta `programa`:

```text
cd programa
python sistema_enrutamiento.py
```

En Windows también puedes usar `py sistema_enrutamiento.py`. Al terminar, el programa guarda `comparacion_resultados.csv`, `rutas_optimizadas.csv` y `progreso.csv` dentro de `programa/`. Los archivos de `resultados/` son una copia de referencia de una ejecución anterior.

## Sobre los datos

El algoritmo usa las matrices de distancia y costo incluidas en `programa/`. Los archivos no indican una unidad física de distancia ni una moneda, así que el programa reporta valores como unidades de distancia y de costo. El tiempo aproximado se calcula suponiendo una velocidad promedio de 30 km/h. La prueba no modela tráfico, demanda, capacidad del vehículo ni tiempo de descarga.

La semilla fija permite repetir la misma secuencia aleatoria con los mismos datos y parámetros. El programa permite hasta 80,000 intentos y puede detenerse antes si pasan 10,000 intentos seguidos sin mejorar la mejor ruta.
