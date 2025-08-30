
import time
import pandas as pd
from typing import List

# ================== Funciones Recursivas 

def invertir_cadena_recursiva(cadena: str) -> str:
    if cadena == "":
        return cadena
    return invertir_cadena_recursiva(cadena[1:]) + cadena[0]

def suma_lista_recursiva(lista: List[int]) -> int:
    if not lista:
        return 0
    return lista[0] + suma_lista_recursiva(lista[1:])

# Funciones Iterativas 

def invertir_cadena_iterativa(cadena: str) -> str:
    resultado = ""
    for caracter in cadena:
        resultado = caracter + resultado
    return resultado

def suma_lista_iterativa(lista: List[int]) -> int:
    total = 0
    for numero in lista:
        total += numero
    return total

#  Utilidades

def medir_ns(func, *args) -> int:
    t0 = time.perf_counter_ns()
    _ = func(*args)
    t1 = time.perf_counter_ns()
    return t1 - t0

def generar_cadena(n: int) -> str:
    # 
    return "".join(chr(97 + (i % 26)) for i in range(n))

#  Casos de prueba (10 ejemplos) 

# Elegimos tamaños moderados para evitar error de recursión
tamaños_texto = [5, 10, 20, 50, 100, 200, 300, 400, 600, 800]
tamaños_lista = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800]

#  Medición y tabla 

filas = []

# --- Invertir cadena (10 casos) ---
for idx, n in enumerate(tamaños_texto, start=1):
    txt = generar_cadena(n)
    esperado = txt[::-1]

    t_rec = medir_ns(invertir_cadena_recursiva, txt)
    r_rec = invertir_cadena_recursiva(txt)
    t_it  = medir_ns(invertir_cadena_iterativa, txt)
    r_it  = invertir_cadena_iterativa(txt)

    correcto = (r_rec == esperado) and (r_it == esperado)
    mejor = "Recursiva" if t_rec < t_it else "Iterativa"

    filas.append({
        "Caso": f"Invertir #{idx}",
        "Tipo": "Invertir Cadena",
        "Tamaño entrada": n,
        "Tiempo Recursiva (ns)": t_rec,
        "Tiempo Iterativa (ns)": t_it,
        "Mejor Algoritmo": mejor,
        "Correcto": "✔" if correcto else "✘"
    })

# --- Sumar lista (10 casos) ---
for idx, n in enumerate(tamaños_lista, start=1):
    lst = list(range(n))
    esperado = sum(lst)

    t_rec = medir_ns(suma_lista_recursiva, lst)
    r_rec = suma_lista_recursiva(lst)
    t_it  = medir_ns(suma_lista_iterativa, lst)
    r_it  = suma_lista_iterativa(lst)

    correcto = (r_rec == esperado) and (r_it == esperado)
    mejor = "Recursiva" if t_rec < t_it else "Iterativa"

    filas.append({
        "Caso": f"Suma #{idx}",
        "Tipo": "Suma Lista",
        "Tamaño entrada": n,
        "Tiempo Recursiva (ns)": t_rec,
        "Tiempo Iterativa (ns)": t_it,
        "Mejor Algoritmo": mejor,
        "Correcto": "✔" if correcto else "✘"
    })

df = pd.DataFrame(filas)

# (Opcional) Ordenar por tipo y tamaño para lectura
df = df.sort_values(by=["Tipo", "Tamaño entrada"], ascending=[True, True]).reset_index(drop=True)

# Agregar filas de promedio por tipo
for tipo in ["Invertir Cadena", "Suma Lista"]:
    sub = df[df["Tipo"] == tipo]
    fila_prom = {
        "Caso": "Promedio",
        "Tipo": tipo,
        "Tamaño entrada": "-",
        "Tiempo Recursiva (ns)": int(sub["Tiempo Recursiva (ns)"].mean()),
        "Tiempo Iterativa (ns)": int(sub["Tiempo Iterativa (ns)"].mean()),
        "Mejor Algoritmo": "Recursiva" if sub["Tiempo Recursiva (ns)"].mean() < sub["Tiempo Iterativa (ns)"].mean() else "Iterativa",
        "Correcto": "-"
    }
    df = pd.concat([df, pd.DataFrame([fila_prom])], ignore_index=True)

# Mostrar tabla final en consola
print(df.to_string(index=False))
