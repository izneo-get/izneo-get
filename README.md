# izneo-get

Ce script permet de récupérer une BD présente sur `https://www.izneo.com/fr/` dans la limite des capacités de notre compte existant.  
Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Izneo.  
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.  

## Utilisation en mode interactif

Il est possible de lancer le programme sans aucun argument.  
Le programme demandera alors les paramètres interactivement.  

TODO: remplir

## Utilisation en ligne de commande

### Utilisation

```cmd
usage: izneo_get.py [-h] 
                    [--config CONFIG] 
                    [--output-folder OUTPUT_FOLDER] 
                    [--output-filename OUTPUT_FILENAME]
                    [--image-format {webp,jpeg,origin}] [--image-quality IMAGE_QUALITY] [--output-format {cbz,images,both}] [--pause PAUSE]   
                    [--user-agent USER_AGENT] 
                    [--continue] 
                    [--ignore-cache]
                    [url]

Script pour sauvegarder une BD Izneo.

positional arguments:
  url                   L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs

options:
  -h, --help            show this help message and exit
  --config CONFIG       Fichier de configuration
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-filename OUTPUT_FILENAME
                        Nom du fichier ou répertoire de sortie
  --image-format {webp,jpeg,origin}
                        Conversion des images au format JPEG ou WEBP
  --image-quality IMAGE_QUALITY
                        Qualité de conversion des images (100 = maximum)
  --output-format {cbz,images,both}, -f {cbz,images,both}
                        Format de sortie
  --pause PAUSE         Pause (en secondes) à respecter après chaque téléchargement d'image
  --user-agent USER_AGENT
                        User agent à utiliser
  --continue            Pour éviter de télécharger un fichier déjà existant
  --ignore-cache        Pour ne pas utiliser le cache de session
```

Exemple :  

* Pour récupérer la BD dans un répertoire d'images (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

* Pour récupérer la BD dans une archive CBZ en forçant le titre (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 -f cbz --force-title "[Yusei Matsui] Assassination Classroom - Tome 1"
```

* Pour récupérer la BD dans une archive CBZ avec des images converties en WEBP (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 -f cbz --webp 70
```

* Pour récupérer une liste de BDs, dans un répertoire d'images correspondant à l'arborescence du serveur, sans fichier de config présent :  

```cmd
python izneo_get.py /tmp/input.txt -s abcdefghijkl123456789012345 -o /tmp/DOWNLOADS --tree
```

* Récupérer tous les tomes d'une série :  

```cmd
python izneo_list.py --full-only URL > input.txt
python izneo_get.py --continue --output-format cbz --webp 70 --full-only input.txt
```

SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans les cookies.  

Pour les obtenir, identifiez vous sur `https://www.izneo.com/fr/` et recherchez votre cookie avec votre navigateur web.

#### Chrome

Menu --> Plus d'outils --> Outils de développements  
Application / Storage / Cookies  
et recherchez le cookie `https://www.izneo.com`.  

#### Firefox

Menu --> Developpement web --> Inspecteur de stockage --> Cookies  
et recherchez le cookie `https://www.izneo.com`.  

Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get_selenium.cfg".  

### izneo_list

#### Utilisation

```cmd
python izneo_list.py [-h] [--session-id SESSION_ID] [--config CONFIG] [--pause PAUSE] [--full-only] [--force-title] search

Script pour obtenir une liste de BDs Izneo.

positional arguments:
  search                La page de série qui contient une liste de BDs

options:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --config CONFIG       Fichier de configuration
  --pause PAUSE         Pause (en secondes) à respecter après chaque appel de page
  --full-only           Ne prend que les liens de BD disponible dans l'abonnement
  --force-title         Ajoute l'élément "--force-tilte" dans la sortie
```

Exemple :  

* Pour récupérer la liste des liens d'une série (fichier de config présent) :  

```cmd
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567
```

* Pour récupérer la liste des liens d'une série, dans la limite des albums complets inclus dans l'abonnement en ajoutant le tag "--force-title" (fichier de config présent) :  

```cmd
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567 --full-only --force-title
```

* Pour récupérer la liste des liens de séries qui correspondent à la rechercher "largo" (fichier de config présent) :  

```cmd
python izneo_list.py "largo"
```

### izneo_infos

#### Utilisation

```cmd
python izneo_infos.py [-h] [--output OUTPUT_FILE] URL

Script pour obtenir les infos sur une BD Izneo.

positional arguments:
  URL                   L'URL d'une BD.

options:
  -h, --help            show this help message and exit
  --output OUTPUT_FILE, -o OUTPUT_FILE
                        Enregistrer le résultat dans un fichier (JSON ou XML).
```

Exemple :  

* Pour afficher les informations d'une BD :  

```cmd
python izneo_infos.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

Le résultat sera :

```cmd
Genres               : Shonen | Action / Aventure
Auteur               : Yusei Matsui
Editeur              : Kana
Numéro               : 1/21
Paru le              : 22/11/2013
Public               : 12 ans et +
Modes de Lecture     : HD
title                : Assassination classroom
subtitle             : Assassination classroom T1
serie_name           : Assassination classroom
volume               : 1
shelf_name           : Manga
gender_name          : Shonen
readDirection        : rtl
synopsis             : Une salle de cours, un professeur, des élèves... et des coups de feu !
Les élèves de la classe 3-E du collège de Kunugigaoka sont des assassins en herbe, et leur professeur est leur cible à abattre !
Découvrez le quotidien insolite d'un drôle de professeur et de ses élèves !!
```

* Pour enregistrer les informations d'une BD dans un fichier :  

```cmd
python izneo_infos.py --output assassination-classroom-t1.json https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

ou

```cmd
python izneo_infos.py --output assassination-classroom-t1.xml https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

## Installation

### Prérequis

* Python 3.10+ (non testé avec les versions précédentes)
* pip (désormais inclus avec Python)
* Librairies SSL

#### Sous Windows

##### Python

Allez sur ce site :  
<https://www.python.org/downloads/windows/>  
et suivez les instructions d'installation de Python 3.

##### Librairies SSL

* Vous pouvez essayer de les installer avec la commande :  

```cmd
pip install pyopenssl
```

* Vous pouvez télécharger [OpenSSL pour Windows](http://gnuwin32.sourceforge.net/packages/openssl.htm).  

#### Sous Linux

Si vous êtes sous Linux, vous n'avez pas besoin de moi pour installer Python, Pip ou SSL...  

### Installation

* En ligne de commande, clonez le repo :  

```cmd
git clone https://github.com/izneo-get/izneo-get.git
cd izneo-get
```

* (optionnel) Créez un environnement virtuel Python dédié :  

```cmd
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
```

* Installez les dépendances :  

```cmd
python -m pip install -r requirements.txt
```

En cas de problème, on peut installer les dépendances à la main :  

```cmd
cd izneo-get
python -m venv env
env\Scripts\activate
python.exe -m pip install --upgrade pip
python.exe -m pip install pycryptodome
python.exe -m pip install requests
python.exe -m pip install beautifulsoup4
python.exe -m pip install Pillow
```
  
ou  
  
* Vous pouvez télécharger uniquement le [binaire Windows](https://github.com/izneo-get/izneo-get/releases/latest) (expérimental).  
