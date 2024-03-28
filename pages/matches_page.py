import streamlit as st
from database import db

def matches_page():
    update_needed = False  # Initialize a variable to track if the table needs to be updated

    st.header("Match Results")
    st.table(db.matches_df)

    st.subheader("Add Match Result")
    player1 = st.selectbox("Select Player 1", db.players_df["Player"])
    player2 = st.selectbox("Select Player 2", db.players_df["Player"])
    winner = st.selectbox("Select Winner", [player1, player2])
    if st.button("Add Match"):
        db.add_match(player1, player2, winner)
        st.success("Match result added successfully!")
        update_needed = True  # Set the flag to True to indicate the table needs to be refreshed

    st.subheader("Remove Match")
    if len(db.matches_df) > 0:
        match_index = st.number_input("Enter match index to remove", min_value=0, max_value=len(db.matches_df) - 1)
        if st.button("Remove Match"):
            db.remove_match(match_index)
            st.success("Match removed successfully!")
            update_needed = True  # Set the flag to True to indicate the table needs to be refreshed
    else:
        st.write("No matches to remove.")

    # Check if the table needs to be refreshed due to an update
    if update_needed:
        st.experimental_rerun()  # Refresh the table to reflect the changes

matches_page()