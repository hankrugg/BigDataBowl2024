"""

File: Visualizations.py
Used for all visualizations and animations related to the project

Inspired by https://www.kaggle.com/code/huntingdata11/plotly-animated-and-interactive-nfl-plays
"""

import pandas as pd
import plotly.graph_objects as go

from Constants import nfl_teams_colors
from Preprocessing import create_acceleration_vectors, create_velocity_vectors


def animatePlay(games: pd.DataFrame, plays: pd.DataFrame, tracking: pd.DataFrame, gameId: int,
                playId: int, acceleration=False, velocity=False):
    """
    Function to animate a singular play for a given game

    :param games: DataFrame containing games data
    :param plays: DataFrame containing plays data
    :param tracking: DataFrame containing tracking data
    :param gameId: ID of the game to animate
    :param playId: ID of the play to animate
    :param acceleration: Boolean indicating whether to show acceleration vectors. Default is false
    :param velocity: Boolean indicating whether to show velocity vectors. Default is false
    """
    # Filter data based on gameId and playId
    game = games.query('gameId == @gameId')
    play = plays.query('playId == @playId and gameId == @gameId')
    tracking = tracking.query('playId == @playId and gameId == @gameId')
    home_team = games.query('gameId == @gameId')['homeTeamAbbr'].unique()[0]
    visiting_team = games.query('gameId == @gameId')['visitorTeamAbbr'].unique()[0]
    down = int(plays.query('playId == @playId')['down'].iloc[0])
    line_of_scrimmage = play.query('playId == @playId')['absoluteYardlineNumber'].iloc[0]

    # Plot the line of scrimmage in black
    line_of_scrimmage_plot = go.Scatter(
        x=[line_of_scrimmage, line_of_scrimmage],
        y=[0, 53.3],
        mode="lines",
        line=dict(color='black', width=2),
        showlegend=False
    )

    # Plot the first down yard line in yellow
    first_down_yard = line_of_scrimmage + play.query('playId == @playId')['yardsToGo'].iloc[0] if \
    tracking.query('playId == @playId')['playDirection'].iloc[0] == 'Right' else line_of_scrimmage - \
                                                                                 play.query('playId == @playId')[
                                                                                     'yardsToGo'].iloc[0]
    first_down_plot = go.Scatter(
        x=[first_down_yard, first_down_yard],
        y=[0, 53.3],
        mode="lines",
        line=dict(color='yellow', width=2),
        showlegend=False
    )

    # Plot the team names in each endzone
    team_names_plot = go.Scatter(
        x=[5, 115],
        y=[27, 27],
        mode="text",
        text=[home_team, visiting_team],
        textfont=dict(color="white", size=30, family="Courier New"),
        showlegend=False
    )

    # Plot the top hashmarks
    top_hashmarks_plot = go.Scatter(
        x=[i for i in range(10, 110)],
        y=[53.3 - 23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    # Plot the yard numbers on the top
    top_yardmarkers_plot = go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[43.5 for _ in range(10)],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    # Plot the yardmarkers on the bottom
    bottom_yardmarkers_plot = go.Scatter(
        x=[20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        y=[10 for _ in range(10)],
        mode="text",
        text=['10', '20', '30', '40', '50', '40', '30', '20', '10'],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    # Plot the hashmarks on the bottom
    bottom_hashmarks_plot = go.Scatter(
        x=[i for i in range(10, 110)],
        y=[23.58 for i in range(10, 110)],
        mode="text",
        text=['|' for i in range(10, 110)],
        textfont=dict(color="white", size=35, family="Courier New"),
        showlegend=False
    )

    # Create the frames
    # Keep a list of all the different plots that need to be updated in each frame
    frames = []
    for frame_id in tracking['frameId'].unique():

        tracking_frame = tracking.query('frameId == @frame_id')

        players_scatter_plot = go.Scatter(
            x=tracking_frame['x'],
            y=tracking_frame['y'],
            text=tracking_frame['jerseyNumber'],
            # Use markers and text mode to show each player as a circle(marker) and each circle have the jersey
            # number(text) inside the circle(marker)
            mode="markers+text",
            # Make each marker correspond to the nfl_team_colors stored in Constants.py
            marker=dict(
                color=[nfl_teams_colors[club][0] for club in tracking_frame['club']],
                size=16,
                line=dict(
                    color=[nfl_teams_colors[club][1] for club in tracking_frame['club']],
                    width=1
                )
            ),
            textfont=dict(
                family="Arial",
                size=8,
                color="white"
            )
        )

        # Collect x and y coordinates for all players' velocity vectors
        x_start = tracking_frame['x'].to_numpy()
        y_start = tracking_frame['y'].to_numpy()
        x_2_velo = (tracking_frame['x_velocity_component'] + x_start).to_numpy()
        y_2_velo = (tracking_frame['y_velocity_component'] + y_start).to_numpy()
        x_2_accel = (tracking_frame['x_acceleration_component'] + x_start).to_numpy()
        y_2_accel = (tracking_frame['y_acceleration_component'] + y_start).to_numpy()

        # Create lists to store x and y coordinates for lines
        x_lines_velo = []
        y_lines_velo = []

        x_lines_accel = []
        y_lines_accel = []

        # Iterate through players to create line segments
        for i in range(len(tracking_frame)):

            # These if statements are needed to either show or not show the velocity and acceleration vectors
            # They will be created but will be empty if the respective variable is not set to TRUE
            if velocity:
                x_lines_velo.extend([x_start[i], x_2_velo[i], None])  # Use None to separate lines
                y_lines_velo.extend([y_start[i], y_2_velo[i], None])  # Use None to separate lines
            if acceleration:
                x_lines_accel.extend([x_start[i], x_2_accel[i], None])  # Use None to separate lines
                y_lines_accel.extend([y_start[i], y_2_accel[i], None])  # Use None to separate lines

        # Create the velocity plot
        velocity_plot = go.Scatter(
            x=x_lines_velo,
            y=y_lines_velo,
            mode='lines',
            line=dict(color='black')
        )

        # Create the acceleration plot
        acceleration_plot = go.Scatter(
            x=x_lines_accel,
            y=y_lines_accel,
            mode='lines',
            line=dict(color='red')
        )
        # Create the frame with all elements
        frame = go.Frame(
            data=[team_names_plot, top_hashmarks_plot, bottom_hashmarks_plot, top_yardmarkers_plot,
                  bottom_yardmarkers_plot, first_down_plot, line_of_scrimmage_plot, velocity_plot,
                  acceleration_plot, players_scatter_plot])
        frames.append(frame)

    # Create the figure
    # This is the initial figure that will be shown before the play button is clicked
    fig = go.Figure(
        data=[
            team_names_plot,
            top_hashmarks_plot,
            bottom_hashmarks_plot,
            top_yardmarkers_plot,
            bottom_yardmarkers_plot,
            first_down_plot,
            line_of_scrimmage_plot,
            go.Scatter(),  # Placeholder for the velocity plot. It should not be shown to start
            go.Scatter(),  # Placeholder for the acceleration plot. It should not be shown to start
            go.Scatter(
                x=tracking.query('frameId == 1')['x'],
                y=tracking.query('frameId == 1')['y'],
                text=tracking.query('frameId == 1')['jerseyNumber'],
                # Use markers and text mode to show each player as a circle(marker) and each circle have the jersey
                # number(text) inside the circle(marker)
                mode="markers+text",
                # Make each marker correspond to the nfl_team_colors stored in Constants.py
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
            ),
        ],
        # Details of the plot
        layout=go.Layout(
            # Background green
            plot_bgcolor='green',
            xaxis=dict(
                # 0-120 because of the 10 yard endzones
                range=[0, 120],
                autorange=False,
                zeroline=False,
                # Use the gridlines as the 5-yard lines
                showgrid=True,
                showticklabels=False,
                gridwidth=2,
                tickwidth=5,
                # 5-yard lines every 5 yards from 10-110
                tickvals=list(range(10, 111, 5))
            ),
            yaxis=dict(
                range=[0, 53.3],
                autorange=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False
            ),
            # Create the play button and make each frame last 0.1 second or 100 milliseconds
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

    # Add colored endzones based on the team
    fig.add_shape(type="rect",
                  x0=0, y0=0, x1=10, y1=53.3,
                  line=dict(color=nfl_teams_colors[home_team][1]),
                  fillcolor=nfl_teams_colors[home_team][0],
                  layer="below")

    # Add colored endzones based on the team
    fig.add_shape(type="rect",
                  x0=110, y0=0, x1=120, y1=53.3,
                  line=dict(color=nfl_teams_colors[visiting_team][1]),
                  fillcolor=nfl_teams_colors[visiting_team][0],
                  layer="below")

    # Add down marker
    # Use the first down yard variable from above
    fig.add_shape(type="rect",
                  x0=first_down_yard, y0=51.3, x1=first_down_yard + 2, y1=53.3,
                  line=dict(color='black'),
                  fillcolor='orange',
                  layer="below")

    # Add the down on top of the down marker
    fig.add_scatter(x=[first_down_yard + 1],
                    y=[52],
                    mode="text",
                    text=str(play.query('playId == @playId')['down'].iloc[0]),
                    line=dict(color='black'))

    fig.show()


if __name__ == '__main__':
    games = pd.read_csv("data/games.csv")
    players = pd.read_csv("data/players.csv")
    plays = pd.read_csv("data/plays.csv")
    tackles = pd.read_csv("data/tackles.csv")

    tracking = []
    for i in range(1, 10):
        tracking.append(pd.read_csv(f"data/tracking_week_{i}.csv"))
    tracking = pd.concat(tracking)

    tracking = create_acceleration_vectors(tracking)

    tracking = create_velocity_vectors(tracking)

    animatePlay(games, plays, tracking, gameId=2022102310, playId=1318, velocity=True, acceleration=True)
