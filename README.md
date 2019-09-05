# izneo-get
Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.


# Utilisation
python izneo_get.py [-h] 
                [--cfduid CFDUID]
                [--session-id SESSION_ID] 
                [--output-folder OUTPUT_FOLDER]
                [--output-format {cbz,both,jpg}] [--config CONFIG]
                url

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
