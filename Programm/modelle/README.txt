KI-MODELLE FÜR DIE BILDVERBESSERUNG – Me Goos-ta Deutsch 2.1
=============================================================

realesrgan-x4plus.npz   (Standard, beste Qualität – 30 MB; gehört zum Tool „Bildverbesserung“ und ist nicht
                         vorinstalliert: Werkzeuge → Tools → Bildverbesserung „Installieren“, beim ersten
                         Gebrauch auf Nachfrage oder python3 ki_modelle.py --laden realesrgan-x4plus)
  Real-ESRGAN x4plus – Wang, Xie, Dong, Shan: „Real-ESRGAN: Training Real-World Blind Super-Resolution with
  Pure Synthetic Data“ (ICCVW 2021). Lizenz: BSD-3-Clause (siehe LICENSE-RealESRGAN.txt).
  Quelle: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
  SHA-256 der Originaldatei: 4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1
  Umgewandelt in eine pickle-freie NumPy-Datei (float16) mit ki_modelle.py – gerechnet wird in reinem NumPy,
  ohne PyTorch und ohne Grafikkarte. Entfernt JPEG-Blöcke und Rauschen und vergrößert ×4.

realesrgan-x2plus.npz   (optional, etwa 4× schneller, fast gleiche Qualität)
  Nicht im Download enthalten. Laden: Werkzeuge → Tools → Bildverbesserung „+ Schneller ×2“
  oder: python3 ki_modelle.py --laden realesrgan-x2plus   (Prüfsumme wird kontrolliert)

fsrcnn_x2.npz, fsrcnn_x3.npz, fsrcnn_x4.npz   (Rückfall, sehr schnell)
  FSRCNN (Dong, Loy, Tang, ECCV 2016), Gewichte aus https://github.com/Saafke/FSRCNN_Tensorflow
  (Apache-2.0, siehe LICENSE-FSRCNN.txt). Wird genutzt, wenn Real-ESRGAN fehlt oder „FSRCNN (schnell)“
  gewählt ist.

Fehlt ein Modell, wählt „Auto“ das beste vorhandene; ohne jedes Modell wird mit Lanczos vergrößert.
Modelle neu laden oder prüfen:  python3 ki_modelle.py --liste
