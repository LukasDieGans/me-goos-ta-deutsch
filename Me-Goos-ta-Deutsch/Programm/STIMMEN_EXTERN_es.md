# Tu propia voz con otros programas

Esta guía pertenece a la herramienta **🎙 Tu propia voz** de Me Goos-ta Deutsch. Muestra cómo crear grabaciones para tus palabras con programas gratuitos e importarlas, sin suscripciones y con espíritu de ganso. Me Goos-ta Deutsch no inicia ni descarga ninguno de estos programas; solo importa los audios terminados.

Datos de noviembre de 2026. Las licencias y los tamaños pueden cambiar; siempre vale la página de cada proyecto.

## El camino en tres pasos

1. **Descarga la lista de palabras.** Herramientas → «Tu propia voz» → «Descargar la lista de palabras (CSV)». El archivo tiene las columnas `datei;sprache;text;vorhanden`. En `datei` está el nombre de cada grabación, p. ej. `es/3f2a9c0d1e4b5a67`; la carpeta es el idioma.
2. **Crea los archivos.** Un audio por palabra con exactamente ese nombre más la extensión, p. ej. `es/3f2a9c0d1e4b5a67.wav`. Se admiten WAV, MP3, OGG, Opus, M4A y WebM, máximo 2 MB por archivo (WAV máximo 15 segundos). Lo ideal son de uno a tres segundos por palabra.
3. **Importa.** Suelta la carpeta, los archivos o un ZIP en la herramienta. Desde entonces cada 🔊 reproduce primero tu archivo.

Usa solo tu propia voz, o una para la que tengas permiso. Palabra de ganso.

## Receta 1: Grabar tú mismo

Lo más fácil es hacerlo en el programa: 🎙 junto a la palabra o la **ronda de grabación** de la herramienta. Si prefieres tu propio equipo:

- **Audacity** (GPL, gratis para cualquier uso, unos 40 MB): graba todas las palabras de una vez con pausas cortas, marca las palabras con etiquetas (como nombre de la etiqueta, el valor de `datei` sin la carpeta) y escribe un archivo por etiqueta con «Exportar → Múltiples archivos». Elige una carpeta distinta para cada idioma (`de`, `es`, …).
- **Grabadora del celular**: una grabación por palabra y luego renombra los archivos en la computadora según la lista. Los formatos de los dispositivos comunes (M4A, MP3, WAV) sirven sin convertir.

## Receta 2: Una voz lista con Piper

**Piper** es un sintetizador de voz que funciona en tu propia computadora sin internet; es un programa aparte, no forma parte de Me Goos-ta Deutsch.

- Licencia: programa GPL-3.0; las voces tienen licencias propias: alemán `de_DE-thorsten` (CC0), español de México `es_MX-claude` (Apache-2.0) y `es_MX-ald` (Unlicense). Uso privado y comercial.
- Tamaño: unos 60 MB por voz, más el programa. Funciona sin tarjeta gráfica.
- Pasos: instala Piper según las instrucciones del proyecto, descarga la voz y crea un WAV por cada línea de la lista. Con Python basta un bucle pequeño:

```
import csv, pathlib, subprocess, sys
stimmen = {"de": "de_DE-thorsten-medium", "es": "es_MX-claude-high"}
for z in csv.DictReader(open("wortliste.csv", encoding="utf-8-sig"), delimiter=";"):
    if z["sprache"] in stimmen:
        ziel = pathlib.Path("aufnahmen") / (z["datei"] + ".wav")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper", "-m", stimmen[z["sprache"]], "-f", str(ziel), "--", z["text"].lstrip("'")], check=True)
```

Después suelta la carpeta `aufnahmen` en la herramienta.

## Receta 3: Clonar tu propia voz

Estos programas leen palabras nuevas con tu timbre; como muestra basta una grabación tuya corta y limpia.

- **Chatterbox Multilingual** (programa y modelo MIT, uso privado y comercial): 23 idiomas, entre ellos alemán y español. Unos 3 GB, necesita PyTorch; con tarjeta gráfica va mucho más rápido.
- **Pocket TTS** (programa MIT, modelo CC-BY-4.0, requiere atribución): alemán y español, funciona en el procesador sin tarjeta gráfica. La descarga del modelo pide una cuenta gratuita con el proveedor del modelo.

Pasos en ambos: graba la muestra (de 10 a 30 segundos, en un lugar tranquilo), crea un archivo por cada línea de la lista con el nombre de `datei` e importa. Escucha algunos resultados: las voces clonadas no siempre aciertan con palabras cortas sueltas; esas las grabas tú rápidamente en el programa.

## Receta 4: Entrenar tu propio modelo de Piper

Para pacientes: una voz de Piper totalmente tuya.

- **Piper Recording Studio** (MIT): te lee frases que tú repites; de una a dos horas de grabaciones son un buen comienzo.
- **Entrenamiento** con las herramientas de Piper (GPL-3.0): un modelo existente se sigue entrenando con tus grabaciones. Necesita PyTorch y una tarjeta gráfica y tarda horas.
- Aviso: si en lugar de tu tarjeta gráfica usas un servicio de cómputo gratuito en internet, subes tu voz allí; entonces sale de tu dispositivo.

El modelo terminado se usa como en la receta 2.

## Receta 5: Conversión de voz

**RVC** y **Applio** (ambos MIT) convierten una voz sintetizada, por ejemplo la de la receta 2, en tu timbre. Necesitas unos diez minutos de grabaciones propias y un entrenamiento, de preferencia con tarjeta gráfica. Es el camino más laborioso y aquí solo se menciona para completar.

## Resumen

| Programa | Licencia | Privado / comercial | Tamaño | Necesita |
| --- | --- | --- | --- | --- |
| Audacity | GPL | sí / sí | unos 40 MB | micrófono |
| Piper + voz | GPL-3.0, voces CC0 / Apache-2.0 / Unlicense | sí / sí | unos 60 MB por voz | nada especial |
| Chatterbox Multilingual | MIT | sí / sí | unos 3 GB | PyTorch, tarjeta gráfica recomendable |
| Pocket TTS | MIT, modelo CC-BY-4.0 | sí / sí (con atribución) | unos cientos de MB | PyTorch, cuenta gratuita para la descarga |
| Piper Recording Studio + entrenamiento | MIT / GPL-3.0 | sí / sí | varios GB | PyTorch, tarjeta gráfica |
| RVC / Applio | MIT | sí / sí | varios GB | PyTorch, tarjeta gráfica recomendable |

## Si algo no encaja

- **«sin palabra correspondiente»**: el nombre del archivo no coincide con la lista. Después de cambiar una palabra, descarga la lista otra vez; el nombre depende del texto.
- **«no aceptadas»**: el archivo no tiene un formato admitido, pesa más de 2 MB o es un WAV de más de 15 segundos.
- **Un 🔊 se queda callado**: tu navegador no reproduce el formato; entonces lee la voz del sistema. WAV y MP3 se reproducen en todas partes.
