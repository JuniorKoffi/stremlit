import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Étape 2 : Créer la base de données
conn = psycopg2.connect(
    host="localhost",
    database="base",
    user="postgres",
    password="admin"
)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS mes_donnees
             (id SERIAL PRIMARY KEY,
             nom TEXT,
             prix REAL NOT NULL);''')
conn.commit()
conn.close()

# Étape 4 : Connexion à la source de données
file_type = st.sidebar.selectbox("Choisir le type de fichier", ["CSV", "Excel"])
if file_type == "CSV":
    uploaded_file = st.sidebar.file_uploader("Télécharger le fichier CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
elif file_type == "Excel":
    uploaded_file = st.sidebar.file_uploader("Télécharger le fichier Excel", type=["xlsx", "xls"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)

# Nettoyage des données
if st.sidebar.checkbox("Nettoyage des données"):
    # Supprimer les lignes avec des valeurs manquantes
    df.dropna(inplace=True)
    # Renommer les colonnes
    df.rename(columns={"nom": "nom", "prix": "prix"}, inplace=True)

if st.sidebar.checkbox("Ajout de colonne"):
    # Obtenir le nom de la nouvelle colonne
    new_col_name = st.sidebar.text_input("Nom de la nouvelle colonne")
    # Obtenir le nom de la colonne existante pour laquelle la nouvelle colonne sera calculée
    existing_col_name = st.sidebar.selectbox("Nom de la colonne existante", df.columns)
    # Appliquer la fonction à la colonne existante pour créer la nouvelle colonne
    def my_function(x):
        # Appliquer une opération quelconque sur la colonne existante pour créer la nouvelle colonne
        return x*2
    df[new_col_name] = df[existing_col_name].apply(my_function)
    # Enregistrer le DataFrame mis à jour dans un fichier CSV
    csv_file = st.sidebar.text_input("Nom du fichier CSV", value="data.csv")
    df.to_csv(csv_file, index=False)
    # Afficher le tableau de données mis à jour avec la nouvelle colonne
    st.dataframe(df)



# Suppression de colonne
if st.sidebar.checkbox("Suppression de colonne"):
    # Obtenir le nom de la colonne à supprimer
    col_to_delete = st.sidebar.selectbox("Choisir la colonne à supprimer", df.columns)
    # Supprimer la colonne
    if st.sidebar.button("Supprimer la colonne"):
        df.drop(col_to_delete, axis=1, inplace=True)

# Ajout de champ calculé
if st.sidebar.checkbox("Ajout de champ calculé"):
    # Obtenir les noms des colonnes à multiplier
    col1 = st.sidebar.selectbox("Choisir la première colonne", df.columns)
    col2 = st.sidebar.selectbox("Choisir la deuxième colonne", df.columns)
    # Ajouter le champ calculé
    if st.sidebar.button("Ajouter le champ calculé"):
        df["Prix double"] = df[col1] * df[col2]

# Étape 5 : Génération du tableau de bord
if st.sidebar.button("Générer le tableau de bord"):
    # Connexion à la base de données
    conn = psycopg2.connect(
        host="localhost",
        database="base",
        user="postgres",
        password="admin"
    )
    # Ajout des données à la base de données
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute("INSERT INTO mes_donnees (nom, prix) VALUES (%s, %s)", (row['nom'], row['prix']))
    conn.commit()
    # Lire les données à partir de la base de données
    cursor = conn.cursor()
    cursor.execute("SELECT nom, SUM(prix) from mes_donnees GROUP BY nom")
    data = cursor.fetchall()
    conn.close()
    # Création du graphique en barres
    df = pd.DataFrame(data, columns=['nom', 'Total'])
    fig = px.bar(df, x='nom', y='Total', title='Total des prix par produit')
    st.plotly_chart(fig)

# Étape 10 : Visualisation du tableau de données
if st.sidebar.checkbox("Visualiser le tableau de données"):
    # Connexion à la base de données
    conn = psycopg2.connect(
        host="localhost",
        database="base",
        user="postgres",
        password="admin"
    )
    # Lecture des données à partir de la base de données
    df = pd.read_sql_query("SELECT * FROM mes_donnees", conn)
    conn.close()
    # Affichage du tableau de données
    st.dataframe(df)
