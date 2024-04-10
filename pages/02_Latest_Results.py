import streamlit as st
from database import db

def latest_results_page():
    update_needed = False  # Initialize a variable to track if the table needs to be updated

    if "loaded" not in st.session_state:
        st.session_state.loaded = True
        db.load_data()

    st.header("Match Results")
    match_table = st.empty()
    match_table.table(db.matches_df)

    st.subheader("Add Match Result")
    player1 = st.selectbox("Select Player 1", db.players_df["Player"])
    player2 = st.selectbox("Select Player 2", db.players_df["Player"])
    winner = st.selectbox("Select Winner", [player1, player2])
    if st.button("Add Match"):
        db.add_match(player1, player2, winner)
        st.success("Match result added successfully!")
        match_table.table(db.matches_df)

    st.subheader("Remove Match")
    if len(db.matches_df) > 0:
        match_index = st.number_input("Enter match index to remove", min_value=0, max_value=len(db.matches_df) - 1)
        if st.button("Remove Match"):
            db.remove_match(match_index)
            st.success("Match removed successfully!")
            match_table.table(db.matches_df)
    else:
        st.write("No matches to remove.")

latest_results_page()
