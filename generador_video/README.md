# Generador del video: ciclo euleriano

Genera el video silencioso, sin subt?tulos, con las escenas y los tiempos del video original. No necesita archivos de audio ni subt?tulos.

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
python renderizar.py
```

El resultado se guarda en `video/ciclo_euleriano.mp4`. El programa usa Microsoft Edge o Google Chrome si est?n instalados; de lo contrario, usa Chromium de Playwright. Para una vista previa de menor resoluci?n: `python renderizar.py --preview`. Los tiempos de cada escena est?n en `duraciones.json`.
