#!/usr/bin/env python3
"""
Convertidor universal a WAV y MP3.

Convierte cualquier archivo de audio o video (mp4, ogg, mkv, flac, m4a, avi, etc.)
a formato WAV y/o MP3 usando ffmpeg como motor de conversión.

Requisitos:
    - ffmpeg instalado y disponible en el PATH del sistema.
      Windows:  https://ffmpeg.org/download.html (o `choco install ffmpeg`)
      macOS:    brew install ffmpeg
      Linux:    sudo apt install ffmpeg

Uso:
    python convertir_audio.py entrada.mp4
    python convertir_audio.py entrada.ogg --formato mp3
    python convertir_audio.py entrada.mkv --formato wav --salida carpeta_salida
    python convertir_audio.py *.mp4 --formato ambos      (en bash/zsh con glob)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def verificar_ffmpeg():
    """Verifica que ffmpeg esté instalado; si no, aborta con un mensaje claro."""
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "❌ No se encontró 'ffmpeg' en el sistema.\n"
            "   Instálalo primero:\n"
            "   - Windows: https://ffmpeg.org/download.html\n"
            "   - macOS:   brew install ffmpeg\n"
            "   - Linux:   sudo apt install ffmpeg"
        )


def convertir(
    archivo_entrada: Path,
    formato: str,
    carpeta_salida: Path,
    bitrate_mp3: str = "192k",
    sample_rate: int = 44100,
):
    """
    Convierte un archivo a WAV, MP3 o ambos usando ffmpeg.

    Args:
        archivo_entrada: ruta del archivo original (cualquier formato soportado por ffmpeg).
        formato: 'wav', 'mp3' o 'ambos'.
        carpeta_salida: carpeta donde se guardarán los archivos convertidos.
        bitrate_mp3: bitrate para la salida mp3 (ej. '192k', '320k').
        sample_rate: frecuencia de muestreo de salida en Hz.
    """
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    nombre_base = archivo_entrada.stem
    resultados = []

    tareas = []
    if formato in ("wav", "ambos"):
        tareas.append("wav")
    if formato in ("mp3", "ambos"):
        tareas.append("mp3")

    for ext in tareas:
        salida = carpeta_salida / f"{nombre_base}.{ext}"
        cmd = [
            "ffmpeg",
            "-y",  # sobrescribe si ya existe
            "-i",
            str(archivo_entrada),  # archivo de entrada
            "-vn",  # descarta cualquier pista de video
            "-ar",
            str(sample_rate),  # frecuencia de muestreo
        ]
        if ext == "mp3":
            cmd += ["-codec:a", "libmp3lame", "-b:a", bitrate_mp3]
        else:  # wav
            cmd += ["-codec:a", "pcm_s16le"]
        cmd.append(str(salida))

        print(f"🎧 Convirtiendo '{archivo_entrada.name}' → '{salida.name}' ...")
        proceso = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if proceso.returncode != 0:
            print(f"❌ Error al convertir a {ext.upper()}:")
            print(
                proceso.stderr.strip().splitlines()[-1]
                if proceso.stderr
                else "Error desconocido"
            )
        else:
            print(f"✅ Listo: {salida}")
            resultados.append(salida)

    return resultados


def main():
    parser = argparse.ArgumentParser(
        description="Convierte cualquier formato de audio/video a WAV y/o MP3."
    )
    parser.add_argument(
        "archivos",
        nargs="+",
        help="Uno o más archivos de entrada (mp4, ogg, mkv, flac, etc.)",
    )
    parser.add_argument(
        "--formato",
        choices=["wav", "mp3", "ambos"],
        default="ambos",
        help="Formato de salida deseado (por defecto: ambos)",
    )
    parser.add_argument(
        "--salida",
        default="convertidos",
        help="Carpeta donde se guardarán los archivos convertidos (por defecto: ./convertidos)",
    )
    parser.add_argument(
        "--bitrate",
        default="192k",
        help="Bitrate para MP3, ej. 128k, 192k, 320k (por defecto: 192k)",
    )
    parser.add_argument(
        "--samplerate",
        type=int,
        default=44100,
        help="Frecuencia de muestreo en Hz (por defecto: 44100)",
    )
    args = parser.parse_args()

    verificar_ffmpeg()
    carpeta_salida = Path(args.salida)

    total_ok = 0
    for ruta_str in args.archivos:
        archivo = Path(ruta_str)
        if not archivo.exists():
            print(f"⚠️  Archivo no encontrado, se omite: {archivo}")
            continue
        resultados = convertir(
            archivo, args.formato, carpeta_salida, args.bitrate, args.samplerate
        )
        total_ok += len(resultados)

    print(
        f"\n🎉 Conversión terminada. {total_ok} archivo(s) generado(s) en '{carpeta_salida}'."
    )


if __name__ == "__main__":
    main()
