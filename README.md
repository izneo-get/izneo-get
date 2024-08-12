# izneo-get

Ce script permet de récupérer une BD présente sur `https://www.izneo.com/fr/` dans la limite des capacités de notre compte existant.  
Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Izneo.  
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.  

Sites compatibles :

- <https://archive.org/>
- <https://www.izneo.com/fr/>

## Utilisation en mode interactif

Il est possible de lancer le programme sans aucun argument.  
Le programme demandera alors les paramètres interactivement.  

```cmd
[?] What parameter do you want to update: 
   Output folder: DOWNLOADS/{serie}
   Filename pattern: {title} - {volume}. {subtitle}
   Image format: JPEG
   Image quality: 100
   Output format: IMAGES
   Pause (sec): 0
   User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
   Continue from existing: False
   Authentication from cache: True
   Save this config as default
   >> DONE <<
```

Ce menu se navigue avec les flèches du clavier et la touche `Entrée` pour valider. Vous pouvez changer toutes les valeurs.  
Pour en faire les valeurs par défaut, on peut les enregistrer dans le fichier de config avec l'option `Save this config as default`.  
Une fois les paramètres définis, terminer avec `>> DONE <<`.  

- `Output folder` : Le répertoire dans lequel sera enregistré les fichiers.
- `Filename pattern` : Le modèle utilisé pour le nom de fichier. Les mots clés entre `{}` seront remplacés par la valeur correspondante dans les informations du livre.
- `Image format` : Le format des images.
- `Image quality` : La qualité des images (uniquement si `Image format` est différent de `ORIGIN`).
- `Output format` : Permet de dire si on souhaite avoir en sortie un répertoire avec des images (`IMAGES`), un fichier CBZ (`CBZ`) ou les deux (`BOTH`).
- `Pause (sec)` : Le temps d'attente en secondes entre 2 téléchargements d'image. Si `0`, les images seront téléchargées en parallèle.
- `User agent` : La signature de navigateur à utiliser.
- `Continue from existing` : Permet de reprendre un téléchargement interrompu (`True`) ou télécharger à nouveau même si les fichiers existent déjà (`False`).
- `Authentication from cache` : Permet d'utiliser le fichier de cache pour s'authentifier (`True`). Si `False`, les informations de connexion seront demandées.
- `Save this config as default` : Enregistrer cette configuration pour qu'elle soit utilisée par défaut.
- `>> DONE <<` : Passer à l'étape suivante.
  
Le programme demande l'action à effectuer :  

```cmd
[?] What do you want to do?: 
   Download + Convert + Pack
   Get book infos only
   Download book only
   Convert book only
   Pack book only
   EXIT
```

- `Download + Convert + Pack` : Télécharger le livre dans `Output folder` avec un nom basé sur `Filename pattern`, convertir les images au format attendu (`Image format`, `Image quality`) et créer l'archive au format attendu (`Output format`).
- `Get book infos only` : Récupérer et afficher les informations du livre uniquement.
- `Download book only` : Télécharger le livre uniquement, sans modifier les images.
- `Convert book only` : Convertir les images d'un répertoire au format attendu uniquement.
- `Pack book only` : Créer l'archive au format attendu uniquement.
- `EXIT` : Sortir du programme sans rien faire.

## Utilisation en ligne de commande

### Utilisation

```cmd
usage: izneo_get.py [-h] [--config CONFIG] [--output-folder OUTPUT_FOLDER] [--output-filename OUTPUT_FILENAME] [--image-format {webp,jpeg,origin}] [--image-quality IMAGE_QUALITY]
                    [--output-format {cbz,images,both}] [--pause PAUSE] [--user-agent USER_AGENT] [--continue] [--ignore-cache]
                    [action] [url]
Script pour sauvegarder une BD Izneo.
positional arguments:
  action                L'action à exécuter {infos,download,convert,pack,process}
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

- Pour récupérer la BD dans un répertoire d'images (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

- Pour récupérer la BD dans une archive CBZ en forçant le titre (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 --output-format cbz --output-filename "[Yusei Matsui] Assassination Classroom - Tome 1"
```

- Pour récupérer la BD dans une archive CBZ avec des images converties en WEBP (fichier de config présent) :  

```cmd
python izneo_get.py https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197 --output-format cbz --image-format webp --image-quality 70
```

- Récupérer tous les tomes d'une série :  

```cmd
python izneo_list.py --full-only URL > input.txt
python izneo_get.py --continue --output-format cbz --image-format webp --image-quality 70 input.txt
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

#### Utilisation (izneo_list)

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

- Pour récupérer la liste des liens d'une série (fichier de config présent) :  

```cmd
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567
```

- Pour récupérer la liste des liens d'une série, dans la limite des albums complets inclus dans l'abonnement en ajoutant le tag "--force-title" (fichier de config présent) :  

```cmd
python izneo_list.py https://www.izneo.com/fr/manga-et-simultrad/shonen/naruto-567 --full-only --force-title
```

- Pour récupérer la liste des liens de séries qui correspondent à la rechercher "largo" (fichier de config présent) :  

```cmd
python izneo_list.py "largo"
```

### izneo_infos

#### Utilisation (izneo_infos)

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

- Pour afficher les informations d'une BD :  

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

- Pour enregistrer les informations d'une BD dans un fichier :  

```cmd
python izneo_infos.py --output assassination-classroom-t1.json https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

ou

```cmd
python izneo_infos.py --output assassination-classroom-t1.xml https://www.izneo.com/fr/manga-et-simultrad/shonen/assassination-classroom-4744/assassination-classroom-t1-19197
```

### izneo_basket

#### Utilisation (izneo_basket)

```cmd
python izneo_basket.py [-h] [--session-id SESSION_ID] [--config CONFIG] url

Script pour obtenir une liste de BDs Izneo à partir de la page panier fin.

positional arguments:
  url                La page de panier fin qui contient une liste de BDs

options:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --config CONFIG       Fichier de configuration
```

Exemple :

- Pour récupérer la liste des liens d'une page de panier fin (fichier de config présent)
avec 1020304 le numéro de la commande :

```cmd
python izneo_basket.py https://www.izneo.com/fr/panier-fin/1020304
```

## Installation

### Prérequis

- Python 3.10+ (non testé avec les versions précédentes)
- `poetry` (recommandé) ou `pip`
- Librairies SSL

#### Sous Windows

##### Python

Allez sur ce site :  
<https://www.python.org/downloads/windows/>  
et suivez les instructions d'installation de Python 3.

##### Librairies SSL

- Vous pouvez essayer de les installer avec la commande :  

```cmd
pip install pyopenssl
```

- Vous pouvez télécharger [OpenSSL pour Windows](http://gnuwin32.sourceforge.net/packages/openssl.htm).  

#### Sous Linux

Si vous êtes sous Linux, vous n'avez pas besoin de moi pour installer Python, Pip ou SSL...  

### Installation (sous Linux)

- En ligne de commande, clonez le repo :  

```cmd
git clone https://github.com/izneo-get/izneo-get.git
cd izneo-get
```

#### Avec poetry (recommandé)

- Créez un environnement virtuel Python dédié :  

```cmd
poetry shell
```

- Installez les dépendances :  

```cmd
poetry install
```

#### Avec pip

- Créez un environnement virtuel Python dédié :  

```cmd
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
```

- Installez les dépendances :  

```cmd
python -m pip install -r requirements.txt
```

En cas de problème, on peut installer les dépendances à la main :  

```cmd
cd izneo-get
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pycryptodome
python -m pip install requests
python -m pip install beautifulsoup4
python -m pip install Pillow
python -m pip install inquirer
python -m pip install tqdm
python -m pip install opencv-python
python -m pip install pytest
```
  
## Alternative sans installer Python (sous Windows uniquement)  
  
- Vous pouvez télécharger uniquement le [binaire Windows](https://github.com/izneo-get/izneo-get/releases/latest) (expérimental).  

### Mémo

#### Mettre à jour le fichier `requirements.txt` depuis poetry

```
poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt
```
