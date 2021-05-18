# ProjetSPQR
## Projet de fin de formation

### Pré-requis :

* psycopg2-binary version 2.8.6
* jupyter-lab version 3.0.9
* pandas version 1.2.3
* sqlalchemy version 1.3.23
* numpy version 1.20.1
* matplotlib version 3.3.4


### Contexte du projet :
Notre client est un site Internet éducatif sur le thème de l’Histoire, à destination des jeunes, étudiants ou amateurs. Il aimerait développer un service permettant de trouver facilement des informations sur des personnalités historiques de l'antiquité romaine et aimerait pour cela disposer d'une base de données simple et navigable.

### Contenu du dépôt :

* Fichier README
* Fichier requirements.txt pour l'installation des librairies utilisées
* Fichier script.py qu'il suffit de lancer pour créer, formater et remplir la base de données
* Notebook TestBDD.ipynb qui contient à peu près le même code que le fichier script.py mais sous format notebook
* Notebook RequetesSQL.ipynb avec quelques requêtes pour interroger la base de données
* Notebook Visualisations.ipynb où on peut voir la génération de graphiques avec matplotlib
* Fichier LAMBERT Philippe dossier certification data Nantes 2021.pdf qui explique le déroulement du projet
* Répertoire data/ avec les fichiers csv utilisés, ainsi qu'un fichier json contenant 
* Fichier metadata.py qui permet de créer au sein du répertoire data/ un fichier json contenant les métadonnées des différents fichiers csv


### Étapes pour installer et lancer le projet :
* Copier le dépôt

```git clone https://gitlab.com/simplon-dev-data-nantes-2020/projet-chef-d-oeuvre/-/tree/PhilippeLambert```
* Créer son environnement virtuel avec Git Bash

```python3 -m venv nomDeEnv```

* Activer son environnement sous Windows avec GitBash

```source nomDeEnv/Scripts/activate```

* Installer jupyter-lab et toutes les librairies python nécessaires

```pip install -r requirements.txt```
* Aller dans le dépôt projet-chef-d-oeuvre

```cd projet```

Afin d'accéder aux scripts il nous faut lancer jupyter lab :

```jupyter lab```
