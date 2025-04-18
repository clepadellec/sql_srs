import os
import logging
import shutil
import duckdb
import streamlit as st
from datetime import date, timedelta
import pandas as pd

if not "data" in os.listdir():
    logging.info("Création du dossier data")
    os.mkdir("data")


if "exercises_sql_tables.duckdb" not in os.listdir("data"):
    exec(open("init_db.py").read())

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

# con.execute(open("new_exercise_mappings.sql").read())

# mappings_df = con.execute("SELECT * FROM theme_exercise_mapping").df()
# exercise_name_mapping = dict(
#     zip(mappings_df["exercise_name"], mappings_df["display_name"])
# )


def check_users_solution(user_query: str):
    result = con.execute(user_query).df()
    st.dataframe(result)
    try:
        result = result[solution_df.columns]
        comparison = result.compare(solution_df)
        st.dataframe(comparison)

        if comparison.empty:
            st.success("Correct!")
            st.balloons()
        else:
            st.error("Certaines valeurs sont incorrectes.")
    except KeyError:
        st.error("Certaines colonnes sont manquantes")
    n_lines_difference = result.shape[0] - solution_df.shape[0]
    if n_lines_difference != 0:
        st.warning(
            f"Le résultat a une différence de {n_lines_difference} lignes par rapport à la solution."
        )


st.sidebar.title("Sélection d'exercice")
available_themes_df = con.execute("SELECT DISTINCT theme FROM memory_state").df()
theme = st.sidebar.selectbox(
    "Sélectionnez un thème à réviser :", available_themes_df["theme"].unique(), index=0
)

if theme:
    st.sidebar.write(f"Vous avez sélectionné **{theme}**")
    exercises_query = f"SELECT * FROM memory_state WHERE theme = '{theme}'"
else:
    exercises_query = "SELECT * FROM memory_state"

exercises_df = (
    con.execute(exercises_query)
    .df()
    .sort_values("last_reviewed")
    .reset_index(drop=True)
)

if "exercise_name" not in exercises_df or exercises_df["exercise_name"].isnull().any():
    st.error("Certaines données d'exercice manquent.")
    st.stop()

display_exercises_df = exercises_df.copy()
display_exercises_df["display_name"] = display_exercises_df["exercise_name"]
exercise_display_name = st.sidebar.selectbox(
    "Sélectionnez un exercice :", display_exercises_df["display_name"].dropna(), index=0
)

exercise_name = display_exercises_df[
    display_exercises_df["display_name"] == exercise_display_name
]["exercise_name"].iloc[0]
st.sidebar.write(f"Exercice sélectionné: **{exercise_display_name}**")

st.title("Exercices pratiques SQL")

exercise_info = exercises_df[exercises_df["exercise_name"] == exercise_name].iloc[0]
exercise_tables = exercise_info["tables"]
with st.expander("Détails de l'exercice", expanded=True):
    st.write(f"**Nom de l'exercice**: {exercise_name}")
    st.write(f"**Thème**: {theme}")
    st.write("**Tables pertinentes**:")
    for table in exercise_tables:
        st.write(f"**{table}**")
        df_table = con.execute(f"SELECT * FROM {table}").df()
        st.dataframe(df_table)

with open(f"answers/{exercise_name}.sql", "r") as f:
    answer = f.read()

solution_df = con.execute(answer).df()

st.header("Entrez votre requête SQL :")
query = st.text_area(label="Votre requête SQL", key="user_input", height=200)
submit_button = st.button("Soumettre la requête")

if submit_button and query:
    check_users_solution(query)

st.sidebar.header("Planifier la révision")
for n_days in [2, 7, 21]:
    if st.sidebar.button(f"Réviser dans {n_days} jours", key=f"review_{n_days}"):
        next_review = date.today() + timedelta(days=n_days)
        con.execute(
            f"UPDATE memory_state SET last_reviewed = '{next_review}' WHERE exercise_name = '{exercise_name}'"
        )
        st.success(f"Révision planifiée dans {n_days} jours!")
        st.experimental_set_query_params()
if st.sidebar.button("Réinitialiser toutes les révisions"):
    con.execute("UPDATE memory_state SET last_reviewed = '1970-01-01'")
    st.success("Tous les plannings de révision ont été réinitialisés!")
    st.experimental_set_query_params()
st.sidebar.header("Onglet de solution")
if st.sidebar.checkbox("Afficher la requête de solution", key="solution"):
    st.subheader("Requête de solution")
    st.code(answer, language="sql")
