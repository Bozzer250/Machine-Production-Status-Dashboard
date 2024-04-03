import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

data = {
    'Machine': ['Machine 1', 'Machine 1', 'Machine 1', 'Machine 2', 'Machine 2'],
    'Start Time': ['2024-03-21 08:00:00', '2024-03-21 09:30:00', '2024-03-21 11:00:00', '2024-03-21 10:00:00', '2024-03-21 12:00:00'],
    'End Time': ['2024-03-21 09:00:00', '2024-03-21 10:00:00', '2024-03-21 12:00:00', '2024-03-21 11:00:00', '2024-03-21 13:00:00'],
    'State': [0, 1, 2, 1, 2]
}

df = pd.DataFrame(data)
df['Start Time'] = pd.to_datetime(df['Start Time'])
df['End Time'] = pd.to_datetime(df['End Time'])

app = dash.Dash(__name__)

colors = {'background': '#f0f0f0', 'text': '#333333'}

dropdown_style = {'fontSize': '18px'}
label_style = {'fontSize': '20px', 'marginRight': '10px', 'color': colors['text']}
info_div_style = {'marginTop': '20px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'backgroundColor': '#ffffff'}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("Machine Production Status Dashboard", style={'textAlign': 'center', 'color': colors['text']}),

    html.Div([
        html.Label("Select Machine:", style=label_style),
        dcc.Dropdown(
            id='machine-dropdown',
            options=[{'label': machine, 'value': machine} for machine in df['Machine'].unique()],
            value=df['Machine'].unique()[0],
            clearable=False,
            style=dropdown_style
        ),
    ], style={'width': '50%', 'margin': 'auto', 'textAlign': 'center', 'padding': '20px'}),

    html.Div([
        html.Label("Filter by State:"),
        dcc.Dropdown(
            id='state-dropdown',
            options=[
                {'label': 'Off Mode', 'value': 1},
                {'label': 'Idle Mode', 'value': 1},
                {'label': 'Production Mode', 'value': 2}
            ],
            value=None,
            clearable=True
        ),
    ], style={'width': '50%', 'margin': 'auto', 'textAlign': 'center', 'padding': '10px'}),

    dcc.Graph(id='machine-status', config={'editable': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 800, 'width': 1000}}),

    html.Div(id='machine-info', style=info_div_style),
])


@app.callback(
    Output('machine-info', 'children'),
    [Input('machine-status', 'selectedData'),
     Input('machine-status', 'clickData')]
)
def update_info(selectedData, clickData):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id']
        if prop_id == 'machine-status.selectedData':
            if selectedData is not None and 'range' in selectedData:
                x_range = [selectedData['range']['x'][0], selectedData['range']['x'][1]]
                y_range = [selectedData['range']['y'][0], selectedData['range']['y'][1]]
                return f"X range: {x_range}, Y range: {y_range}"
            else:
                return "No data selected"
        elif prop_id == 'machine-status.clickData':
            if clickData is not None:
                point_index = clickData['points'][0]['pointIndex']
                machine = df.loc[point_index, 'Machine']
                start_time = df.loc[point_index, 'Start Time']
                end_time = df.loc[point_index, 'End Time']
                state = df.loc[point_index, 'State']
                return html.Div([
                    html.H2(f"Machine: {machine}"),
                    html.P(f"Start Time: {start_time}"),
                    html.P(f"End Time: {end_time}"),
                    html.P(f"State: {state}")
                ])

    return "No data selected"


@app.callback(
    Output('machine-status', 'figure'),
    [Input('machine-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_graph(selected_machine, selected_state):
    filtered_df = df.copy()
    if selected_machine:
        filtered_df = filtered_df[filtered_df['Machine'] == selected_machine]
    if selected_state is not None:
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    fig = px.timeline(filtered_df, x_start='Start Time', x_end='End Time', y='Machine', color='State',
                      color_discrete_map={0: '#ff0000', 1: '#ffff00', 2: '#008000'})
    fig.update_yaxes(categoryorder='total ascending')
    fig.update_layout(title="Machine Production Status",
                      xaxis_title="Time",
                      yaxis_title="Machine",
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font=dict(color=colors['text'])
                      )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
