# Erzeugen von synthetischen Trainingsdaten für maschinelle Lernverfahren in Anwendung in der Landwirtschaft


- AirSim (Speicherort: ...\documents):
    - settings.json: Von AirSim bereitgestellte Datei, die stark bearbeitet wurde. Sie legt Fahrzeug, Bildgröße, Bildtyp und Belichtung fest


- script (Speicherort: ...\Microsoft Visual Studio\2019\Community\AirSim\PythonClient): <br> Neuester Stand der Dateien. Kann sowohl Einzelpflanzen als auch eine Menge verarbeiten.
    - placement.py: Setzt die Pflanzen an gegebene Positionen, ermöglicht das Löschen der Pflanzen <br> Die Funktionen werden einzeln im Unreal Editor aufgerufen
    - pictures.py: Positioniert die Kamera und speichert Bilder <br> Ausführung wird in der Datei gezeigt
    - cococrowd.py: speichert Informationen im Cocoformat, geeignet für eine Pflanzenmenge
    - cocosingle.py: speichert Informationen im Cocoformat, geeignet für Einzelpflanzen
    - setup_path.py: gegebene Datei von AirSim

- training
    - inference_graph: enthält einen der verwendeten inference Graphen
    - tfrecords: enthält die verwendeten tfrecords
    - labelmap.pbtxt: ordnet den Klassen eine ID zu
    - ssd_mobilenet_v2_coco.config: verwendete Konfigurationsdatei für Trainingsmodell ssd_mobilenet_v2_coco
