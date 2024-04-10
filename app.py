import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import math

from database import db



def main():
    st.title("ATPing Ranking")
    network_plot()


def network_plot():
    G = nx.MultiDiGraph()
    for _, row in db.matches_df.iterrows():
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
    node_sizes = [
        math.log((wins.get(node, 0) + 1)) * 20 for node in H.nodes()
    ]  # Multiply by 10 for better visualization

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
            color=[
                wins[node] if node in wins else 0 for node in H.nodes()
            ],  # Color can be a list of values, here we use number of wins
            colorscale=["#111146", "#2bb6bf", "#e61f68"],
            showscale=True,
            colorbar=dict(
                thickness=15, title="Number of Wins", xanchor="left", titleside="right"
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
    # width=2000

    # Display the figure
    st.plotly_chart(fig)

main()