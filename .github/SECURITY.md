# Security policy 🪿

Thank you for helping to keep Me Goos-ta Deutsch and its learners safe – every careful report makes the flock stronger.

## Supported versions

Only the **latest release** gets security fixes:
https://github.com/LukasDieGans/me-goos-ta-deutsch/releases/latest

The phone app (https://lukasdiegans.github.io/me-goos-ta-deutsch/) always serves the latest version.
Older releases are not patched – please update first (Tools → “Keep the program up to date”, or the download page:
https://lukasdiegans.github.io/me-goos-ta-deutsch/download/).

## Verifying a release

From version 2.5 on, `SHA256SUMS.txt` of every release is signed with the project’s key (minisign format, Ed25519;
file `SHA256SUMS.txt.minisig`, trusted comment `me-goos-ta-deutsch v<version>`). “Update now” in the program installs
a new version only if this signature is valid – a stolen GitHub account or token alone cannot push an update. To check
a download yourself with the free tool minisign:

```
minisign -Vm SHA256SUMS.txt -P RWTgF/PLaqyFaOLbzuVu1f/n4Ym5ajtcWCm1zsQdvXugs6WwITJQaRz7
```

Key ID `6885AC6ACBF317E0`; then compare the SHA-256 of the ZIP with the line in `SHA256SUMS.txt`. A reserve key
(ID `01C92660376DB3D4`) is kept offline. If both keys were ever lost, the next version would have to be installed by
hand once (download page) – the program never trusts an unsigned update.

## How to report a vulnerability

Please **do not** open a public issue for security problems.

1. Open https://github.com/LukasDieGans/me-goos-ta-deutsch/security/advisories/new
   (tab “Security” → “Report a vulnerability”).
2. Describe what you found, how to reproduce it, which version and system you used, and what an attacker could do.
3. Screenshots, logs or a small proof of concept help – please leave out personal data and your own flash cards.

The report is private: only you and the maintainer can see it.

## What to expect

- First answer within **7 days** (this is a one-person hobby project – thanks for your patience).
- An assessment within **14 days**: confirmed, needs more information, or not a vulnerability (with reasons).
- Confirmed problems are fixed in a new release as soon as possible. With your permission you are credited in the
  advisory and the release notes.
- Please give us a reasonable time to fix the problem before you publish details (coordinated disclosure, usually
  up to 90 days).

## Scope

In scope – everything that ships in this repository:

- **Update in the program** (“Update now”: download, signature, checksum, unpacking, restart)
- **Start files** (`Me Goos-ta Deutsch - Windows.cmd`, `- Mac.command`, `- Linux.sh`) and the first setup
  (Python and package downloads, checksums)
- **Local server** of the interface (`127.0.0.1` only: token, cookie, host/origin checks, content security policy,
  file and ZIP handling)
- **Phone access** in the home network (optional, off by default, PIN protected)
- **Web app** on GitHub Pages (service worker, offline storage, backup import)
- Tools you install yourself (model and font downloads with checksums), translation suggestions
- The GitHub Actions workflows in `.github/`

Out of scope: problems that need full control of your computer or account already, social engineering, denial of
service through huge files you load yourself, and reports produced only by automated scanners without a concrete
impact.

---

**Deutsch (kurz):** Sicherheitslücken bitte nie als öffentliches Issue melden, sondern privat über
https://github.com/LukasDieGans/me-goos-ta-deutsch/security/advisories/new („Report a vulnerability“). Unterstützt
wird nur das neueste Release. Antwort innerhalb von 7 Tagen, Einschätzung innerhalb von 14 Tagen. Dazu gehören Update
im Programm, Startdateien, lokaler Server, Handy-Zugang, Web-App und die Workflows. Ab 2.5 ist `SHA256SUMS.txt`
signiert (minisign, Schlüssel-ID `6885AC6ACBF317E0`) – das Programm übernimmt nur Updates mit gültiger Signatur.

**Español (breve):** Por favor, no reportes vulnerabilidades en un issue público; usa el reporte privado en
https://github.com/LukasDieGans/me-goos-ta-deutsch/security/advisories/new (“Report a vulnerability”). Solo la versión
más reciente recibe correcciones. Respuesta en 7 días, evaluación en 14 días. Incluye la actualización dentro del
programa, los archivos de inicio, el servidor local, el acceso desde el celular, la app web y los workflows. Desde la
2.5, `SHA256SUMS.txt` está firmado (minisign, ID de clave `6885AC6ACBF317E0`): el programa solo instala actualizaciones
con una firma válida.
