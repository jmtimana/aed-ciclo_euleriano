"""Exporta la presentación HTML a MP4 silencioso, sin grabar la pantalla."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from playwright.sync_api import sync_playwright
import imageio_ffmpeg

BASE = Path(__file__).resolve().parent

def tiempos():
    datos = json.loads((BASE / 'duraciones.json').read_text(encoding='utf-8'))
    return datos['duraciones']

def navegador():
    candidatos = [Path(os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)'))/'Microsoft/Edge/Application/msedge.exe',
                  Path(os.environ.get('PROGRAMFILES', 'C:/Program Files'))/'Google/Chrome/Application/chrome.exe']
    return next((str(p) for p in candidatos if p.exists()), None)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Exporta a menor resolución')
    args = parser.parse_args()
    duraciones = tiempos()
    salida = BASE / 'video' / 'ciclo_euleriano.mp4'
    salida.parent.mkdir(exist_ok=True)
    width, height = (854, 480) if args.preview else (1920, 1080)
    with tempfile.TemporaryDirectory(prefix='euler_render_') as tmp, sync_playwright() as p:
        executable = navegador()
        browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
        page = browser.new_page(viewport={'width': 1140, 'height': 680}, device_scale_factor=1)
        page.goto((BASE/'index.html').as_uri(), wait_until='load')
        page.add_style_tag(content='body{padding:0}.frame{width:1100px;max-width:none;aspect-ratio:16/9}.controls{visibility:hidden}')
        total = page.evaluate('sequence.length')
        if total != len(duraciones):
            raise ValueError(f'La presentación tiene {total} pasos y el SRT {len(duraciones)}; revisa los tiempos.')
        entradas = []
        for i, duracion in enumerate(duraciones):
            scene = page.evaluate('(i) => { displayEvent(i); return sequence[i].scene; }', i)
            # Muestreamos la animación de la pila durante su primer segundo.
            muestras = 8 if scene == 4 else 1
            for j in range(muestras):
                if muestras > 1:
                    page.wait_for_timeout(125)
                else:
                    page.wait_for_timeout(300)
                archivo = Path(tmp) / f'{i:03}_{j:02}.png'
                page.screenshot(path=str(archivo), clip=page.locator('.frame').bounding_box(), animations='allow')
                tramo = .125 if j < muestras-1 else max(.125, duracion - .125*(muestras-1))
                entradas.append((archivo, tramo))
            print(f'Escena {i+1}/{total}', flush=True)
        browser.close()
        manifiesto = Path(tmp)/'imagenes.txt'
        manifiesto.write_text(''.join(f"file '{f.as_posix()}'\noption framerate 1000\nduration {d:.3f}\n" for f,d in entradas) + f"file '{entradas[-1][0].as_posix()}'\noption framerate 1000\n", encoding='utf-8')
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(manifiesto), '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p,fps=30', '-fps_mode', 'cfr', '-an', '-sn', '-c:v', 'libx264', '-preset', 'veryfast', '-movflags', '+faststart', str(salida)]
        subprocess.run(cmd, check=True)
        # Ajusta peque?as diferencias del codificador a la duracion exacta del audio.
        objetivo = json.loads((BASE / 'duraciones.json').read_text(encoding='utf-8'))['duracion_final']
        inspeccion = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(salida)], capture_output=True, text=True).stderr
        match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', inspeccion)
        if not match:
            raise RuntimeError('No se pudo comprobar la duracion del video')
        h,m,seg = match.groups()
        real = int(h)*3600+int(m)*60+float(seg)
        if abs(real-objetivo) > .05:
            corregido = BASE/'video'/'ajuste_temporal.mp4'
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-i', str(salida), '-vf', f'setpts={objetivo/real:.9f}*PTS,fps=30', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', '-an', '-movflags', '+faststart', str(corregido)], check=True)
            corregido.replace(salida)
    print(f'Video generado: {salida}')

if __name__ == '__main__':
    main()
