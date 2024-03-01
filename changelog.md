# Changelog

## izneo_get.py

### Version 1.1.1 (2024-03-01)

- [FIX] Problème avec les noms de séries qui possèdent des caractères spéciaux.

### Version 1.1.0 (2024-02-02)

- [NEW] Possibilité de télécharger les livres du site  `archive.org`.

### Version 1.0.5 (2023-12-01)

- [FIX] Bug sur le traitement de l'extension ".zip".

### Version 1.0.3 (2023-11-13)

- [FIX] Gestion des erreurs quand une page n'est pas disponible sur Izneo.

### Version 1.0.2 (2023-10-15)

- [FIX] Valeurs par défaut quand il n'y a pas d'information sur un livre.

### Version 1.0.1 (2023-10-07)

- [FIX] Compatibilité avec les fichiers de médiathèque.

### Version 1.0.0 (2023-09-09)

- [NEW] Possibilité d'utiliser l'application en mode interactif.
- [NEW] Téléchargement asynchrone et multithread lorsque aucune pause entre 2 pages est demandée.
- [NEW] Possibilité d'effectuer le post-traitement sans télécharger.
- [CHANGE] Barre de progression.
- [TECH] Refacto du code.
- [TECH] Utilisation de `Poetry`.

### Version 0.09.03 (2021-12-16)

- [BUGFIX] Gestion des espaces en fin de nom de fichier.

### Version 0.09.02 (2021-11-26)

- [NEW] Vérification de la version.
- [CHANGE] Suppression d'un paramètre inutile.
- [BUGFIX] Ajout compatibilité avec les tomes empruntés par médiathèque.

### Version 0.09.00 (2021-06-07)

- [NEW] Ajout compatibilité avec les tomes empruntés par médiathèque.

### Version 0.08.02 (2021-03-01)

- [BUGFIX] Gestion du cas quand il y a plus de 99 tomes.

### Version 0.08.01 (2020-11-08)

- [BUGFIX] Gestion du cas des tomes non renseignés.

### Version 0.08.0 (2020-10-05)

- [CHANGE] Script is blacked.
- [CHANGE] Disparition de l'option "--no-tree" qui devient le comportement par défaut.
- [CHANGE] Apparition de l'option "--tree" qui permet de forcer la création des sous-répertoires.
- [CHANGE] Compatibilité "webtoons".
- [BUGFIX] Le script déchiffre les images.

## izneo_list.py

### Version 0.08 (2023-09-10)

- [ADD] Possibilité de faire la liste de sa bibliothèque avec `izneo_list.py bibliotheque`.

### Version 0.07 (2022-09-17)

- [CHANGE] La récupération d'albums ne peut se faire qu'à partir de l'URL d'une série.
- [CHANGE] La recherche textuelle retourne les URL des séries.

### Version 0.06 (2021-03-15)

- [CHANGE] Modification de la façon de récupérer les listes (corrige le problème avec les séries de plus de 40 tomes).

## izneo_infos.py

### Version 0.01 (2022-11-26)

- [NEW] Version initiale.

## izneo_get_selenium.py

### Version 1.04.0 (2020-10-04)

- [CHANGE] Récupération des images depuis les blobs.
- [CHANGE] Compatibilité "webtoons".

### Version 1.03.0 (2020-09-14)

- [BUGFIX] Compatibilité PIL version 7.

### Version 1.02.0 (2020-09-13)

- [BUGFIX] Erreur lorsqu'on donne un fichier contenant une liste d'URLs.

### Version 1.01.0 (2020-09-13)

- [CHANGE] Le fichier de config n'est plus écrasé.
- [CHANGE] La recherche du binaire "chromebrowser*.exe" est désormais récursive.

### Version 1.00.0 (2020-09-08)

- [NEW] Nouvelle version basée sur Selenium.
- [CHANGE] Disparition de l'option "--no-tree" qui devient le comportement par défaut.
- [CHANGE] Apparition de l'option "--tree" qui permet de forcer la création des sous-répertoires.
