# Me Goos-ta Deutsch – Guía

Actualizada: 21/10/2026 · programa e interfaz versión 2.2 · Alemán: `LEITFADEN.md` · Inglés: `LEITFADEN_en.md`

¡Qué bueno que estás aquí! Esta guía te acompaña desde el primer doble clic hasta la carta terminada, paso a paso y sin tecnicismos. No tienes que leerla de principio a fin: salta a la parte que necesites. Y tranquilo: aquí nadie te apura; cada paso va a tu ritmo, como un ganso que pasea a gusto.

## Panorama general

Me Goos-ta Deutsch convierte imágenes con un juego de palabras «Gans …» en tarjetas de estudio listas para imprimir: adelante la imagen, atrás la palabra en {{español}} con un ganso travieso en la esquina. Aquí «español» siempre significa el español que se habla en México; por eso las sugerencias de traducción prefieren palabras mexicanas. («Gans» significa ganso en alemán y suena igual que «ganz», que quiere decir «bastante» o «muy». De ahí sale el chiste, y nunca pasa de moda.) Las cartas nuevas se hacen en cuatro pasos, todos en la interfaz:

| Paso | Qué pasa |
| --- | --- |
| 1 Preparar imágenes | Agrega una imagen o muchas a la vez, o deja que **🪄 Crear ganso con IA** pinte una foto realista de ganso a partir de una descripción corta (sin conexión). El programa revisa formato, tamaño y nitidez, muestra el anverso y nombra cada archivo según el texto de la imagen. La palabra en {{español}} puede ir de una vez: escrita por ti o como sugerencia (🌐) |
| 2 Rotular cartas | Escribe las palabras en {{español}} que faltan o deja que el programa las sugiera. Revisa si caben en la carta y muestra el reverso en vivo |
| 3 Generar | En tres pasitos: elige un objetivo (impresión en casa, imprenta, hoja de control, tarjetas digitales …), ajusta, ¡vamos! Las imágenes que aún no están mejoradas las pule la IA (Real-ESRGAN) de paso |
| 4 Revisar e imprimir | Mira la hoja de control y luego imprime en casa, en una imprenta, o estudia en digital desde el celular |

Siempre a tu lado:

- **Tabla**: anverso y reverso de todas las cartas lado a lado, ideal para revisar las traducciones.
- **Mejora de imagen**: mejora imágenes por adelantado y compara antes/después.
- **Ideas**: guarda ideas a medias y termínalas después con calma.
- **Herramientas** y **Ayuda**: todo lo demás, desde el acceso desde el celular hasta la autoprueba.
- **Desinstalar**: la última pestaña, por si algún día quieres despedirte (¡ojalá que no!).

Al pasar el puntero sobre casi cualquier botón aparece una pequeña ayuda que explica qué hace.

| Resultado (carpeta `ausgabe/`) | Para qué |
| --- | --- |
| `Me-Goos-ta-Deutsch_Pruefbogen.pdf` | Hoja de control: anverso y reverso de cada carta, textos, nitidez de la imagen |
| `Me-Goos-ta-Deutsch_Heimdruck_A4_88x63.pdf` (o `_Letter_`) | Imprimir tú mismo en cartulina, 8 cartas por hoja, con marcas de corte |
| `Me-Goos-ta-Deutsch_Druckerei_88x63.pdf` | Para una imprenta: una página por cada lado de carta, con 3 mm de sangrado |
| `einzelbilder/` | Un PNG por cada lado de carta, para imprentas que piden imágenes en lugar de PDF |
| `digital/` | Paquete de Anki, página de estudio para el navegador, PDF de pantalla y, si quieres, tablas para otras apps de estudio |

La interfaz habla inglés, alemán y español; cámbiala arriba a la derecha (EN · DE · ES). En el primer inicio está en inglés; el asistente de bienvenida te pregunta enseguida tu idioma favorito. Todo lo anterior (la guía «LIES MICH ZUERST», o sea «léeme primero», los mensajes del archivo de inicio, la ventana de instalación y la pantalla de carga de la app del celular) también empieza en inglés y luego sigue tu elección. Las cartas, claro, no cambian.

## Instalación (una sola vez)

No tienes que instalar nada antes, ni siquiera Python. En el primer inicio, el archivo de inicio prepara todo solo: un Python propio en tu carpeta de usuario (**sin permisos de administrador**; otras instalaciones de Python no se tocan), los paquetes y un icono para iniciar. Tarda de 3 a 10 minutos y necesita internet una sola vez (unos 90 MB): tiempo perfecto para un café. Los extras más grandes, como la mejora de imagen con IA, son **herramientas**: solo descargas lo que de verdad quieres (ver «Herramientas opcionales»). El archivo **«LIES MICH ZUERST»** (léeme primero) del paquete lo muestra todo otra vez con imágenes.

**¿Dónde se descarga?** La página de descarga https://lukasdiegans.github.io/me-goos-ta-deutsch/download/ tiene un solo ZIP para Windows, macOS y Linux (gratis, desde GitHub Releases), con los pasos para tu sistema y la suma de verificación SHA-256. Después también encuentras el enlace en el programa, en **Ayuda → «Acerca del programa»** (en la app para celular: **Más → «Descárgalo para tu computadora»**).

**Windows 11 y 10**

1. **Desbloquea el ZIP** (importante en Windows 11): clic derecho en el ZIP → «Propiedades» → abajo, en «Seguridad», marca **«Desbloquear»** → «Aceptar». Si no, el Control inteligente de aplicaciones bloquea el archivo de inicio (ver «Inicio en Windows y Control inteligente de aplicaciones»).
2. **Descomprime el ZIP:** clic derecho → «Extraer todo …», por ejemplo en `Documentos`.
3. **Doble clic en `Me Goos-ta Deutsch - Windows`.** Una ventana muestra la instalación paso a paso, y un patito nada mientras algo carga. Luego la interfaz se abre en el navegador, y en el escritorio (y en el menú Inicio) aparece el icono **«Me Goos-ta Deutsch»**.
4. Desde entonces: doble clic en el icono del escritorio; la interfaz arranca en segundos, sin ventana negra.

**Mac:** descomprime el ZIP con doble clic y luego haz doble clic en `Me Goos-ta Deutsch - Mac`. Si macOS no lo abre: desde macOS 15 en Configuración del Sistema → Privacidad y seguridad → «Abrir igualmente»; hasta macOS 14 con Control-clic → «Abrir». Siempre funciona: abre la app «Terminal», escribe `sh `, arrastra el archivo y pulsa Intro. Después «Me Goos-ta Deutsch» está en Launchpad y en la carpeta «Aplicaciones» de tu carpeta de usuario.

**Linux:** descomprime el ZIP, abre una terminal en la carpeta y escribe `sh "Me Goos-ta Deutsch - Linux.sh"`, o clic derecho en el archivo → «Ejecutar como un programa» (la terminal se abre sola). Después «Me Goos-ta Deutsch» está en el menú de aplicaciones. Solo necesita `curl` o `wget` y `tar`, que casi siempre ya están.

**¡Bienvenido!** La primera vez que abres el programa te saluda un pequeño asistente: elige tu idioma, decide si el programa se abre en el navegador o en su propia ventana, marca las herramientas que quieras (no hay nada preseleccionado), haz un recorrido corto y ¡listo! «Preguntar después» lo muestra otra vez en el siguiente inicio.

**¿Todo funciona?** En «Herramientas» haz clic en «Iniciar autoprueba». Al final dice «ALLE TESTS BESTANDEN» (todas las pruebas superadas): todo en verde.

**Lo que el programa de inicio reconoce cada vez:** primer inicio → instala todo · la interfaz ya está abierta → solo abre el navegador · versión nueva o carpeta nueva → solo completa lo necesario y ofrece pasar tus cartas de la carpeta anterior · algo falta o está dañado → lo repara solo · dos inicios a la vez → el segundo espera con paciencia. Python, registros y ajustes están en `%LOCALAPPDATA%\Me-Goos-ta-Deutsch` (Mac: `~/Library/Application Support/Me-Goos-ta-Deutsch`, Linux: `~/.local/share/me-goos-ta-deutsch`); tu trabajo, en la carpeta `Programm` (imágenes, `karten.csv`, `ausgabe`).

La interfaz sigue funcionando en segundo plano aunque cierres la pestaña del navegador; ⏻ arriba a la derecha la cierra. Iniciar de nuevo simplemente vuelve a abrir el navegador.

## Instalar una versión nueva (actualización)

Tu trabajo está en la carpeta `Programm`: la lista de cartas `karten.csv`, las imágenes en `bilder/`, tus ideas en `ideen/`, archivos de impresión e imágenes mejoradas en `ausgabe/`, los ajustes en `ui_einstellungen.json` y tu imagen de ganso en `assets/`. La descarga de una versión nueva no trae nada de eso: sus cartas de ejemplo vienen como `beispiel-karten.csv` y `beispiel-bilder/` y solo se usan en una carpeta totalmente nueva. Así no se pierde nada al actualizar.

**La versión nueva** siempre está en la página de descarga; en el programa, en **Ayuda → «Acerca del programa»**, enlace «Versión más reciente para Windows, macOS y Linux». Si hay una versión nueva te lo dice ahí el botón **«🔎 Buscar una versión nueva»**: solo tu clic pregunta una vez a GitHub (api.github.com) por la versión más reciente; nunca por sí solo, nunca en segundo plano, sin datos sobre ti ni tus cartas, y no se guarda nada. Si hay un ganso más nuevo, un enlace te lleva a la página de descarga; «¡Ganso al día!» significa que ya tienes el más reciente. El botón solo existe en la computadora (no en la app del celular ni con el acceso desde el celular).

**Lo más seguro:** antes descarga una copia completa en **Importar / exportar**. La puedes importar en cualquier lugar.

**Recomendado: descomprimir en una carpeta nueva**

1. Cierra la interfaz abierta (⏻ arriba a la derecha).
2. Desbloquea el ZIP nuevo (Windows: Propiedades → «Desbloquear») y descomprímelo con «Extraer todo …»; Windows propone solo una carpeta nueva.
3. Haz doble clic en el archivo de inicio de la carpeta nueva. Encuentra la carpeta anterior y pregunta si quieres pasar tus cartas: responde **Sí** (en la ventana de inicio basta con Intro). Se copian cartas, imágenes, ideas, imágenes mejoradas, ajustes y tu imagen de ganso. Python, paquetes y herramientas instaladas se reutilizan: no hay que descargar nada de nuevo.
4. Desde ahora el icono abre la versión nueva. La carpeta anterior queda sin cambios; bórrala cuando todo esté bien.

Tras pasar tus cartas, las cartas de ejemplo de la versión nueva quedan en `Programm/_beispiele/`. Con **No** la versión nueva empieza con las cartas de ejemplo; puedes pasar tus cartas cuando quieras **importando** una copia.

**También se puede: descomprimir sobre la carpeta anterior.** Al descomprimir, elige la carpeta que contiene tu carpeta anterior y «Reemplazar los archivos en el destino». Solo se reemplazan archivos del programa; lista de cartas, imágenes, ideas, archivos de impresión, ajustes e imagen de ganso se quedan como están. Después haz doble clic una vez en el archivo de inicio.

## Inicio en Windows y Control inteligente de aplicaciones

Windows 11 tiene una protección llamada **Control inteligente de aplicaciones** (Smart App Control). Bloquea archivos de inicio descargados de internet, como `.cmd`, si no están firmados. Windows reconoce «de internet» por una marca invisible que pone al descargar y que pasa a todos los archivos al descomprimir. Los programas firmados sí pueden ejecutarse, entre ellos el Python oficial de python.org que usa el archivo de inicio.

| Opción | ¿Permisos de administrador? | Valoración |
| --- | --- | --- |
| Desbloquear el ZIP antes de descomprimir: Propiedades → «Desbloquear» → Aceptar, y luego descomprimir | no | **recomendado**: después ningún archivo lleva la marca |
| Desbloquear solo el archivo de inicio: clic derecho en `Me Goos-ta Deutsch - Windows` → Propiedades → «Desbloquear» → Aceptar | no | bien si ya descomprimiste: después el archivo de inicio quita la marca de todos los archivos del programa |
| Icono del escritorio (se crea en el primer inicio) | no | para cada inicio posterior: se crea en tu computadora y no lleva marca |
| «Ejecutar como administrador» | sí | no hace falta |
| Desactivar el Control inteligente de aplicaciones | sí | no recomendado: te protege de software malicioso |

Bibliotecas como Pillow y NumPy contienen partes de programa (DLL) que Microsoft no firma. Si el Control inteligente de aplicaciones bloquea una, el programa de inicio lo detecta, prueba solo versiones anteriores y muy usadas y, si hace falta, te explica las demás opciones. Si solo se bloquea la biblioteca de vista previa pypdfium2, la desactiva: los PDF se generan de todos modos y el programa dibuja él mismo la vista previa del reverso.

## La interfaz

| Área | Qué haces ahí |
| --- | --- |
| Mis cartas | Todas las cartas con vista previa (un clic las voltea), calidad de imagen y avisos. Editar, imprimir o pausar, cambiar el orden, quitar de la lista; cada cambio se guarda al instante |
| 🎓 Aprender | Aprende tus cartas como en Anki: cartas pendientes de hoy y nuevas, mazos propios, estadísticas, ajustes (herramienta «Aprender cartas») |
| Tabla | Anverso y reverso de todas las cartas lado a lado: comparar, editar directo, marcar traducciones como «revisada», filtrar, buscar, imprimir |
| Mejora de imagen | Mejorar imágenes por adelantado, estado por imagen, comparación antes/después |
| 1 Preparar imágenes | Agregar imágenes nuevas (muchas a la vez está bien), revisar, nombrar, rotular de una vez, agregar; «🪄 Crear ganso con IA», «🎨 Diseñar imagen GANS» |
| 2 Rotular cartas | Escribir la palabra en {{español}} o pedir sugerencia, ver el reverso en vivo, guardar |
| Ideas | Juntar ideas, completarlas y convertirlas en cartas; seguir con cartas sin terminar |
| 3 Generar | Elegir objetivo, ajustar, ¡vamos!; a la derecha, el registro te cuenta lo que pasa |
| 4 Revisar e imprimir | Hoja de control y lista de revisión, imprimir en casa o en imprenta, estudiar en digital |
| Herramientas | Herramientas opcionales (mejora de imagen, traducción, imágenes IA), importar / exportar, imagen GANS, inicio del programa, abrir en el celular, ajustes de la traducción, autoprueba, ZIP del proyecto, carpetas |
| Ayuda | Esta guía en el idioma elegido, la especificación, estado del programa; si la carga tarda demasiado, usa «Cancelar» o «Intentar de nuevo» |
| Desinstalar | Respaldar y quitar limpiamente |

Los números del menú muestran lo pendiente: en el paso 1 las imágenes que aún no se agregaron, en el paso 2 las cartas sin palabra, en «Ideas» tus ideas, en «Tabla» las palabras traducidas automáticamente que esperan tu revisión.

## Paso 1: Preparar imágenes

Arrastra imágenes al recuadro o haz clic y elígelas: una o muchas. ¿No tienes una foto que encaje? **«🪄 Crear ganso con IA»** pinta una y **«🎨 Diseñar imagen GANS»** pone el juego de palabras sobre una foto (ambos más abajo). Cada imagen tiene una fila con una vista previa pequeña del anverso:

1. Escribe el **texto de la imagen** tal como aparece, por ejemplo «Gans ausgeschlafen». De ahí sale el nombre del archivo: `gans-ausgeschlafen.jpg` (minúsculas, ä → ae, ö → oe, ü → ue, ß → ss, espacio → guion). Si el archivo ya se llama «gans-….jpg», el texto ya aparece escrito.
2. **Palabra en {{español}}** (opcional): escríbela aquí mismo o deja que 🌐 te la sugiera. Si queda vacía, la palabra va en el paso 2.
3. A la derecha ves el resultado de la revisión: **✓ Lista**, **! Avisos** o **✕ Revisa rápido**; en este último caso la imagen se puede agregar en cuanto se resuelva ese punto.
4. **«Detalles ▾»** muestra el original y el anverso en grande, la lista completa de revisiones, **girar** (↺ ↻) y el **recorte**: «Mostrar imagen completa» (los márgenes libres se continúan suavemente) o «Llenar la carta» (los bordes se recortan). ★ marca la recomendación para esa imagen.
5. **«Agregar»** crea esa carta. La imagen va a la carpeta `bilder/`, la carta a la lista.

Arriba de la lista, una barra muestra cuántas imágenes están listas. **«🌐 Traducir todas»** sugiere una palabra para cada imagen sin palabra; **«Agregar todas (n)»** agrega todas las listas de una vez.

La lista de revisión muestra palomitas verdes (todo bien), avisos grises, advertencias naranjas y puntos rojos. Mientras haya algo en rojo, la imagen espera antes de agregarse.

| Mensaje | Significado | Qué hacer |
| --- | --- | --- |
| El programa no puede leer fotos HEIC/HEIF | formato de iPhone | guárdala como JPG: iPhone → Ajustes → Cámara → Formatos → «Más compatible», o en la computadora con la app Fotos. Si subes desde el celular con el acceso por wifi, el iPhone por lo general convierte a JPG solo |
| Este archivo no se puede leer como imagen | archivo dañado o no es imagen | guarda la imagen otra vez o elige otra |
| más de 40 MB / más de 60 megapíxeles | archivo muy grande | redúcela un poco (p. ej. a 3000 px de ancho) |
| demasiado pequeña para una carta (menos de 100 px) | imagen diminuta | busca una versión más grande |
| … ppi en la impresión | fuente algo pequeña | funciona igual; con una imagen más grande queda bien nítida |
| … ya existe en la carpeta de imágenes | nombre ocupado | cambia el texto o marca «reemplazar la imagen existente»; la versión anterior va a `bilder/_entfernt/` |
| Esta misma imagen ya está en la carpeta | repetida | «Descartar» si de verdad es la misma |
| La imagen es vertical y la carta horizontal | formato vertical | está bien; si solo está girada, gírala con ↻ |
| «Llenar la carta» recorta el … % | recorte fuerte | revisa en la vista previa que el texto se vea completo; si no, «Mostrar imagen completa» |
| Bordes negros / transparencia / CMYK / orientación de la cámara / GIF, BMP, TIFF | se corrige o se convierte solo | nada, el programa se encarga |

Lo que importa para la calidad: el área de imagen de una carta mide 957 × 661 píxeles a 300 dpi. Desde unos 960 píxeles de ancho la imagen sale nítida; las más pequeñas se amplían con IA. El formato horizontal de 3 : 2 llena mejor la carta. El chiste debe verse grande en la imagen: se imprime como máximo a 8,1 cm de ancho.

## Diseñar imagen GANS

Con **«🎨 Diseñar imagen GANS»** (paso 1, Ideas o Herramientas) conviertes una foto de ganso en una imagen de carta con el chiste, ¡fácil como un ganso en el agua!:

1. Elige una foto o arrástrala a la ventana.
2. Elige el **recorte** (cuadrado, carta horizontal, vertical); arrastra la imagen para moverla y usa la rueda del ratón o el control para el zoom.
3. Escribe el texto después de **GANS**: aparece en mayúsculas («GANS SEHR HEISS»). Arrastra el texto sobre la imagen para colocarlo; tamaño, fuente y color los eliges tú.
4. **«Como carta nueva (paso 1)»** pasa la imagen al paso 1, **«Guardar como idea»** crea una idea y **«Descargar»** guarda el archivo. El nombre sigue la regla de las cartas: `gans-sehr-heiss.jpg`.

Si la imagen viene de **«Crear ganso con IA»**, ya está colocada: recorte «Carta horizontal» y palabra ya escrita. Abierto desde el editor de cartas, el botón principal es **«Usar para esta carta»**: la imagen con la palabra pasa a ser la imagen nueva de esa carta.

## Crear ganso con IA

¿No tienes una foto que encaje? **«🪄 Crear ganso con IA»** (paso 1) o **«🪄 Con IA …»** (editor de cartas) te pinta una foto realista de ganso, sin conexión y en tu propia computadora. Una sola vez instalas la herramienta **«Imágenes IA»** (Herramientas → Herramientas opcionales) con el modelo Segmind Vega + VegaRT (licencia Apache-2.0, unos 3,5 GB); después ya no hace falta internet.

1. Escribe la **palabra de la carta** después de «GANS», p. ej. «alt». No se pinta en la imagen (el modelo no escribe texto limpio), sino que la pones limpia después.
2. **Descripción en inglés:** ¿cómo y dónde está el ganso? Por ejemplo «swimming on a lake at sunset», «sleeping in a nest of straw», «standing in fresh snow». Puedes agregar luz, estación, clima o ambiente («morning fog», «golden hour»), y mejor di lo que debe verse y no lo que no. ¿Sin inglés a la mano? Escribe en español y haz clic en **«🌐 Al inglés»** (solo con la traducción activada; se envía solo esta descripción). «… de 75 tokens» muestra si todo llega al modelo.
3. **«Sin personas»** (recomendado, activado de forma predeterminada) mantiene lejos a la gente, con la redacción y un prompt negativo suave; tarda unos 20 segundos más. No se puede descartar del todo: si aun así aparece alguien, pide otra variante.
4. **«🪄 Crear ganso»**: en una laptop normal, una imagen tarda unos 1–2 minutos. Después de cada paso ves una vista previa; puedes cerrar la ventana y seguir trabajando, o **cancelar** en cualquier momento.
5. ¿Te gusta el ganso? **«✍️ Poner la palabra en la imagen …»** lo abre en «Diseñar imagen GANS»; desde ahí como carta nueva o, desde el editor de cartas, para esa carta. **«Como carta nueva sin palabra»** o **«Usar para esta carta»** toma la imagen directamente; se revisa como cualquier foto. **«🎲 Otra variante»** pinta una nueva versión y **«Descargar»** guarda la imagen. Misma descripción + misma semilla da la misma imagen.

| Lo hace bien | Ahí le cuesta |
| --- | --- |
| un ganso en un entorno natural, cerca y nítido | texto y letras en la imagen |
| luz, estación del año, clima y paisaje | cantidades exactas y varios animales haciendo algo juntos |
| posturas sencillas: parado, nadando, volando, durmiendo, comiendo, mirando con curiosidad | actividades humanas (andar en bici, leer), sostener cosas con el pico o las patas |
| | razas concretas, el mismo ganso en varias cartas y, de vez en cuando, una pata o un cuello de más: entonces otra variante |

**Prompt estándar (para curiosos):** «Editar prompt estándar …» muestra la plantilla con la que el programa le habla al modelo: `{description}` es tu descripción y `{word}` la palabra de la carta (no se usa de forma predeterminada). Puedes guardar tu propia versión y recuperar la estándar en cualquier momento con «Restaurar estándar».

Bueno saber: generar necesita unos 3 GB de memoria (se recomiendan 8 GB en la computadora). El modelo se guarda en la carpeta de datos, se conserva con versiones nuevas del programa y se elimina al desinstalar. Con el acceso desde el celular todo funciona igual: la computadora hace el trabajo.

**Instalar/quitar la herramienta:** Si la herramienta «Imágenes IA» aún no está, los botones siguen visibles. «🪄 Crear ganso» o «Instalar la herramienta «Imágenes IA» …» en la ventana de IA pregunta primero –con un aviso si la memoria es justa o no hay espacio libre suficiente–, descarga el modelo por la fila de espera y luego vuelve a abrir la ventana de IA con lo que escribiste. Para quitarla: Herramientas → Herramientas opcionales → «Imágenes IA» → «Desinstalar …» borra el modelo y las imágenes intermedias de `ausgabe/.ki-bild`; tu versión propia del prompt se queda.

## Paso 2: Rotular cartas

Aquí aparecen todas las cartas a las que todavía les falta la palabra en {{español}}, y cada carta que abras en «Mis cartas» con «Editar».

| Campo | Contenido |
| --- | --- |
| Palabra en {{español}} | Va en el reverso. `/` separa la palabra principal (grande) de las alternativas (pequeñas debajo), p. ej. `viejo / anciano`; `\|` pone un salto de línea en la palabra principal. 🌐 sugiere una traducción |
| Texto de la imagen (alemán) | Para revisar en la hoja de control; no se imprime |
| Nota | Solo para ti, p. ej. el tipo de palabra; no se imprime |

Los botones á é í ó ú ñ ü ¿ ¡ insertan caracteres especiales, útiles con cualquier teclado. El reverso se actualiza mientras escribes. «Guardar carta» (o Intro) guarda la carta en `karten.csv`; «Después» la deja esperando con paciencia. Con varias cartas, **«🌐 Traducir todas»** sugiere una palabra para todos los campos vacíos y **«Guardar todas (n)»** guarda todas las listas de una vez.

**Cambiar imagen:** debajo de las vistas previas, **«Cambiar imagen …»** trae una imagen nueva para la carta, o simplemente arrástrala sobre la vista previa. Se revisa como en el paso 1, con giro y recorte; la palabra, el texto y la nota se quedan. «Usar la imagen nueva» guarda la anterior en `bilder/_entfernt/` y «Deshacer» la recupera. **«🪄 Con IA …»** pinta en su lugar una imagen nueva de ganso para esa carta (ver «Crear ganso con IA»).

| Mensaje | Qué hacer |
| --- | --- |
| Solo falta la palabra en {{español}} | escríbela: sin palabra la carta no se imprime |
| «ä» no existe en español | ¿error de dedo? El español tiene á é í ó ú ü ñ, pero no ä, ö, ß |
| La palabra principal es algo larga para la carta | acórtala o divídela con `\|` en un buen lugar |
| Las alternativas son algo largas / mucho texto | acorta o quita alternativas |
| más de 2 alternativas | quédate con las dos más importantes |
| En español las preguntas empiezan con «¿» | p. ej. `¿cómo estás?` |
| el carácter no se puede imprimir | quita emojis y caracteres raros |
| El texto no puede empezar con = + - @ | protección contra fórmulas de Excel (también en la nota): quita el carácter del inicio |
| todavía es igual al texto alemán | ¡hora de traducir! |
| ya está en la carta … | solo un aviso: se permiten palabras repetidas |

**Editar la lista a mano (para usuarios avanzados):** cada carta es una fila de `karten.csv` (punto y coma como separador, UTF-8). Columnas: `bild` (obligatoria), `de`, `es` (obligatoria), `notiz`, `fit` (`contain` o `cover`) y `uebersetzung` (`automatisch`, `geprüft` o vacía). Una fila que empieza con `#` se omite. En Excel elige «CSV UTF-8» al guardar; si no, se pierden ñ, á y ü. Luego recarga la interfaz.

```csv
bild;de;es;notiz;uebersetzung
gans-alt.jpg;Gans alt;viejo;Adjektiv;geprüft
gans-arg-hunger.jpg;Gans arg Hunger;muchísima hambre / me muero de hambre;Wendung;automatisch
```

## Juntar ideas

Las buenas ideas llegan de repente, y aquí tienen su lugar. Una idea solo necesita **una imagen, una palabra en alemán o una en {{español}}**; lo demás puede venir después.

- **«+ Idea nueva»** crea una idea vacía; basta con escribir, se guarda al salir del campo. La imagen se agrega con «Elegir imagen …», arrastrándola al recuadro o con «Diseñar imagen GANS …».
- **¿Ya existe la palabra?** Mientras escribes, el programa revisa al instante si ya existe como carta o idea; mayúsculas, diéresis y «Gans» no importan. Así «Gans alt» no se hace dos veces por accidente.
- **🌐 junto al texto alemán** convierte la palabra en {{español}} en una sugerencia para el texto de la imagen («viejo» se vuelve «Gans alt»). Ideal cuando primero se te ocurre la palabra en {{español}}.
- Cuando están la imagen, el texto de la imagen y la palabra en {{español}}, se activa **«Hacer carta»**: la idea pasa las mismas revisiones que en los pasos 1 y 2 y después aparece en **Mis cartas**.
- **«Descartar»** se puede deshacer con «Deshacer».
- Abajo están todas las **cartas sin terminar** de «Carta nueva» con «Seguir →».

**Lista de palabras: muchas ideas de una vez.** ¿Ya tienes una lista de vocabulario? **«📋 Lista de palabras …»** la convierte en ideas de un jalón, con o sin traducción.

1. Elige un archivo (CSV, TSV o texto) o arrástralo, o simplemente pega la lista en el campo y pulsa «Revisar».
2. La **vista previa** muestra cada línea con su estado: *nueva*, *repetida en la lista*, *ya es idea*, *ya es carta* o *con errores* (con el motivo). Las líneas nuevas van marcadas, lo demás lo decides tú; las líneas con errores se corrigen en la lista.
3. Si algo no cuadra, ayudan las opciones de arriba: separador, primera línea como encabezado, una sola columna es alemán o {{español}}, intercambiar columnas, «Gans» delante. Cada cambio vuelve a revisar la lista.
4. **«Crear n ideas»** y listo. El aviso de después trae **«Deshacer»**: retira la lista completa; las ideas que hayas cambiado mientras tanto se quedan.

| En la lista | Resultado |
| --- | --- |
| `alt;viejo` | Gans alt → viejo |
| `müde` | Gans müde, la palabra en {{español}} viene después |
| `Alemán;Palabra;Nota` (primera línea) | encabezado: define el orden de las columnas |
| `rot;rojo;Farbe` | tercera columna = nota |
| `# Farben` | comentario, se omite |

Los separadores pueden ser punto y coma, tabulador, coma, « = » o « – »; como máximo 500 palabras y 1 MB por lista, nunca se acorta nada en silencio. La palabra siempre es del idioma actual de las cartas; para otro idioma, cambia antes el idioma de las cartas.

**🌐 Traducir todas** aparece en cuanto hay ideas con texto en alemán pero sin palabra en {{español}}: un clic trae una sugerencia para todas (con el mismo consentimiento de siempre). Solo se llenan los campos que en ese momento sigan vacíos, marcados como «automática – revisar». Si se agota la cuota diaria del servicio, el programa se detiene sin problemas y te dice cuántas ya están.

## Traducción automática

**Cómo funciona:** 🌐 junto al campo «Palabra en {{español}}» (en el paso 1, el paso 2, Ideas y la tabla) trae una sugerencia. Aparece en el campo; debajo ves la fuente y más opciones para elegir. La primera vez el programa pregunta si puede activar la traducción y explica qué se envía. Ahí también puedes marcar «Traducir automáticamente las cartas nuevas a partir de ahora».

**Revisar sigue siendo importante:** cada palabra que tomas queda marcada «traducida automáticamente: revisar» (en «Mis cartas», en la tabla y en la hoja de control) hasta que la marques como «revisada» en la tabla. Los diccionarios no siempre aciertan con la palabra que se usa en México; que alguien que hable {{español}} le eche un vistazo vale oro.

| Servicio | Para qué | Cuenta | Operador |
| --- | --- | --- | --- |
| Wiktionary | palabras sueltas: varios significados y alternativas, mantenido por personas | no | Wikimedia Foundation |
| MyMemory | frases de varias palabras (automático) | no; unos 5000 caracteres al día | Translated srl (Italia) |
| DeepL | traducción automática muy buena | tu propia clave gratuita «DeepL API Free» | DeepL SE (Alemania) |

«Automático (recomendado)» pregunta primero a Wiktionary con una o dos palabras; con frases más largas, a DeepL (si guardaste una clave) o a MyMemory. Todo lo demás en **Herramientas → Traducción automática**.

**Seguridad y privacidad**

- Sin tu permiso no se envía nada a internet; puedes retirarlo cuando quieras en Herramientas.
- Solo se envía la palabra o la frase sin «Gans», por ejemplo «aufgeregt», de máximo 80 caracteres. Nada de imágenes, nombres de archivo, notas ni datos personales.
- Solo conexiones cifradas (HTTPS con verificación de certificado) a las direcciones fijas de los tres servicios; las respuestas se filtran (sin HTML, sin fórmulas, sin caracteres de control).
- Una sugerencia solo entra en la lista de cartas cuando tú la tomas.
- Ajustes y clave de DeepL quedan en tu carpeta de usuario, legibles solo por tu cuenta; nunca en la carpeta del proyecto ni en el navegador. Las sugerencias guardadas (hasta 90 días) se pueden borrar en Herramientas.

**Instalar/quitar la herramienta:** Tu permiso es a la vez la instalación de la herramienta «Traducción automática»: con el primer 🌐 o en Herramientas → Herramientas opcionales. «Desinstalar …» retira el permiso y borra los ajustes, la clave de DeepL y las sugerencias guardadas. Los botones 🌐 se quedan y la próxima vez simplemente vuelven a preguntar.

## Pestaña «Tabla»: revisar traducciones

La tabla muestra cada carta en una fila: número, imagen pequeña, **anverso (alemán) → reverso ({{español}})**, nota y revisión.

- **Editar:** haz clic en una celda y escribe; se guarda al salir del campo (Intro = listo, Esc = descartar). Valen las mismas revisiones que en el paso 2.
- **🌐** sugiere una palabra para esa fila; **«🌐 Traducir todas»** llena todos los reversos vacíos.
- Marca **«revisada»** en cuanto la traducción esté bien. Si la palabra cambia después, la marca desaparece.
- **Filtrar, buscar y ordenar** con un clic en el encabezado de una columna; «Mostrar imágenes» muestra u oculta las imágenes pequeñas.
- **«Imprimir tabla»**: útil para dársela a alguien que la revise. La vista **«Compacta»** pone cada carta en una línea, y ☐ se puede marcar en papel.

## Pestaña «Mejora de imagen»

Cada anverso se prepara antes de imprimir: se quitan bordes negros, se amplía con **Real-ESRGAN x4plus** (el modelo también quita bloques JPEG y ruido), se ajusta al tamaño de impresión, se enfoca con cuidado y se corrigen los colores. La primera vez tarda unos **1 a 4 minutos por imagen** (según el procesador); después el resultado sale al instante de la memoria intermedia.

En esta pestaña puedes hacerlo por adelantado mientras sigues trabajando:

1. Arriba están **Ampliación con IA** (Auto, Real-ESRGAN, Real-ESRGAN ×2, FSRCNN, Apagado) y **Calidad** (Apagado, Estándar, Fuerte). También valen para «Generar».
2. Elige cartas con la casilla de arriba a la izquierda de la imagen, o con «Elegir todas» / «Elegir las no mejoradas».
3. **«✦ Mejorar seleccionadas (n)»** empieza. Debajo ves cuánto tarda más o menos. «Cancelar» conserva todas las imágenes ya listas.

Cada imagen lleva una banda: **mejorada** · **otro ajuste** · **sin mejorar** · **falta la imagen**. Un clic muestra **antes y después** superpuestos; mueve la línea divisoria con el control. Al generar, las imágenes que faltan se mejoran de todos modos; la pestaña solo te ahorra la espera.

**Instalar/quitar la herramienta:** Real-ESRGAN es la herramienta «Mejora de imagen». Si falta, la pestaña muestra arriba un recuadro con «Instalar» (unos 64 MB) y la versión más rápida ×2. Si empiezas de todos modos, el programa pregunta: «Instalar y seguir» o «Solo ampliar (sin la herramienta)»; entonces trabaja el FSRCNN integrado. Lo mismo vale al generar con Real-ESRGAN elegido a propósito. «Desinstalar …» (Herramientas → Herramientas opcionales) borra los modelos, su copia en la carpeta de datos y las imágenes mejoradas con ellos en la memoria intermedia; los PDF de impresión ya hechos se quedan.

## Paso 3: Generar

Generar va en tres pasitos:

1. **¿Qué quieres crear?** Elige un mosaico:

| Objetivo | Resultado |
| --- | --- |
| Todo para imprimir | PDF para imprenta, impresión en casa, hoja de control y plantillas de una vez; perfecto si todavía no decides |
| PDF para imprenta | Una página por cada lado de carta con sangrado, más imágenes sueltas (PNG) |
| Impresión en casa | Varias cartas por hoja para tu impresora, A4 o Carta (Letter) |
| Hoja de control | Resumen para revisar antes de imprimir |
| Tarjetas digitales | Estudiar sin papel: Anki, página de estudio, PDF de pantalla, tablas para otras apps |
| Plantillas vacías | Guías para tus propios diseños en otro programa |

2. **Ajustes finos** (opcional; los valores predeterminados casi siempre sirven): solo aparecen los ajustes que corresponden a tu objetivo, cada uno con explicación. Todo se guarda solo; «Restablecer todos los ajustes» vuelve a lo predeterminado.
3. **¡Vamos!** Con «Solo estas cartas» (p. ej. `11-14`) solo se hacen las cartas nuevas. A la derecha el registro muestra qué pasa; al final dice «Listo en … ¡Bien hecho!».

**Imagen del ganso en el reverso** (en «Orientación y reverso»): el ganso dibujado (predeterminado) o una imagen tuya. El ganso dibujado nada en un pequeño estanque abajo a la derecha y mira la palabra; con mucho texto se hace un poco más pequeño en su esquina: la palabra siempre queda libre sobre un azul tranquilo. **«Cargar imagen de ganso …»** o arrastra una imagen al recuadro; lo ideal es una imagen tranquila, más bien clara, horizontal y de al menos 960 × 660 píxeles. El programa la revisa, la reduce a máximo 2400 píxeles y la guarda sin metadatos (por ejemplo, sin datos de ubicación). **«Usar el ganso dibujado»** regresa al original y **«Imagen anterior»** recupera la última que reemplazaste.

| Ajuste | Cuándo |
| --- | --- |
| Papel A4 / Carta (impresión en casa) | Carta en EE. UU., Canadá, México y parte de Latinoamérica; también vale para la hoja de control |
| Ampliación con IA «FSRCNN (rápido)» | rápido en lugar de la mejor calidad, p. ej. para probar |
| Ampliación con IA «Real-ESRGAN ×2» | casi la misma calidad, unas 4 veces más rápido; descárgalo antes en Herramientas → Herramientas opcionales → Mejora de imagen «+ Más rápido ×2» |
| Calidad «Fuerte» | colores y nitidez más intensos; «Apagado» desactiva la mejora |
| Archivo de imprenta vertical | la plantilla de la imprenta pide formato vertical |
| Girar el reverso 180° | en la prueba de impresión el reverso sale al revés |
| Tamaño final | otro tamaño de carta en mm, p. ej. 74 × 52 |
| Borde blanco 0 | cartas sin borde |
| Desplazamiento horizontal/vertical (impresión en casa) | en la prueba, anverso y reverso no coinciden exactamente |
| Recalcular todas las imágenes | p. ej. después de una actualización |

Para expertos: «Para expertos: línea de comandos» muestra el comando correspondiente; sin interfaz `py gans_lernkarten.py` (Mac/Linux: `python3`), todos los parámetros con `--help`.

## Herramientas opcionales

Algunos extras ocupan mucho espacio o envían algo a internet. Por eso son **herramientas**: no vienen preinstaladas, se descargan cuando las pides y se quitan cuando quieras. Las pestañas y los botones siempre siguen visibles.

| Herramienta | Para qué | Tamaño |
| --- | --- | --- |
| ✨ Mejora de imagen (Real-ESRGAN) | la ampliación con IA más bonita para imprimir; sin la herramienta, el FSRCNN integrado mejora de forma más sencilla | unos 64 MB de descarga (y opcional «Más rápido ×2») |
| 🌍 Traducción automática | sugerencias para el reverso (Wiktionary, MyMemory, DeepL); instalar aquí significa: dar tu permiso | sin descarga |
| 🎨 Imágenes IA | imágenes realistas de gansos, sin conexión en tu computadora | unos 3,5 GB |
| 🗣 Idiomas (reverso) | más idiomas para el reverso, cada uno por separado (ver «Más idiomas») | 0–17 MB por idioma |
| 🎓 Aprender cartas | aprende tus cartas como con Anki (planificador FSRS); instalar aquí significa: activarla; desinstalar borra tu progreso (expórtalo antes si quieres conservarlo) | sin descarga |

- **La primera vez que abres el programa** pregunta una sola vez qué herramientas descargar de inmediato; no hay nada preseleccionado y «Después» está perfecto.
- **Herramientas → Herramientas opcionales** muestra cada una con su estado (no instalada · en espera · descargando … % · instalada) y el espacio que ocupa. «Instalar» la descarga por la **fila de espera**; mientras, sigues trabajando.
- **Si falta una herramienta** cuando la necesitas, el programa pregunta (para qué sirve, tamaño, ubicación, tiempo). «Instalar y seguir» la descarga y después continúa solo con lo que estabas haciendo.
- **«Desinstalar …»** pregunta antes y borra solo los archivos de la herramienta para liberar espacio. Tus cartas, imágenes e ideas se quedan, y puedes volver a instalarla cuando quieras.
- Los modelos o un permiso de una versión anterior cuentan como instalados de inmediato. La mejora de imagen guarda además una copia en la carpeta de datos: una versión nueva del programa la conserva sin descargar.

## Más idiomas

El reverso no tiene que ser en español. La herramienta **🗣 Idiomas (reverso)** ofrece 14 idiomas más: inglés, bajo alemán, francés, italiano, turco, sueco, noruego, polaco, ruso, japonés, chino, coreano, hindi y árabe estándar. El español siempre está incluido.

- **Herramientas → Herramientas opcionales → Idiomas** muestra cada idioma con su tamaño. Los idiomas con alfabeto latino quedan listos al instante («sin descarga»); los demás descargan su fuente por la fila de espera (1–17 MB).
- **«Usar en el reverso»** (o el selector **Reverso:** arriba en Mis cartas, el paso 2 y la tabla, visible en cuanto hay otro idioma además del español) convierte un idioma en el **idioma de las cartas**. Desde ese momento dice «Palabra en japonés» en vez de «Palabra en español» en todas partes, 🌐 traduce al nuevo idioma y «pendiente» cuenta las cartas sin palabra en ese idioma. Esta guía también habla entonces del idioma elegido.
- **Chips de idioma** («ES», «JA», «AR» …) muestran en cada carta en qué idiomas ya hay reverso: lleno = hay palabra, punteado = aún vacío, oscuro = idioma actual. En Mis cartas, un clic en un chip muestra el reverso en ese idioma.
- **Varios reversos:** una carta puede tener su propia palabra para cada idioma. En el paso 2 el campo del idioma de las cartas va grande arriba; debajo, **«Más idiomas»** abre un campo por cada idioma instalado, cada uno con su propio 🌐. La tabla muestra una columna por idioma y filtra con «falta en …».
- El árabe se escribe de derecha a izquierda; el japonés, el chino y el coreano se escriben con el método de entrada de tu sistema. La barra de caracteres especiales se adapta al idioma.
- **Quitar** un idioma borra solo su paquete. Tus palabras se quedan en `karten.csv` (una columna por idioma) y vuelven en cuanto lo instales de nuevo. Si era el idioma de las cartas, sigue el español.

### Imprimir y exportar en otros idiomas

- En el **Paso 3: Generar**, **Idioma del reverso** define el idioma de impresión: por defecto el idioma actual de las cartas, cualquier idioma instalado también sirve, y **«Todos los instalados»** pone en la cola una tarea por idioma.
- Cada idioma se imprime con su propia fuente del paquete de idioma (ruso Noto Sans, japonés/coreano/chino IBM Plex Sans, árabe IBM Plex Sans Arabic, idiomas con alfabeto latino e hindi Poppins). El hindi y el árabe se forman correctamente (letras unidas, sílabas) y el árabe va de derecha a izquierda; los números y las palabras latinas dentro se leen bien. El japonés y el chino cortan entre caracteres, nunca con un signo de puntuación al inicio de la línea. El tamaño de letra se calcula con el ancho real de los caracteres.
- Los nombres de archivo llevan el código del idioma: `…_Druckerei_88x63_ja.pdf`, `…_Pruefbogen_ar.pdf`, `einzelbilder_ru/`, `digital/…_Anki_ja.apkg`. **El español queda como siempre** (sin código): así todos los idiomas conviven tranquilos.
- **Imprimir código de idioma** (sección «Orientación y reverso»): un pequeño «JA», «AR»… arriba a la izquierda del reverso ayuda a ordenar mazos mezclados. «Auto» lo imprime solo si el reverso no está en español.
- La **hoja de control** indica el idioma («JA: …») y la **vista previa del reverso** ya muestra el idioma de las cartas con su fuente.
- **Digital:** el paquete de Anki recibe un mazo propio por idioma («Me Goos-ta Deutsch – japonés») y un tipo de nota con el campo del idioma, la página de estudio fija idioma y dirección de escritura, y `tabellen/karten_alle_sprachen.csv` contiene todos los idiomas lado a lado (una columna por código de idioma).

## Fila de espera

Para que tu computadora no sude la gota gorda, en segundo plano solo corre **una** tarea a la vez: generar, mejora de imágenes, autoprueba, descargar una herramienta o un ganso IA. Si inicias algo mientras otra tarea está en curso, simplemente se forma en la fila («En la fila de espera: lugar 2») y empieza sola cuando le toca. Los botones siguen libres.

- **⏳ n** arriba a la derecha muestra cuántas tareas están en curso o esperando. Un clic abre la ventana **Fila de espera**.
- **En curso:** título, progreso, duración y «Cancelar»; después empieza automáticamente la siguiente tarea.
- **En espera:** ▲ ▼ mueven una tarea, **«Siguiente»** la pasa al frente, **✕** la quita; **«Quitar todas las que esperan»** pregunta antes.
- **Terminado hace poco:** las últimas diez tareas con ✓ o ✕ y duración, además de «Ver resultado» o «Registro».
- No se puede poner la misma tarea dos veces en la fila: conserva su lugar. Si una tarea no puede empezar (p. ej. porque falta el modelo IA), aparece con ✕ en «Terminado hace poco» y la fila sigue.
- La fila solo existe mientras el programa está abierto. **Salir** pregunta antes si algo sigue en curso o esperando.

## Cambiar los colores

La interfaz puede ser tan colorida como quieras: **Herramientas → «🎨 Colores y apariencia»**. La página muestra cada elección al instante como vista previa; solo se guarda al pulsar **«Guardar»** (si cierras la ventana sin guardar, todo vuelve a como estaba).

- **Cielo de ganso** (estándar): los colores de siempre, sin cambios.
- **Noche de ganso** (oscuro), **Pradera** (verde fresco) y **Alto contraste** (negro sobre blanco, líneas marcadas).
- **Como el sistema:** claro u oscuro, según lo que tenga tu dispositivo.
- **Mis propios colores:** selectores para fondo, superficies (cartas, ventanas), texto, acento y botones, líneas, éxito (verde) y error (rojo). Lo que no cambies queda como en el estándar.
- La **comprobación de contraste** muestra qué tan bien combinan texto y fondo; desde 4,5 : 1 se lee bien, por debajo aparece «Atención: difícil de leer».
- **Restablecer estándar** devuelve todo al Cielo de ganso. La elección también vale en el celular (acceso desde el celular) y solo afecta a la interfaz; las cartas impresas no cambian.

## Paso 4: Revisar e imprimir

**Revisar: un vistazo rápido vale la pena, y cada carta será un éxito.** La hoja de control muestra el anverso y el reverso de cada carta lado a lado, los textos y la nitidez. La lista de revisión al lado te dice qué falta:

1. **Traducción:** ¿la palabra es correcta y así se dice en México? Lo más cómodo es la pestaña «Tabla». Las palabras traducidas automáticamente llevan una nota hasta que las marques como revisadas.
2. **Nitidez:** «… ppi en la impresión»: desde 180 ppi buena, de 120 a 179 aceptable, abajo algo justa (una imagen más grande ayuda).
3. **Prueba de impresión:** imprime una página en papel normal al 100 %; si todo cuadra, ¡adelante!

**Imprimir en casa** (`…_Heimdruck_…pdf`, 8 cartas por hoja):

- Imprime al 100 % o «Tamaño real», no «Ajustar a la página».
- A doble cara, volteo por el borde largo. Sin dúplex: primero los anversos, voltea el montón y luego los reversos.
- Una cartulina firme (unos 200–300 g/m²) hace que las cartas se sientan muy bien.
- Si anverso y reverso no coinciden exactamente: en Generar, en «Impresión en casa», ajusta el desplazamiento en mm. Reverso al revés → «Girar el reverso 180°».
- Corta por las marcas de corte, con regla y cúter o con una guillotina. Si quieres, redondea las esquinas.

**Imprimir en una imprenta** (`…_Druckerei_…pdf` o `einzelbilder/`): hay imprentas en línea para cartas de juego o de estudio personalizadas en muchos países, vivas donde vivas. Así encuentras una buena:

- **Términos de búsqueda:** «imprimir cartas personalizadas», «baraja personalizada», «imprimir tarjetas de estudio»; en inglés «custom playing cards», en alemán «Spielkarten individuell drucken».
- **Importante:** cada carta necesita **su propio anverso y reverso**, no un mismo reverso para todas.
- **Tamaño:** el formato póker de 63 × 88 mm sirve directo; otros tamaños se ajustan en Generar, en «Tamaño final».
- **Sangrado:** casi siempre 3 mm alrededor; ya está incluido en el PDF para imprenta (archivo de 94 × 69 mm, tamaño final 88 × 63 mm).
- **Orientación:** ¿la plantilla pide vertical? Activa «Archivo de imprenta vertical».
- **Subir:** como PDF o imágenes sueltas. Compara pedido mínimo, grosor, acabado y envío.
- **Revisa la vista previa:** sobre todo la dirección del reverso, y pide primero una muestra antes de todo el paquete.

## Aprender cartas

Con la herramienta **«🎓 Aprender cartas»** practicas tus cartas dentro del programa, tal como lo recomienda la investigación sobre el aprendizaje. El primer clic en **«Aprender»** del menú la activa (no se descarga nada). El número del menú muestra cuántas cartas tocan hoy.

**Cómo funciona (en palabras sencillas):** ves la imagen e intentas recordar la palabra en {{español}}; solo entonces volteas la carta («Mostrar respuesta»). Luego dices con honestidad cómo te fue: **Otra vez** (olvidada), **Difícil**, **Bien** o **Fácil**. El planificador **FSRS** (el mismo de Anki) calcula cuándo apenas recordarás la carta y te la muestra justo entonces: al principio tras minutos, después tras días, semanas y meses. Cada botón muestra cuándo vuelve la carta. Las cartas nuevas se aprenden primero en pasos cortos (1 y 10 minutos).

| Zona | Qué encuentras ahí |
| --- | --- |
| Hoy | cuántos repasos y cartas nuevas esperan, «¡Vamos!» |
| Mazos | «Todas las cartas activas» y mazos propios: por idioma, nota, texto de búsqueda, solo nuevas/pendientes/difíciles o marcando cartas; ✎ editar, 🗑 borrar |
| Estadísticas | marcha de gansos (días seguidos), aprendido hoy, pendientes en los próximos 7 días, progreso de las cartas (nueva · aprendiendo · joven · segura), retención |
| Ajustes | cartas nuevas y repasos por día, retención deseada (80–95 %, normal 90 %), dirección (imagen → palabra, palabra → imagen, ambas), idioma de aprendizaje, inicio del día de aprendizaje (normal 4 a. m.) |
| Respaldar progreso | exportar (archivo JSON), importar (en cada carta gana el estado más reciente), reiniciar todo |

**Al aprender:** espacio = mostrar respuesta, teclas **1–4** = calificar, **Ctrl+Z** = deshacer, **Esc** = terminar. En el celular tocas la carta; los botones para calificar quedan abajo, al alcance del pulgar; deslizar a la derecha significa «Bien», a la izquierda «Otra vez» (↶ lo deshace). Puedes parar cuando quieras: cada calificación se guarda al instante, aunque cierres el programa. Si tu sistema tiene una voz para el idioma, 🔊 lee la palabra en voz alta. Después de «Mostrar respuesta» también hay un 🔊 junto al texto en alemán: lee el alemán tal como aparece en la imagen, en ambas direcciones, pero solo después de destapar la carta (si no, revelaría la respuesta). Solo usa una voz de tu sistema que funcione sin internet (primero alemán de Alemania, luego de Austria y después de Suiza); sin ella no aparece el botón. En Windows puedes agregar una voz alemana en Configuración, en «Hora e idioma → Idioma».

**En «Mis cartas»** cada carta muestra su progreso (nueva, aprendiendo, joven, segura; al pasar el mouse: cuántas veces se aprendió y cuándo es el siguiente repaso). Arriba de la lista filtras por pendientes, nuevas, seguras o difíciles. Con **«☑ Seleccionar»** marcas cartas y las aprendes **«ahora»** o las pones en un mazo.

**¿Cambiaste una carta?** Si cambias el texto en alemán, la palabra o la imagen de una carta que ya estás aprendiendo, empieza de nuevo al aprender; el editor te lo dice antes y después aparece un aviso corto. Una nota cambiada conserva el progreso.

**Consejos:** mejor un poco cada día que mucho de vez en cuando. Califica con honestidad: «Otra vez» no es un error, es justo lo que hace listo al planificador. Las cartas que olvidas una y otra vez se vuelven **cartas difíciles**: una imagen más clara o una nota (p. ej. un truco para recordar) suele ayudar más que otro repaso.

## Estudiar en digital

¿Ganas de estudiar en cualquier lugar? Elige **«Tarjetas digitales»** en Generar; el resultado queda en `ausgabe/digital/`:

| Formato | Cómo estudiar con él |
| --- | --- |
| Paquete de Anki (`.apkg`) | ábrelo en Anki en tu computadora (Windows, Mac, Linux), o mándalo al celular por correo, nube o cable e impórtalo en AnkiDroid (Android) o AnkiMobile (iPhone/iPad) |
| Página de estudio (`.html`) | un solo archivo que funciona sin conexión en el navegador de la computadora. Voltear, «¡La sé!» u «Otra vez»; después de voltear, 🔊 lee el texto en alemán (solo con una voz sin conexión de tu sistema; si no, no hay botón); tu progreso se guarda en ese navegador. En el celular funciona solo a medias (en el iPhone casi nunca arranca desde la app Archivos); ahí mejor usa el paquete de Anki o el PDF de pantalla |
| PDF de pantalla | hojéalo en cualquier app de PDF: anverso, reverso, siguiente carta |
| Tablas (CSV) | para Quizlet, Brainscape, Mochi y más; elige «Tablas para otras apps» en los ajustes finos |

En «Revisar e imprimir» obtienes cada archivo con «Descargar», por ejemplo para mandarlo a tu celular. Aún más práctico en el celular: la app (ver «Como app en el celular»), para estudiar tus cartas incluso sin conexión.

## Importar y exportar cartas e ideas

En **Mis cartas → «⇅ Importar / exportar»** (también en Ideas y Herramientas):

- **Exportar:** descarga cartas, ideas o **todo como copia completa** en un ZIP, para respaldar, compartir o mudarte a otra computadora. Con las cartas, todas o solo las que se imprimen.
- **Importar:** elige o arrastra un ZIP así (o un `karten.csv`). Primero ves una **vista previa**: nueva · ya existe, pero distinta · igual · con error. Si algo ya existe, decides en cada fila: **Conservar** (se queda lo tuyo) o **Reemplazar** (gana la importación). No se pierde nada: las imágenes reemplazadas van a `bilder/_entfernt/`. También se reconoce una palabra que ya existe con otro nombre de archivo.
- Imágenes y textos se revisan como en los pasos 1 y 2; fórmulas de Excel, imágenes dañadas o HEIC se quedan fuera.

## Abrir en el celular (wifi)

¿Subir fotos directo desde el celular? En **Herramientas → «Abrir en el celular (wifi)»** activas el acceso desde el celular. Viene apagado y solo funciona en tu propia red wifi:

1. «Activar acceso desde el celular»: aparecen un código QR, la dirección y un PIN de 6 dígitos.
2. Escanea el código QR con la cámara del celular (o escribe la dirección en su navegador) e ingresa el PIN.
3. ¡Listo! Ahora puedes agregar imágenes, crear gansos con IA, rotular cartas y juntar ideas desde el celular.

La dirección sigue igual la próxima vez que lo actives, así que un marcador en el celular sigue sirviendo. La primerísima vez, Windows o macOS pregunta si Python puede aceptar conexiones: permítelo (red privada).

Por tu seguridad: dentro de tu red de casa la conexión no está cifrada, así que úsalo solo en casa. Se apaga solo después de 2 horas, tras 5 PIN incorrectos y al cerrar el programa. Cerrar, desinstalar y abrir carpetas solo se puede directamente en la computadora.

## Como app en el celular

Me Goos-ta Deutsch también existe como **app para el celular** (app web) para Android, Google Pixel y iPhone/iPad: la misma interfaz y el mismo programa, solo que sin computadora: Python funciona directamente en el navegador del celular. Después de la primera carga (poco más de 20 MB), la app también se abre sin internet.

- **Dirección y guías:** en la computadora, **Herramientas → «Abrir en el celular (wifi)»** muestra abajo el código QR de la app (para eso no hace falta el acceso por wifi), igual que «📲 Como app en el celular» en **Revisar e imprimir → Aprender en digital**. Junto a los archivos de inicio hay tres guías con dibujos: `Me Goos-ta Deutsch - Android.html`, `… - iPhone.html` y `… - Google Pixel.html`: abre una en la computadora y escanea el código QR, o envía el archivo al celular por correo o la nube. No necesitan JavaScript, así que también abren en apps de archivos.
- **Instalar:** abre la dirección de la app en el navegador y toca «📲 Instalar app»; con Chrome (Android, Google Pixel) se vuelve una app de verdad en tu menú de apps. En iPhone/iPad (desde iOS 16.4): Safari → Compartir → «Agregar a pantalla de inicio» → «Agregar». Los pasos con dibujos están en la app en **Más → Instalar app**.
- **Abajo**, la barra de la app te lleva a todo: **Cartas · Nueva · Aprender · Imprimir · Más**. «Más» abre la tabla, la mejora de imagen, las ideas, las herramientas, la ayuda y lo de la app. El gesto de atrás primero cierra una ventana abierta y luego regresa una sección. La misma barra aparece también con el acceso desde el celular en pantallas táctiles de hasta 860 px de ancho.
- **Tus datos se quedan en el dispositivo** (en el almacenamiento del navegador: sin cuenta, sin subir nada). En **Más → Copia y almacenamiento**, «Respaldar todo» guarda cartas, imágenes, ideas, avance de aprendizaje y ajustes en un archivo; «Restaurar copia» los recupera y reemplaza todo en este dispositivo. En iPhone los datos solo se quedan para siempre en la app instalada; si no, Safari borra los datos del sitio tras 7 días sin visitarlo.
- **Traer cartas de la computadora:** en la computadora, en Mis cartas → ⇅ Importar / exportar, exporta «Todo: copia de seguridad completa», envía el archivo al celular (correo, nube, cable) e impórtalo en la app, con tu avance de aprendizaje.
- **Los resultados** (PDF de impresión, paquete de Anki, copia) se abren para **compartir** (imprimir, correo, «Archivos») o **guardar**. Las tareas largas muestran su avance y «Cancelar» las detiene; todo va en orden por la cola.
- **Qué cambia en el celular:** las imágenes IA solo están en la computadora (modelo de 3,5 GB); el botón se queda y te avisa. Real-ESRGAN es bastante más lento en el celular; el FSRCNN integrado basta para imprimir. La traducción automática usa Wiktionary y MyMemory (DeepL solo en la computadora). Hindi y árabe se imprimen sin formas de sílabas (eso necesita uharfbuzz en la computadora). El programa de inicio, las carpetas, el acceso desde el celular y la desinstalación no existen en la app.
- **Nueva versión:** la app descarga las actualizaciones sola en segundo plano y avisa «Hay una nueva versión del ganso: ¿recargar?» (también en Más).

## Inicio del programa: navegador o ventana propia

Si Me Goos-ta Deutsch se abre **en el navegador predeterminado**, **en un navegador concreto** o **en su propia ventana** sin barra de direcciones (para eso hace falta Edge, Chrome, Brave o Chromium) lo decides en el asistente de bienvenida, y lo cambias cuando quieras en **Herramientas → Inicio del programa**. Se aplica desde el próximo inicio.

## Desinstalar

La última pestaña **«Desinstalar»** te guía en dos pasos:

1. **Respaldar cartas e ideas:** «Descargar copia completa» guarda todo en un ZIP. Después de una instalación nueva, incluso en otro dispositivo, «Importar / exportar → Importar» lo vuelve a cargar todo.
2. **Desinstalar el programa:** tras una pregunta («¿Seguro?») y una casilla, el programa quita el icono, la app o la entrada del menú, su propio Python con ajustes y traducciones guardadas **y la carpeta del programa con todas las cartas, imágenes e ideas**. No se puede deshacer; por eso existe el paso 1. Tu copia de respaldo, los archivos fuera de la carpeta del programa y otros programas no se tocan.

Volver a instalar se puede cuando quieras: descomprime la descarga, haz doble clic en el archivo de inicio, importa tu copia y listo.

## Mejora de imagen: ¿qué modelo de IA?

Se probaron cinco modelos libres contra el más sencillo FSRCNN con fotos pequeñas y muy comprimidas con texto: Real-ESRGAN x4plus, Real-ESRGAN x2plus, Real-ESRGAN anime 6B, Real-ESRGAN general v3 y SwinIR-L. **Real-ESRGAN x4plus** da el mejor resultado: quita los bloques JPEG, deja plumas y ojos convincentemente nítidos y mantiene limpias las letras. Los modelos de difusión quedan fuera: inventan detalles, también letras. Real-ESRGAN tiene licencia BSD-3 y el programa lo calcula sin software adicional, en NumPy puro.

## Seguridad

- La interfaz solo es accesible desde tu computadora y solo se abre con el programa de inicio (clave de inicio secreta), salvo que actives a propósito el acceso desde el celular: entonces, además, con PIN y en tu propia wifi.
- Otras páginas web no pueden controlarla; los archivos solo se leen y escriben en las carpetas del proyecto, y «Abrir» nunca ejecuta programas ni scripts.
- La traducción automática solo envía datos con tu permiso y solo la palabra a traducir (en la imagen IA, al hacer clic, la descripción corta), cifrada, a tres servicios fijos.
- «Buscar una versión nueva» solo pregunta cuando haces clic en el botón: una consulta a api.github.com, sin datos sobre ti ni tus cartas. El programa nunca busca actualizaciones por sí solo.
- Leer en voz alta (🔊) solo usa voces de tu sistema que funcionan sin conexión; ningún texto va a internet para eso.
- El modelo de imágenes IA trabaja por completo en tu computadora; las descripciones y las imágenes no salen de ella.
- Los textos que Excel tomaría como fórmula (que empiezan con = + - @) se rechazan, también al importar. Las imágenes se revisan y se guardan sin metadatos.
- Los modelos de IA y Python solo se descargan de fuentes oficiales y se verifican con suma de comprobación; los archivos de modelo no pueden ejecutar código.
- Nada de esto necesita permisos de administrador, y el Control inteligente de aplicaciones de Windows sigue activado.

## Solución de problemas

No te preocupes: casi todo tiene una solución rápida.

| Problema | Solución |
| --- | --- |
| «Python was not found …» o Windows pide un programa para archivos `.py` | No hace falta Python: el archivo de inicio trae el suyo; solo haz doble clic en él |
| «El Control inteligente de aplicaciones bloqueó …» | Desbloquea el ZIP o el archivo de inicio: Propiedades → «Desbloquear» → Aceptar |
| «Windows protegió su PC» | «Más información» → «Ejecutar de todas formas» |
| La ventana de inicio dice «No hay conexión a internet» | Solo el primer inicio necesita internet: revisa la conexión e inicia de nuevo. Lo ya descargado se reutiliza |
| No se abre el navegador | Copia la dirección de la ventana de inicio (http://127.0.0.1:…) en el navegador |
| La página dice «Ábrelo con el icono …» | Inicia con el icono: un marcador no funciona después de reiniciar, la clave de inicio cambia cada vez |
| «La conexión se tomó un respiro» | La interfaz se cerró: iníciala otra vez con el icono |
| El icono no hace nada o dice «carpeta del programa movida» | Haz doble clic una vez en el archivo de inicio de la carpeta (nueva): revisa y repara todo |
| Después de actualizar faltan mis cartas | Importa tu copia, o copia `karten.csv` y la carpeta `bilder` de la carpeta anterior a la nueva carpeta `Programm` |
| 🌐 dice «… aún no está activada» | Elige «Activar y traducir» en la ventana o permítela en Herramientas |
| «Uy, el ganso se enredó un momento (…)» | un error inesperado: inténtalo otra vez; si vuelve a pasar, reinicia el programa desde su icono (entre paréntesis está el motivo técnico, útil si pides ayuda) |
| El servicio de traducción no responde / se agotó la cuota del día | Prueba más tarde, guarda tu propia clave de DeepL, o escribe la palabra tú mismo |
| El celular no encuentra la dirección | La computadora y el celular deben estar en la misma wifi; las redes de invitados suelen separar los dispositivos. ¿El firewall de Windows o macOS preguntó si Python puede aceptar conexiones? Permítelo para redes privadas |
| «🪄 Crear ganso con IA» dice que falta el modelo | Herramientas → Herramientas opcionales → Imágenes IA «Instalar» (unos 3,5 GB, una vez); una descarga interrumpida continúa la próxima vez |
| El ganso IA parece más bien un pato, tiene una pata de más o sí aparecen personas | 🎲 otra variante; describe con más detalle; deja «Sin personas» activado y describe una escena tranquila («early morning», «empty») en vez de una multitud |
| La imagen IA tarda mucho | 1–2 minutos es normal, computadoras viejas tardan 3–5; cierra otros programas grandes. Apagar «Sin personas» ahorra unos 20 segundos |
| Se rechaza la imagen de ganso | Usa JPG, PNG o WEBP (no HEIC), mínimo 300 píxeles, máximo 40 MB |
| Generar tarda mucho | Real-ESRGAN necesita de 1 a 4 minutos por imagen la primera vez; después va rápido. Mejora las imágenes antes en «Mejora de imagen» o elige «FSRCNN (rápido)» para probar |
| La vista previa del reverso solo muestra la palabra | Haz doble clic una vez en el archivo de inicio (lo repara); los PDF salen bien de todos modos |
| Lista de palabras: «parece un archivo de Excel» | en Excel «Guardar como» → «CSV UTF-8 (delimitado por comas)», o copia las celdas y pégalas en el campo de la lista |
| La lista muestra caracteres raros (Ã¤ en vez de ä) | guárdala como «CSV UTF-8» o texto UTF-8; la vista previa muestra arriba la codificación detectada |
| Lista de palabras: «lista demasiado larga, divídela» | como máximo 500 palabras y 1 MB por lista: divídela en varios archivos y créalos uno tras otro |
| ñ, á o ü salen como caracteres raros | Guarda `karten.csv` como «CSV UTF-8» |
| Reverso al revés / impresión desplazada | «Girar el reverso 180°» / «desplazamiento» en Generar |
| Imagen mal recortada | Cambia el recorte en el paso 1 |

En caso de duda: **Herramientas → Autoprueba**. Revisa todo en una copia con las cartas de ejemplo y no toca tus archivos.

## Acordeón

```
 Inicio         icono «Me Goos-ta Deutsch»
   │            (la primera vez: archivo de inicio de la carpeta)
   │
 1 Imágenes     arrastrar imágenes (muchas está bien) · <───┐
   │            o deja que la IA pinte (1–2 min) ·          │
   │            texto de la imagen · palabra · agregar      │
   │                                                        │
 2 Rotular      palabras que faltan («Traducir todas») ·    │ no:
   │            ver el reverso · «Guardar todas»            │ corregir en
   │                                                        │ el paso 1,
   Tabla        alemán ↔ español · «revisada»     │ el paso 2 o
   │                                                        │ la tabla
 3 Generar      elegir objetivo · ajustar · ¡vamos!         │
   │            (imágenes nuevas: 1–4 min, antes en         │
   │            «Mejora de imagen»)                         │
   │                                                        │
 4 Revisar      hoja de control + lista ── ¿todo bien? ─────┘
   │ sí
   Imprimir     en casa (100 %, borde largo), imprenta, o estudiar en digital
```

¡Que te diviertas aprendiendo! Vas de maravilla, y eso es Gans cierto.
