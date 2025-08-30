# -*- coding: utf-8 -*-
# ejercicio_1_tabla_mejor_por_fila.py

import time
import pandas as pd
from typing import List, Any, Optional

# ========= Algoritmos de búsqueda =========

def busqueda_lineal(arr: List[Any], objetivo: Any) -> int:
    for i, val in enumerate(arr):
        if val == objetivo:
            return i
    return -1

def busqueda_binaria_iterativa(arr: List[Any], objetivo: Any) -> int:
    izq, der = 0, len(arr) - 1
    while izq <= der:
        medio = (izq + der) // 2
        if arr[medio] == objetivo:
            return medio
        if arr[medio] < objetivo:
            izq = medio + 1
        else:
            der = medio - 1
    return -1

def busqueda_binaria_recursiva(arr: List[Any], objetivo: Any, izq: int = 0, der: Optional[int] = None) -> int:
    if der is None:
        der = len(arr) - 1
    if izq > der:
        return -1
    medio = (izq + der) // 2
    if arr[medio] == objetivo:
        return medio
    if arr[medio] < objetivo:
        return busqueda_binaria_recursiva(arr, objetivo, medio + 1, der)
    return busqueda_binaria_recursiva(arr, objetivo, izq, medio - 1)

# ========= Función para medir =========

def medir_ns(funcion, lista, objetivo) -> int:
    t0 = time.perf_counter_ns()
    _ = funcion(lista, objetivo)
    t1 = time.perf_counter_ns()
    return t1 - t0

# ========= Datos =========

tamaño = 20_000
datos_ordenados = list(range(tamaño))

# 🎯 Lista de números que quieres buscar
objetivos = [3, 3433, 6778, 6, 15000, 19999, 50, 12345, 9876, 1]

# ========= Ejecución =========

resultados = []

for idx, num in enumerate(objetivos, start=1):
    t_lin = medir_ns(busqueda_lineal, datos_ordenados, num)
    t_bin_it = medir_ns(busqueda_binaria_iterativa, datos_ordenados, num)
    t_bin_rec = medir_ns(busqueda_binaria_recursiva, datos_ordenados, num)

    # Determinar el más rápido
    tiempos = {
        "Lineal": t_lin,
        "Binaria Iterativa": t_bin_it,
        "Binaria Recursiva": t_bin_rec
    }
    mejor_algoritmo = min(tiempos, key=tiempos.get)

    resultados.append({
        "Búsqueda #": idx,
        "Número": num,
        "Lineal (ns)": t_lin,
        "Binaria Iterativa (ns)": t_bin_it,
        "Binaria Recursiva (ns)": t_bin_rec,
        "Mejor Algoritmo": mejor_algoritmo
    })

# Crear DataFrame para tabla
df_resultados = pd.DataFrame(resultados)

# Agregar fila con promedios
promedios = {
    "Búsqueda #": "Promedio",
    "Número": "-",
    "Lineal (ns)": int(df_resultados["Lineal (ns)"].mean()),
    "Binaria Iterativa (ns)": int(df_resultados["Binaria Iterativa (ns)"].mean()),
    "Binaria Recursiva (ns)": int(df_resultados["Binaria Recursiva (ns)"].mean()),
    "Mejor Algoritmo": min(
        {
            "Lineal": df_resultados["Lineal (ns)"].mean(),
            "Binaria Iterativa": df_resultados["Binaria Iterativa (ns)"].mean(),
            "Binaria Recursiva": df_resultados["Binaria Recursiva (ns)"].mean()
        },
        key=lambda x: {
            "Lineal": df_resultados["Lineal (ns)"].mean(),
            "Binaria Iterativa": df_resultados["Binaria Iterativa (ns)"].mean(),
            "Binaria Recursiva": df_resultados["Binaria Recursiva (ns)"].mean()
        }[x]
    )
}

df_resultados = pd.concat([df_resultados, pd.DataFrame([promedios])], ignore_index=True)

# Mostrar tabla final
print(df_resultados.to_string(index=False))
