import os
import psycopg2
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine

# On a defini un mot de passe secret dans les variables systeme, par securite.
mot_passe = os.environ.get('pg_psw')

# On se connecte a Postgres, dans la base par defaut "postgres".
conn = psycopg2.connect(
   database="postgres",
   user='postgres',
   password=mot_passe,
   host='localhost',
   port='5432'
)
conn.autocommit = True

# On definit un curseur.
cursor = conn.cursor()

# On cree une nouvelle base de donnees nommee "ProjetSPQR".
sql = '''CREATE database ProjetSPQR;'''

cursor.execute(sql)
print("Base de données créée avec succès !")

# On se deconnecte de la base par defaut "postgres".
conn.close()

# On se reconnecte, cette fois a la base "ProjetSPQR"
conn = psycopg2.connect(
   database="projetspqr",
   user='postgres',
   password=mot_passe,
   host='localhost',
   port='5432'
)
conn.autocommit = True

cursor = conn.cursor()


# On definit une fonction pour creer des tables dans la bdd.
def creer_table(conn, sql_creation_table):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_creation_table)
        conn.commit()
    except psycopg2.Error as e:
        print("Erreur lors de la création de la table")
        print(e)
        return
    cursor.close()
    print("La table a été crée avec succès")

# On ecrit la requete de creation de chaque table.
sql_creer_table_personne = """
    CREATE TABLE IF NOT EXISTS personne (
    id integer,
    nom_fr text,
    praenomen text,
    nomen text,
    cognomen text,
    gens text,
    sexe text,
    date_naissance date,
    lieu_naissance text,
    date_mort date,
    lieu_mort text,
    id_pere integer,
    id_mere integer,
    PRIMARY KEY(id)
    );
"""

sql_creer_table_activite = """
    CREATE TABLE IF NOT EXISTS activite (
    personne_id integer,
    activite text,
    CONSTRAINT fk_personne
        FOREIGN KEY(personne_id)
            REFERENCES personne(id)
    );
"""

sql_creer_table_poste = """
    CREATE TABLE IF NOT EXISTS poste (
    personne_id integer,
    poste text,
    CONSTRAINT fk_personne
        FOREIGN KEY(personne_id)
            REFERENCES personne(id)
    );
"""

sql_creer_table_mariage = """
    CREATE TABLE IF NOT EXISTS mariage (
    id serial,
    id_mari integer,
    id_epouse integer,
    PRIMARY KEY(id),
    CONSTRAINT fk_personne
        FOREIGN KEY(id_mari)
            REFERENCES personne(id),
        FOREIGN KEY(id_epouse)
            REFERENCES personne(id)
    );
"""

sql_creer_table_oeuvre = """
    CREATE TABLE IF NOT EXISTS oeuvre (
    id integer,
    titre_fr text,
    titre_lat text,
    auteur_id integer,
    genre text,
    PRIMARY KEY(id),
    CONSTRAINT fk_personne
        FOREIGN KEY(auteur_id)
            REFERENCES personne(id)
);
"""

creer_table(conn, sql_creer_table_personne)
creer_table(conn, sql_creer_table_activite)
creer_table(conn, sql_creer_table_poste)
creer_table(conn, sql_creer_table_mariage)
creer_table(conn, sql_creer_table_oeuvre)

# On place les donnees csv dans un dataframe pour les manipuler facilement.
df_personne = pd.read_table("data/query_personne.csv", delimiter=",")

# On ajoute les resultats de requetes complementaires (on dédoublonnera apres).
df_kingdom = pd.read_table("data/query_kingdom.csv", delimiter=",")
df_early_republic = pd.read_table("data/query_early_republic.csv", delimiter=",")
df_middle_republic = pd.read_table("data/query_middle_republic.csv", delimiter=",")
df_late_republic = pd.read_table("data/query_late_republic.csv", delimiter=",")
df_high_empire = pd.read_table("data/query_high_empire.csv", delimiter=",")
df_low_empire = pd.read_table("data/query_low_empire.csv", delimiter=",")

df_personne = df_personne.append(df_kingdom, ignore_index=True)
df_personne = df_personne.append(df_early_republic, ignore_index=True)
df_personne = df_personne.append(df_middle_republic, ignore_index=True)
df_personne = df_personne.append(df_late_republic, ignore_index=True)
df_personne = df_personne.append(df_high_empire, ignore_index=True)
df_personne = df_personne.append(df_low_empire, ignore_index=True)

# On renomme les colonnes.
df_personne.rename(columns={"item": "id",
                            "itemLabel": "nom_fr",
                            "praenomenLabel": "praenomen",
                            "nomenLabel": "nomen",
                            "cognomenLabel": "cognomen",
                            "gensLabel": "gens",
                            "sexeLabel": "sexe",
                            "pere": "id_pere",
                            "mere": "id_mere"},
                   inplace=True)

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
df_personne['id'] = df_personne.id.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)
df_personne['id_pere'] = df_personne.id_pere.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)
df_personne['id_mere'] = df_personne.id_mere.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)

# On supprime les doublons.
df_personne.drop_duplicates(subset="id", keep="first", inplace=True)

# On supprime les codes d'erreur qui remplacent certaines valeurs manquantes.
df_personne = df_personne.replace(
    to_replace='t[0-9]+',
    value=np.nan,
    regex=True)
df_personne = df_personne.replace(
    to_replace='^Q[0-9]+',
    value=np.nan,
    regex=True)

# On supprime la mention inutile de l'heure et fuseau horaire dans les dates.
df_personne['date_naissance'] = df_personne.date_naissance.str.replace(
    'T00:00:00Z',
    '',
    regex=True)
df_personne['date_mort'] = df_personne.date_mort.str.replace(
    'T00:00:00Z',
    '',
    regex=True)

# On remplace les annees negatives en annees BC (Before Christ) pour l'import.
df_personne = df_personne.replace(
    r"^-([0-9]*-[0-9]*-[0-9]*)$",
    r"\1BC",
    regex=True)
# On renomme l'annee 0 qui n'existe pas en annee 1BC pour l'import.
df_personne = df_personne.replace(
    r"^0000(-[0-9]*-[0-9]*)$",
    r"0001\1BC",
    regex=True)

# On remplace les NaN de pandas (type float) en None, pour l'import.
df_personne = df_personne.where(pd.notnull(df_personne), None)

# On place les donnees csv dans un dataframe pour les manipuler facilement.
df_activite = pd.read_table("data/query_activite.csv", delimiter=",")

# On renomme les colonnes.
df_activite.rename(columns={"item": "personne_id",
                            "occupationLabel": "activite"},
                   inplace=True)

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
df_activite['personne_id'] = df_activite.personne_id.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)

# On supprime les codes d'erreur qui remplacent certaines valeurs manquantes.
df_activite = df_activite.replace(
    to_replace='^t[0-9]+',
    value=np.nan,
    regex=True)
df_activite = df_activite.replace(
    to_replace='^Q[0-9]+',
    value=np.nan,
    regex=True)

# On remplace les NaN de pandas (type float) en None, pour l'import.
df_activite = df_activite.where(pd.notnull(df_activite), None)

# On place les donnees csv dans un dataframe pour les manipuler facilement.
df_poste = pd.read_table("data/query_poste.csv", delimiter=",")

# On renomme les colonnes.
df_poste.rename(columns={"item": "personne_id",
                         "positionLabel": "poste"},
                inplace=True)

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
df_poste['personne_id'] = df_poste.personne_id.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)

# On supprime les codes d'erreur qui remplacent certaines valeurs manquantes.
df_poste = df_poste.replace(
    to_replace='t[0-9]+',
    value=np.nan,
    regex=True)
df_poste = df_poste.replace(
    to_replace='^Q[0-9]+',
    value=np.nan,
    regex=True)

# On remplace les NaN de pandas (type float) en None, pour l'import.
df_poste = df_poste.where(pd.notnull(df_poste), None)

# On place les donnees csv dans un dataframe pour les manipuler facilement.
df_oeuvre = pd.read_table(
    "data/query_oeuvre.csv",
    delimiter=",")

# On renomme les colonnes.
df_oeuvre.rename(columns={"oeuvre": "id",
                          "oeuvreLabel": "titre_fr",
                          "titre": "titre_lat",
                          "auteur": "auteur_id",
                          "genreLabel": "genre"},
                 inplace=True)

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
for index, row in df_oeuvre.iterrows():
    e = df_oeuvre.at[index, 'id']
    e.replace('http://www.wikidata.org/entity/Q', '')

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
df_oeuvre['id'] = df_oeuvre.id.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)
df_oeuvre['auteur_id'] = df_oeuvre.auteur_id.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)

# On supprime les doublons.
df_oeuvre.drop_duplicates(subset="id", keep="first", inplace=True)

# On supprime les codes d'erreur qui remplacent certaines valeurs manquantes.
df_oeuvre = df_oeuvre.replace(
    to_replace='^t[0-9]+',
    value=np.nan,
    regex=True)
df_oeuvre = df_oeuvre.replace(
    to_replace='^Q[0-9]+',
    value=np.nan,
    regex=True)

# On remplace les NaN de pandas (type float) en None, pour l'import.
df_oeuvre = df_oeuvre.where(pd.notnull(df_oeuvre), None)

# On place les donnees csv dans un dataframe pour les manipuler facilement.
df_mariage = pd.read_table("data/query_mariage.csv", delimiter=",")

# On renomme les colonnes.
df_mariage.rename(columns={"item": "id_mari",
                           "epouse": "id_epouse"},
                  inplace=True)

# On ne retient pour les id que l'identifiant unique Wikidata, sans le Q.
df_mariage['id_mari'] = df_mariage.id_mari.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)
df_mariage['id_epouse'] = df_mariage.id_epouse.str.replace(
    'http://www.wikidata.org/entity/Q',
    '',
    regex=True)

# On supprime les codes d'erreur qui remplacent certaines valeurs manquantes.
df_mariage = df_mariage.replace(
    to_replace='^t[0-9]+',
    value=np.nan,
    regex=True)
df_mariage = df_mariage.replace(
    to_replace='^Q[0-9]+',
    value=np.nan,
    regex=True)

# On supprime les lignes ou il n'y a pas d'id d'epouse.
df_mariage.dropna(subset=["id_epouse"], inplace=True)

# On cree une liste des id de personne dans la base.
personne_id_list = df_personne['id'].tolist()

# On filtre les mariages avec des personnes exterieures a la base.
for e in df_mariage['id_epouse']:
    if e not in personne_id_list:
        df_mariage.drop(
            df_mariage.loc[df_mariage['id_epouse'] == e].index,
            inplace=True)

# Pareil pour les autres tables
for e in df_activite['personne_id']:
    if e not in personne_id_list:
        df_activite.drop(
            df_activite.loc[df_activite['personne_id']==e].index,
            inplace=True)

for e in df_poste['personne_id']:
    if e not in personne_id_list:
        df_poste.drop(
            df_poste.loc[df_poste['personne_id']==e].index,
            inplace=True)

# On reinitialise l'index apres les suppressions
df_mariage = df_mariage.reset_index(drop=True)

# On rajoute une colonne avec un id pour chaque mariage
df_mariage.insert(0, 'id', range(0, len(df_mariage)))

# Requetes SQL d'insertion des donnees dans les tables
sql_insert_personne = """INSERT INTO personne (
    id,
    nom_fr,
    praenomen,
    nomen,
    cognomen,
    gens,
    sexe,
    date_naissance,
    lieu_naissance,
    date_mort,
    lieu_mort,
    id_pere,
    id_mere) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

sql_insert_oeuvre = """INSERT INTO oeuvre (
    id,
    titre_fr,
    titre_lat,
    auteur_id,
    genre) VALUES (%s, %s, %s, %s, %s)"""

sql_insert_poste = """INSERT INTO poste (personne_id, poste) VALUES (%s, %s)"""

sql_insert_activite = """INSERT INTO activite (
    personne_id,
    activite) VALUES (%s, %s)"""

sql_insert_mariage = """INSERT INTO mariage (
    id,
    id_mari,
    id_epouse) VALUES (%s, %s, %s)"""

# On insere les donnees.
for index, row in df_personne.iterrows():
    cursor.execute(sql_insert_personne, tuple(row))

for index, row in df_oeuvre.iterrows():
    cursor.execute(sql_insert_oeuvre, tuple(row))

for index, row in df_activite.iterrows():
    cursor.execute(sql_insert_activite, tuple(row))

for index, row in df_poste.iterrows():
    cursor.execute(sql_insert_poste, tuple(row))

for index, row in df_mariage.iterrows():
    cursor.execute(sql_insert_mariage, tuple(row))

# On ferme la connexion a la base de donnees.
conn.close()
