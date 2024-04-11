from datetime import datetime
import pytz
import requests
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import math

from database import db
from config import PING_URL



def main():
    st.title("ATPing Ranking")

    st.subheader(f"Central Court :tennis: Availability")

    last_activity, time_diff = get_last_activity()

    st.write(f"Last activity: {last_activity} | {display_time_diff(time_diff)} ago")

    if st.button("Say I'm currently playing! :wave:"):
        update_last_activity()
        st.success("Ping sent successfully!")



    st.subheader(f"Current :crown: of the Hill: *{db.get_king()}*")

    st.subheader("Games Results")
    fig = network_plot(db.matches_df)
    st.plotly_chart(fig)


@st.cache_resource
def network_plot(matches_df):
    G = nx.MultiDiGraph()
    for _, row in matches_df.iterrows():
        G.add_edge(row["Player 1"], row["Player 2"])

    # Convert to undirected graph for edge width calculation
    H = G.to_undirected()

    # Calculate edge widths (number of matches between two players)
    edge_widths = {}
    for u, v in H.edges():
        edge_widths[(u, v)] = H.number_of_edges(u, v)

    # Calculate node sizes (number of wins)
    wins = db.matches_df["Winner"].value_counts().to_dict()
    games = (
        pd.concat([db.matches_df["Player 1"], db.matches_df["Player 2"]])
        .value_counts()
        .to_dict()
    )
    win_rates = {player: wins.get(player, 0) / games[player] for player in games}
    node_sizes = [
        math.log((games.get(node, 0) + 1)) * 10 for node in H.nodes()
    ]

    # Set positions using a layout algorithm
    pos = nx.kamada_kawai_layout(H)

    # Create traces for Plotly
    edge_traces = []
    for width in set(edge_widths.values()):
        # Select edges with the current width
        edge_x = []
        edge_y = []
        for u, v in H.edges():
            if edge_widths[(u, v)] == width:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y, line=dict(width=width, color="#888"), mode="lines"
        )
        edge_traces.append(edge_trace)

    # Create node trace for Plotly
    node_x = []
    node_y = []
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=[
            f"Player: {node}<br>Wins: {wins.get(node, 0)}<br>Lose: {games.get(node, 0) - wins.get(node, 0)}"
            for node in H.nodes()
        ],
        text=[node for node in H.nodes()],
        textposition="top center",
        marker=dict(
            size=node_sizes,
            color=[win_rates[node] if node in wins else 0 for node in H.nodes()],
            colorscale=["#111146", "#2bb6bf", "#e61f68"],
            cmin=0,
            cmax=1,
            showscale=True,
            colorbar=dict(
                thickness=15, title="Win rate", xanchor="left", titleside="right"
            ),
            line_width=2,
        ),
    )

    # Create the figure
    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig


def get_last_activity():
    response = requests.get( f"{PING_URL}/last_activity", timeout=5)
    response.raise_for_status()
    
    last_activity = response.json()["last_activity"]
    
    last_activity = datetime.fromisoformat(last_activity)

    last_activity_utc = last_activity.replace(tzinfo=pytz.utc)
    paris_tz = pytz.timezone("Europe/Paris")
    last_activity_paris_tz = paris_tz.normalize(last_activity_utc).strftime("%A %d %B %Y %H:%M:%S")

    time_diff = datetime.now(pytz.utc) - last_activity_utc

    return last_activity_paris_tz, time_diff

def display_time_diff(time_diff):
    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days == 0:
        if hours == 0:
            return f"{minutes} minutes"
        return f"{hours} hours, {minutes} minutes"
    
    return f"{days} days, {hours} hours, {minutes} minutes"


def update_last_activity():
    response = requests.get( f"{PING_URL}/ping_from_board", timeout=5)
    response.raise_for_status()


    

main()