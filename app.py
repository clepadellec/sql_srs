import streamlit as st
import duckdb
import pandas as pd

# Create a DuckDB in-memory database
con = duckdb.connect(database=':memory:')
# Create a sample table and insert data
con.execute('CREATE TABLE students (id INTEGER, name TEXT, grade INTEGER)')
con.execute("INSERT INTO students VALUES (1, 'Alice', 85), (2, 'Bob', 78), (3, 'Cathy', 92)")
st.header("Mode de Révision SQL")

query = st.text_area("Écrivez votre requête SQL ici:")
if st.button("Exécuter la requête"):
    try:
        result = con.execute(query).df()
        st.dataframe(result)
    except Exception as e:
        st.error(f"Erreur: {e}")

# Close the connection when done
con.close()
