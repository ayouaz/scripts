# Exécution du script Python `filter_voie_ec_dv.py`

## Prérequis
- Python 3.8 ou supérieur
- Aucun paquet externe requis (utilise `os`, `re`, `argparse`)

## Fichier d’entrée
- `levéRaildemo.txt` par défaut
- Format attendu : lignes avec identifiant de point (`VO01_*` ou `VO02_*`), coordonnées, et code `EC` ou `DV`

## Commande rapide
- Depuis le dossier `c:\Projets\TramawayOran\levé\scripts\script_railway`:
  - Windows PowerShell: `python .\filter_voie_ec_dv.py`
  - Linux/macOS: `python3 filter_voie_ec_dv.py`

## Options
- `--input` : chemin du fichier source (défaut `levéRaildemo.txt`)
- `--output` : dossier de sortie (défaut `.`)
- `--threshold-mm` : seuil d’alerte en millimètres (défaut `5`)
- `--excel-file` : nom du fichier Excel XML généré (défaut `ec_alerts.xml`)

Exemple Windows :
- `python .\filter_voie_ec_dv.py --input .\levéRaildemo.txt --output .\out --threshold-mm 5 --excel-file ec_alerts.xml`

Exemple Linux/macOS :
- `python3 filter_voie_ec_dv.py --input levéRaildemo.txt --output out --threshold-mm 5 --excel-file ec_alerts.xml`

Changer le seuil d’alerte :
- `--threshold-mm 8`

## Fichiers générés
- `voie01.txt`, `voie02.txt` : toutes les mesures par voie
- `voie01_ec.txt`, `voie01_dv.txt`, `voie02_ec.txt`, `voie02_dv.txt` : filtrage par code
- `voie01_ec_analysis.txt`, `voie02_ec_analysis.txt` : distances et écart en mm format texte
- `voie01_ec_analysis.csv`, `voie02_ec_analysis.csv` : distances, écart (`diff_mm`) et drapeau `OK/ALERT`
- `ec_alerts.xml` : Excel XML avec deux feuilles `VOIE01_ALERTS` et `VOIE02_ALERTS` listant les paires avec `|diff_mm| > threshold`

## Notes
- Encodage UTF‑8 géré à la lecture (`errors="ignore"`). Si votre chemin contient des caractères spéciaux, entourez‑le de guillemets.
- Exécutez la commande depuis le répertoire du script, ou passez des chemins complets pour `--input` et `--output`.
- Un script PowerShell minimal `filter_voie_ec_dv.ps1` est disponible pour un découpage rapide (`voie01/02`, `EC/DV`) sous Windows.
