"""

File: Visualizations.py
Used for all visualizations and animations related to the project
"""

import pandas as pd
import plotly.graph_objects as go

from Constants import nfl_teams_colors


def animatePlay(games: pd.DataFrame, players: pd.DataFrame, plays: pd.DataFrame, tracking: pd.DataFrame, gameId: int,
                playId: int):
    """
    Function to animate a singular play for a given game

    :param games: DataFrame containing games data
    :param players: DataFrame containing players data
    :param plays: DataFrame containing plays data
    :param tracking: DataFrame containing tracking data
    :param gameId: ID of the game to animate
    :param playId: ID of the play to animate
    """
    # Filter data based on gameId and playId
    game = games.query('gameId == @gameId')
    play = plays.query('playId == @playId and gameId == @gameId')
    tracking = tracking.query('playId == @playId and gameId == @gameId')
    homeTeam = games.query('gameId == @gameId')['homeTeamAbbr'].unique()[0]
    visitingTeam = games.query('gameId == @gameId')['visitorTeamAbbr'].unique()[0]

    frames = []  # Create an empty list to store the frame data for animation
    for frame_id in tracking['frameId'].unique():  # Iterate over unique frameIds
        frame_data = go.Scatter(
            x=tracking.query('frameId == @frame_id')['x'],  # X-coords of all the players and football at this frame
            y=tracking.query('frameId == @frame_id')['y'],  # X-coords of all the players and football at this frame
            text=tracking.query('frameId == @frame_id')['jerseyNumber'],
            # Jersey of all the players and football at this frame
            mode="markers+text",
            marker=dict(
                color=[nfl_teams_colors[club][0] for club in tracking.query('frameId == @frame_id')['club']],
                # List of colors to set each marker
                size=16,
                line=dict(
                    color=[nfl_teams_colors[club][1] for club in tracking.query('frameId == @frame_id')['club']],
                    # List of colors to set the outline of each marker
                    width=1
                )
            ),
            # Details of jersey number text
            textfont=dict(
                family="Arial",
                size=8,
                color="white"
            ),
        )
        # Make a plotly frame with the data and append it to the comprehensive frame list
        frame = go.Frame(data=[frame_data])
        frames.append(frame)

    fig = go.Figure(
        # Plot initial frame data at frameID of 1
        data=[
            go.Scatter(x=tracking.query('frameId == 1')['x'],
                       y=tracking.query('frameId == 1')['y'],
                       text=tracking.query('frameId == 1')['jerseyNumber'],
                       mode="markers+text",
                       marker=dict(
                           color=[nfl_teams_colors[club][0] for club in tracking.query('frameId == 1')['club']],
                           # List of colors to set each marker
                           size=16,
                           line=dict(
                               color=[nfl_teams_colors[club][1] for club in
                                      tracking.query('frameId == 1')['club']],
                               # List of colors to set the outline of each marker
                               width=1
                           )
                       ),
                       textfont=dict(
                           family="Arial",
                           size=8,
                           color="white"
                       ),
                       )
        ],

        # Details of the plot
        layout=go.Layout(
            plot_bgcolor='green',
            # X-axis grid to show the yard-lines
            xaxis=dict(range=[0, 120], autorange=False, zeroline=False, showgrid=True, showticklabels=False, gridwidth=2, tickwidth=5,
                       tickvals=list(range(10, 111, 5))),
            # Don't show any horizontal gridlines
            yaxis=dict(range=[0, 53.3], autorange=False, zeroline=False, showgrid=False, showticklabels=False),
            hovermode="closest",
            showlegend=False,
            # Frames are shown every tenth (0.1) of a second or 100 milliseconds
            # Make a play button to start the animation
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, {"frame": {"duration": 100, "redraw": True}}]
                              )]
            )]
        ),
        frames=frames
    )
    # Add the team names to the endzones
    fig.add_trace(go.Scatter(
        x=[5, 115],
        y=[27, 27],
        mode="text",
        text=[homeTeam, visitingTeam],
        textfont=dict(color="white",
                      size=30),
        showlegend=False
    ))

    # Add the yard markers 10 yards from the bottom (separated from top for readability)
    fig.add_trace(go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white",
                      size=35,
                      family="Courier New"),
        showlegend=False
    ))

    # Add the yard markers 10 yards from the top (separated from bottom for readability)
    fig.add_trace(go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[43.5, 43.5, 43.5, 43.5, 43.5, 43.5, 43.5, 43.5, 43.5, 43.5],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white",
                      size=35,
                      family="Courier New"),
        showlegend=False
    ))

    # Add hashmarks to the bottom, 23.58 yards from the bottom sideline
    fig.add_trace(go.Scatter(
        x=[i for i in range(10, 110)],
        y=[23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white",
                      size=35,
                      family="Courier New"),
        showlegend=False
    ))

    # Add hashmarks to the top, 23.58 yards from the top sideline
    fig.add_trace(go.Scatter(
        x=[i for i in range(10, 110)],
        y=[53.3 - 23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white",
                      size=35,
                      family="Courier New"),
        showlegend=False,
        name='hashmarks',
        marker=dict(opacity=0),
        # Making markers fully transparent
    ))

    # Add colored endzones
    fig.add_shape(type="rect",
                  x0=0, y0=0, x1=10, y1=53.3,
                  line=dict(color=nfl_teams_colors[homeTeam][1]),
                  fillcolor=nfl_teams_colors[homeTeam][0],
                  layer="below")

    # Add colored endzones
    fig.add_shape(type="rect",
                  x0=110, y0=0, x1=120, y1=53.3,
                  line=dict(color=nfl_teams_colors[visitingTeam][1]),
                  fillcolor=nfl_teams_colors[visitingTeam][0],
                  layer="below")
    # Display the figure in Jupyter Notebook
    fig.show()


if __name__ == '__main__':
    games = pd.read_csv("data/games.csv")
    players = pd.read_csv("data/players.csv")
    plays = pd.read_csv("data/plays.csv")
    tackles = pd.read_csv("data/tackles.csv")
    tracking = pd.read_csv("data/tracking_week_1.csv")

    animatePlay(games, players, plays, tracking, gameId=2022091103, playId=3126)
