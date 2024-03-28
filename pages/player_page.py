import streamlit as st
from database import db

def players_page():

    update_needed = False
    if "loaded" not in st.session_state:
        st.session_state.loaded = True
        db.load_data()

    st.header("Registered Players")
    
    # Display the table of players before checking for updates
    st.table(db.players_df.sort_values("Elo", ascending=False).reset_index(drop=True))

    st.subheader("Add Player")
    new_player = st.text_input("Enter player name", key="new_player")
    if st.button("Add Player"):
        db.add_player(new_player)
        st.success(f"Player {new_player} added successfully!")
        # Flag that the table needs to be refreshed
        update_needed = True

    st.subheader("Remove Player")
    remove_player = st.selectbox("Select player to remove", db.players_df["Player"], key="remove_player")
    if st.button("Remove Player"):
        db.remove_player(remove_player)
        st.success(f"Player {remove_player} removed successfully!")
        # Flag that the table needs to be refreshed
        update_needed = True

    # Refresh the table if there was an update
    if update_needed:
        st.experimental_rerun()

players_page()

