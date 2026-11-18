# Generador del video: ciclo euleriano

Genera el video silencioso del algoritmo de Hierholzer. La animación utiliza
los estados producidos por la ejecución de la implementación propia en C++:
aristas usadas, pila y circuito parcial. También ejecuta el caso sin aristas.
El grafo ilustrativo y las posiciones para dibujarlo están en `grafo.json`;
los textos y la duración de las escenas forman parte de la presentación.

Se necesita Python, un compilador `g++` compatible con C++11 en el PATH,
y Microsoft Edge o Google Chrome; en su defecto, Chromium de Playwright.

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
python renderizar.py
```

El renderizador compila `hierholzer.cpp` en un directorio temporal, ejecuta
el algoritmo para ambos grafos y entrega su traza al navegador. El resultado
se guarda en `video/ciclo_euleriano.mp4`. Para una vista previa de menor
resolución se puede usar `python renderizar.py --preview`. Los tiempos están
en `duraciones.json`. El HTML se carga mediante el renderizador, que aporta
los datos calculados; abrirlo directamente no ejecuta el algoritmo.
