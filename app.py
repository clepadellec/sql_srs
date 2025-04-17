import streamlit as st
import duckdb
import pandas as pd

# Create a DuckDB in-memory database
con = duckdb.connect(database=":memory:")
# Create tables and insert data
con.execute("CREATE TABLE students (id INTEGER, name TEXT, grade INTEGER)")
con.execute(
    "INSERT INTO students VALUES (1, 'Alice', 85), (2, 'Bob', 78), (3, 'Cathy', 92)"
)
con.execute("CREATE TABLE courses (student_id INTEGER, course TEXT)")
con.execute("INSERT INTO courses VALUES (1, 'Math'), (2, 'Science'), (3, 'Literature')")

st.header("Mode de Révision SQL")

theme = st.sidebar.selectbox(
    "Choisissez le thème de révision:",
    ["Sélection de données", "Agrégation", "Jointures", "Sous-requêtes"],
)

questions = {
    "Sélection de données": (
        "SELECT name FROM students WHERE grade > 80",
        "Quelles sont les étudiantes ayant une note supérieure à 80?",
    ),
    "Agrégation": (
        "SELECT avg(grade) FROM students",
        "Quelle est la moyenne des notes?",
    ),
    "Jointures": (
        "SELECT s.name, c.course FROM students s JOIN courses c ON s.id = c.student_id",
        "Liez les étudiants à leurs cours.",
    ),
    "Sous-requêtes": (
        "SELECT name FROM students WHERE grade = (SELECT max(grade) FROM students)",
        "Quel est l'étudiant avec la meilleure note?",
    ),
}

correct_answer, question = questions[theme]

st.write(question)
user_query = st.text_area("Écrivez votre requête SQL ici:")
expected_result = con.execute(correct_answer).fetch_df()
if st.button("Vérifier la réponse"):
    try:
        user_result = con.execute(user_query).fetch_df()

        if user_result.equals(expected_result):
            st.success("Correct!")
        else:
            if set(user_result.columns) == set(expected_result.columns) and len(
                user_result
            ) == len(expected_result):
                st.error(
                    "Incorrect! Les différences sont mises en évidence ci-dessous."
                )
                st.write(user_result.compare(expected_result))
            else:
                st.error(
                    "Incorrect! La structure des résultats ne correspond pas à ce qui est attendu."
                )

        st.dataframe(user_result)
    except Exception as e:
        st.error(f"Erreur dans l'exécution de la requête: {e}")

with st.expander("Détails de l'énoncé"):
    st.write("**Contenu des tables :**")
    st.write("**students**")
    st.dataframe(con.execute("SELECT * FROM students").fetch_df())
    st.write("**courses**")
    st.dataframe(con.execute("SELECT * FROM courses").fetch_df())
    st.write("**Résultat attendu :**")
    st.dataframe(expected_result)

con.close()
