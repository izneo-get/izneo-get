# izneo-get
Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Izneo. 
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.


# Utilisation
python izneo_get.py [-h] 
                [--cfduid CFDUID]
                [--session-id SESSION_ID] 
                [--output-folder OUTPUT_FOLDER]
                [--output-format {cbz,both,jpg}] [--config CONFIG]
                url

Exemple : 
Pour récupérer la BD dans un répertoire d'images (fichier de config présent) : 
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197

Pour récupérer la BD dans une archive CBZ (fichier de config présent) :
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 -f cbz

Pour récupérer la BD dans un répertoire d'images, sans fichier de config présent : 
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 -c abcdef12345678901234567890123456789012345678 -s abcdefghijkl123456789012345 -o /tmp/DOWNLOADS

CFDUID est la valeur de "cfduid" dans le cookie.
SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans le cookie.

Pour les obtenir, identifiez vous sur https://www.izneo.com/fr/ et recherchez votre cookie avec votre navigateur web.

Chrome : 
Menu --> Plus d'outils --> Outils de développements
Application / Storage / Cookies
et recherchez le cookie "https://www.izneo.com".

Firefox : 
Menu --> Developpement web --> Inspecteur de stockage --> Cookies
et recherchez le cookie "https://www.izneo.com".

Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get.cfg".


# Prérequis
L'ordinateur doit posséder les librairies OpenSSL. 

pip install -r requirements.txt
