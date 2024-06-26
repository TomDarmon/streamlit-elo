import streamlit as st
from database import db

def players_page():
    if "loaded" not in st.session_state:
        st.session_state.loaded = True
        db.load_data()

    st.header("Registered Players")
    
    # Display the current table of players
    players_table = st.empty()
    players_table.table(db.players_df.sort_values("Elo", ascending=False).reset_index(drop=True))

    st.subheader("Add Player")
    new_player = st.text_input("Enter player name", key="new_player")
    if st.button("Add Player"):
        db.add_player(new_player)
        st.success(f"Player {new_player} added successfully!")
        # Update the displayed table with the new player
        players_table.table(db.players_df.sort_values("Elo", ascending=False).reset_index(drop=True))

    st.subheader("Remove Player")
    remove_player = st.selectbox("Select player to remove", db.players_df["Player"], key="remove_player")
    if st.button("Remove Player"):
        db.remove_player(remove_player)
        st.success(f"Player {remove_player} removed successfully!")
        # Update the displayed table after removing the player
        players_table.table(db.players_df.sort_values("Elo", ascending=False).reset_index(drop=True))


players_page()
