"""

File: Visualizations.py
Used for all visualizations and animations related to the project

Inspired by https://www.kaggle.com/code/huntingdata11/plotly-animated-and-interactive-nfl-plays
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

    lineOfScrimmage = play.query('playId == @playId')['absoluteYardlineNumber'].iloc[0]
    lineOfScrimmagePlot = go.Scatter(
        x=[lineOfScrimmage, lineOfScrimmage],
        y=[0, 53.3],
        mode="lines",
        line=dict(color='black', width=2),
        showlegend=False
    )

    firstDownYard = lineOfScrimmage + play.query('playId == @playId')['yardsToGo'].iloc[0]
    firstDownPlot = go.Scatter(
        x=[firstDownYard, firstDownYard],
        y=[0, 53.3],
        mode="lines",
        line=dict(color='yellow', width=2),
        showlegend=False
    )

    teamNamesPlot = go.Scatter(
        x=[5, 115],
        y=[27, 27],
        mode="text",
        text=[homeTeam, visitingTeam],
        textfont=dict(color="white", size=30, family="Courier New"),
        showlegend=False
    )

    topHashmarksPlot = go.Scatter(
        x=[i for i in range(10, 110)],
        y=[53.3 - 23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    topYardMarkersPlot = go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[43.5 for _ in range(10)],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    bottomYardmarkersPlot = go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[10 for _ in range(10)],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    bottomHashmarksPlot = go.Scatter(
        x=[i for i in range(10, 110)],
        y=[23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    # Create the frames
    frames = []
    for frame_id in tracking['frameId'].unique():
        playersScatterPlot = go.Scatter(
            x=tracking.query('frameId == @frame_id')['x'],
            y=tracking.query('frameId == @frame_id')['y'],
            text=tracking.query('frameId == @frame_id')['jerseyNumber'],
            mode="markers+text",
            marker=dict(
                color=[nfl_teams_colors[club][0] for club in tracking.query('frameId == @frame_id')['club']],
                size=16,
                line=dict(
                    color=[nfl_teams_colors[club][1] for club in tracking.query('frameId == @frame_id')['club']],
                    width=1
                )
            ),
            textfont=dict(
                family="Arial",
                size=8,
                color="white"
            )
        )

        frame = go.Frame(
            data=[teamNamesPlot, topHashmarksPlot, bottomHashmarksPlot, topYardMarkersPlot, bottomYardmarkersPlot, firstDownPlot, lineOfScrimmagePlot,  playersScatterPlot])
        frames.append(frame)

    # Create the figure
    fig = go.Figure(
        data=[
            teamNamesPlot,
            topHashmarksPlot,
            bottomHashmarksPlot,
            topYardMarkersPlot,
            bottomYardmarkersPlot,
            firstDownPlot,
            lineOfScrimmagePlot,
            go.Scatter(
                x=tracking.query('frameId == 1')['x'],
                y=tracking.query('frameId == 1')['y'],
                text=tracking.query('frameId == 1')['jerseyNumber'],
                mode="markers+text",
                marker=dict(
                    color=[nfl_teams_colors[club][0] for club in tracking.query('frameId == 1')['club']],
                    size=16,
                    line=dict(
                        color=[nfl_teams_colors[club][1] for club in tracking.query('frameId == 1')['club']],
                        width=1
                    )
                ),
                textfont=dict(
                    family="Arial",
                    size=8,
                    color="white"
                )
            )
        ],
        layout=go.Layout(
            plot_bgcolor='green',
            xaxis=dict(
                range=[0, 120],
                autorange=False,
                zeroline=False,
                showgrid=True,
                showticklabels=False,
                gridwidth=2,
                tickwidth=5,
                tickvals=list(range(10, 111, 5))
            ),
            yaxis=dict(
                range=[0, 53.3],
                autorange=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False
            ),
            hovermode="closest",
            showlegend=False,
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, {"frame": {"duration": 100, "redraw": False}}]
                              )]
            )]
        ),
        frames=frames
    )

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

    # Add down marker
    # Use the first down yard variable from above
    fig.add_shape(type="rect",
                  x0=firstDownYard, y0=51.3, x1=firstDownYard+2, y1=53.3,
                  line=dict(color='black'),
                  fillcolor='orange',
                  layer='below')

    # Add the down on top of the down marker
    fig.add_scatter(x=[firstDownYard+1],
                    y=[52],
                    mode="text",
                    text=str(play.query('playId == @playId')['down'].iloc[0]),
                    line=dict(color='black'),
                    fillcolor='orange')

    fig.show()


if __name__ == '__main__':
    games = pd.read_csv("data/games.csv")
    players = pd.read_csv("data/players.csv")
    plays = pd.read_csv("data/plays.csv")
    tackles = pd.read_csv("data/tackles.csv")
    tracking = pd.read_csv("data/tracking_week_1.csv")

    animatePlay(games, players, plays, tracking, gameId=2022090800, playId=167)
