# izneo-get
Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Izneo. 
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.


## Utilisation
### izneo_get
usage: 
```
python izneo_get.py [-h] [--session-id SESSION_ID] [--cfduid CFDUID]
                    [--output-folder OUTPUT_FOLDER]
                    [--output-format {both,jpg,cbz}] [--config CONFIG]
                    [--from-page FROM_PAGE] [--limit LIMIT] [--pause PAUSE]
                    [--full-only] [--continue] [--user-agent USER_AGENT]
                    url

Script pour sauvegarder une BD Izneo.

positional arguments:
  url                   L'URL de la BD à récupérer ou le chemin vers un
                        fichier local contenant une liste d'URLs

optional arguments:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --cfduid CFDUID, -c CFDUID
                        L'identifiant cfduid
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-format {both,jpg,cbz}, -f {both,jpg,cbz}
                        Répertoire racine de téléchargement
  --config CONFIG       Fichier de configuration
  --from-page FROM_PAGE
                        Première page à récupérer (défaut : 0)
  --limit LIMIT         Nombre de pages à récupérer au maximum (défaut : 1000)
  --pause PAUSE         Pause (en secondes) à respecter après chaque
                        téléchargement d'image
  --full-only           Ne prend que les liens de BD disponible dans
                        l'abonnement
  --continue            Pour reprendre là où on en était
  --user-agent USER_AGENT
                        User agent à utiliser
```

Exemple :  
Pour récupérer la BD dans un répertoire d'images (fichier de config présent) :  
```
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```


Pour récupérer la BD dans une archive CBZ (fichier de config présent) :  
```
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 -f cbz
```


Pour récupérer une liste de BDs, dans un répertoire d'images, sans fichier de config présent :  
```
python izneo_get.py /tmp/input.txt -c abcdef12345678901234567890123456789012345678 -s abcdefghijkl123456789012345 -o /tmp/DOWNLOADS
```


CFDUID est la valeur de "cfduid" dans le cookie.  
SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans le cookie.  

Pour les obtenir, identifiez vous sur https://www.izneo.com/fr/ et recherchez votre cookie avec votre navigateur web.

#### Chrome  
Menu --> Plus d'outils --> Outils de développements  
Application / Storage / Cookies  
et recherchez le cookie "https://www.izneo.com".  


#### Firefox  
Menu --> Developpement web --> Inspecteur de stockage --> Cookies  
et recherchez le cookie "https://www.izneo.com".  


Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get.cfg".  


### izneo_get
```
usage: izneo_list.py [-h] [--session-id SESSION_ID] [--cfduid CFDUID]
                     [--config CONFIG] [--pause PAUSE] [--full-only]
                     search

Script pour obtenir une liste de BDs Izneo.

positional arguments:
  search                La page de série qui contient une liste de BDs

optional arguments:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --cfduid CFDUID, -c CFDUID
                        L'identifiant cfduid
  --config CONFIG       Fichier de configuration
  --pause PAUSE         Pause (en secondes) à respecter après chaque appel de
                        page
  --full-only           Ne prend que les liens de BD disponible dans
                        l'abonnement
```

Exemple :  
Pour récupérer la liste des liens d'une série (fichier de config présent) :  
```
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567
```

Pour récupérer la liste des liens d'une série, dans la limite des albums complets inclus dans l'abonnement (fichier de config présent) :  
```
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567 --full-only
```



## Prérequis
Python 3
pip install -r requirements.txt
L'ordinateur doit posséder les librairies OpenSSL. 
