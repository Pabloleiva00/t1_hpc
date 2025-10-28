a) Los resultados de referencia estan en el archivo `resultados.csv`

b) Los ajustes del codigo estan en `main.cpp`

c) La implementacion en Python esta `main.py` y sus respectivos resultados estan en `resultados_numba.csv` y `resultados_numba1.csv`

d) Los graficos con los resultados estan en [Colab](https://colab.research.google.com/drive/19K46_v6vEFIr4JTWJzmNxD2URZwWkuy9?usp=sharing#scrollTo=sFgdWeV7n0Xh)

e) Los graficos de speedup y eficiencia estan en [Colab](https://colab.research.google.com/drive/19K46_v6vEFIr4JTWJzmNxD2URZwWkuy9?usp=sharing#scrollTo=sFgdWeV7n0Xh)

Discusión e) y f) 

Para esta respuesta se consideran los resultados encontrados (+21.000.000 primos) por el dataset hecho por C++ y los dos dataset hechos por numba. Guiandonos por eficienciencia y speedup, todos los resultados estan muy cercanos, estadisticamente probablemente no hay distincion significativa entre los modos guided/dynamic/secuencial/static. Aún con eso dicho, dynamic guided muestra resultados ligeramente que el resto. En base a los resultados de C++.

Ahora, sobre el scaling: usando los resultados de numba se ve como la eficiencia disminuye linealmente a medida que aumenta los threads y el speedup aumenta linealmente tambien, ambos aproximadamente.

<img width="790" height="490" alt="image" src="https://github.com/user-attachments/assets/1cf4ead4-b930-4577-bf76-a1606d144c4e" />
**Grafico: Eficiencia vs Threads**

<img width="790" height="490" alt="image" src="https://github.com/user-attachments/assets/17ddf506-0378-4cce-af21-9e00ce624a50" />
**Speedup vs Threads**

Viendo estas metricas en C++ se ven los mismo efectos de speedup y eficiencia lineal.

Si bien se mantienen las relaciones lineales a medida que aumenta los cores, este (de)crecimiento le sigue el pie a los cores, en C++ hay un crecimiento en speedup de $\frac{1}{4} \frac{speedup}{thread}$, en numba se ve un speedup más cercano a $\frac{4}{10}$.  Se explica el mejor rendimiento en Numba debido a que estos resultados parten de tiempos peores, y por ende aún el overhead aun no es proporcialmente tan relevante vs la tarea en si: 
* C++ (static):
  1. 1 thread: 116s
  2. 2 thread: 61s
  3. 10 thread: 31s
* Numba:
  1. 1 thread: 360s
  2. 2 thread: 229s
  3. 10 thread: 66s

Hablando de escalabilidad en terminos de la Ley de Amdahl y Gustafson, se ve que si bien existen speedups y tendencia a menores tiempo, la eficiencia esta disminuyendo en todos los casos. Basado en esto se rechaza la hipotesis de que haya escalamiento fuerte. En cambio, los datos y en la naturaleza del problema este problema se podria categorizar como uno de escalamiento debil. Se espera que aumentando la cantidad de primos que calcular propocionalmente con los cores/threads el speedup se podría mantener una eficiencia lineal haciendo el overhead dijo proporcionalmente insignificante.

**Tabla: Caida en eficiencia proporcional a threads (numba1.csv)**

| index | modo       | threads | eficiencia |
|-------:|------------|--------:|-----------:|
| 0     | paralelo   | 1       | 1.035557   |
| 1     | paralelo   | 2       | 0.812427   |
| 2     | paralelo   | 4       | 0.716317   |
| 3     | paralelo   | 6       | 0.658154   |
| 4     | paralelo   | 8       | 0.610782   |
| 5     | paralelo   | 10      | 0.559862   |
| 6     | paralelo   | 12      | 0.497035   |
| 7     | secuencial | 1       | 1.000000   |
