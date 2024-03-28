import streamlit as st
from database import db

def matches_page():
    st.header("Match Results")
    st.table(db.matches_df)

    st.subheader("Add Match Result")
    player1 = st.selectbox("Select Player 1", db.players_df["Player"])
    player2 = st.selectbox("Select Player 2", db.players_df["Player"])
    winner = st.selectbox("Select Winner", [player1, player2])
    if st.button("Add Match"):
        db.add_match(player1, player2, winner)
        st.success("Match result added successfully!")

    st.subheader("Remove Match")
    if len(db.matches_df) > 0:
        match_index = st.number_input("Enter match index to remove", min_value=0, max_value=len(db.matches_df) - 1)
        if st.button("Remove Match"):
            db.remove_match(match_index)
            st.success("Match removed successfully!")
    else:
        st.write("No matches to remove.")


matches_page()