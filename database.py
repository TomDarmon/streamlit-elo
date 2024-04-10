import pandas as pd
from config import GCS_BUCKET, DEFAULT_ELO, ENV

class Database:
    def __init__(self):
        self.players_file = f"gs://{GCS_BUCKET}/players_{ENV}.csv"
        self.matches_file = f"gs://{GCS_BUCKET}/matches_{ENV}.csv"
        self.players_df = None
        self.matches_df = None
        self.load_data()

    def load_data(self):
        try:
            self.players_df = pd.read_csv(self.players_file, dtype={"Elo": int})
        except FileNotFoundError:
            self.players_df = pd.DataFrame(columns=["Player", "Elo"], dtype={"Elo": int})

        try:
            self.matches_df = pd.read_csv(self.matches_file, dtype={"Elo Change P1": int, "Elo Change P2": int})
        except FileNotFoundError:
            self.matches_df = pd.DataFrame(columns=["Player 1", "Player 2", "Winner", "Date", "Elo Change P1", "Elo Change P2"])

    def save_data(self):
        self.players_df.to_csv(self.players_file, index=False)
        self.matches_df.to_csv(self.matches_file, index=False)

    def add_player(self, player):
        if player not in self.players_df["Player"].values:
            new_row = pd.DataFrame({"Player": [player], "Elo": [DEFAULT_ELO]}).astype({"Elo": int})
            self.players_df = pd.concat([self.players_df, new_row], ignore_index=True)
            self.save_data()

    def remove_player(self, player):
        self.players_df = self.players_df[self.players_df["Player"] != player]
        self.save_data()

    def add_match(self, player1, player2, winner):
        elo_change = self.update_elo(player1, player2, winner)

        new_row = pd.DataFrame({
            "Player 1": [player1],
            "Player 2": [player2],
            "Winner": [winner],
            "Date": [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')],
            "Elo Change P1": [int(elo_change[0])],  # Cast to int
            "Elo Change P2": [int(elo_change[1])]   # Cast to int
        })
        self.matches_df = pd.concat([self.matches_df, new_row], ignore_index=True)
        self.save_data()

    def remove_match(self, index):
        try:
            match_to_remove = self.matches_df.loc[index]
            player1, player2 = match_to_remove['Player 1'], match_to_remove['Player 2']
            elo_change_player1, elo_change_player2 = match_to_remove['Elo Change P1'], match_to_remove['Elo Change P2']
            self.players_df.loc[self.players_df["Player"] == player1, "Elo"] -= elo_change_player1
            self.players_df.loc[self.players_df["Player"] == player2, "Elo"] -= elo_change_player2
            self.matches_df = self.matches_df.drop(index).reset_index(drop=True)
            self.save_data()
        except KeyError:
            print(f"No match found at index {index}.")

    def compute_elo_change(self, player1, player2, winner):
        k = 32
        player1_elo = self.players_df.loc[self.players_df["Player"] == player1, "Elo"].values[0]
        player2_elo = self.players_df.loc[self.players_df["Player"] == player2, "Elo"].values[0]

        player1_expected = 1 / (1 + 10 ** ((player2_elo - player1_elo) / 400))
        player2_expected = 1 / (1 + 10 ** ((player1_elo - player2_elo) / 400))

        if winner == player1:
            player1_new_elo = player1_elo + k * (1 - player1_expected)
            player2_new_elo = player2_elo + k * (0 - player2_expected)
        else:
            player1_new_elo = player1_elo + k * (0 - player1_expected)
            player2_new_elo = player2_elo + k * (1 - player2_expected)

        return player1_new_elo, player2_new_elo

    def update_elo(self, player1, player2, winner):
        player1_new_elo, player2_new_elo = self.compute_elo_change(player1, player2, winner)
        elo_change_player1 = int(player1_new_elo) - self.players_df.loc[self.players_df["Player"] == player1, "Elo"].values[0]
        elo_change_player2 = int(player2_new_elo) - self.players_df.loc[self.players_df["Player"] == player2, "Elo"].values[0]
        self.players_df.loc[self.players_df["Player"] == player1, "Elo"] = int(player1_new_elo)
        self.players_df.loc[self.players_df["Player"] == player2, "Elo"] = int(player2_new_elo)
        return elo_change_player1, elo_change_player2

db = Database()
