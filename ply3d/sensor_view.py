import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import datetime
from numba import jit
import numpy as np
import os
import ply3d.view_control as vc


@jit
def plyfile_search(folder_path):
    # plyファイルの拡張子を取り除きファイル名だけを返す
    ply_file = []
    for file in os.listdir(folder_path):
        if file.endswith(".ply"):
            ply_file.append(''.join(os.path.splitext(file)[0]))
    return ply_file


@jit
def update_plyfile_dict(path, filelist):
    # 1.フォルダに入っているファイル名の辞書
    # {tool', ['filename1', 'filename2', ...]}
    # 2.ファイル名でファイルパスを取り出せるような辞書作成
    # {'f16','/ply3d/ply/vehicle/f16.ply'}
    global plyfile_dict
    filelist.sort()  # 昇順に並び替える(a,b,c,..)
    for i in range(len(filelist)):
        key = filelist[i]
        value = path + key + '.ply'
        plyfile_dict.update({key: value})


@jit
def create_plyfile_and_folder_dict(plyfolder_path, type_folder):
    # plyフォルダで種類別に作成したフォルダを検索し、
    # app.pyが置かれた階層をルートとする絶対パスを作成し、
    # 辞書化する関数に渡す
    global folder_dict
    for folder_name in type_folder:
        search_folder_path = plyfolder_path + '/' + folder_name + '/'
        plyfile_list = plyfile_search(search_folder_path)
        update_plyfile_dict(search_folder_path, list(plyfile_list))
        folder_dict.update({folder_name: list(plyfile_list)})


# Global variables
plyfolder_path = 'ply3d/ply'
type_folder = ['乗り物', '食べ物', '人物', '生物', '道具']

# Dictionaly
plyfile_dict = {}
folder_dict = {}
'''
一例
plyfile_dict.items() = [{'リンゴ', 'ply3d/ply/food/apple.ply'}, ...]
folder_dict.items() = [
                        {'乗り物', ['飛行機', 'ガレオン船', ...]},
                        {'食べ物', ['りんご']},
                        {'道具', ['ウォークマン', 'サンダル', ...]}, ...
                      ]
辞書取り出し
value = plyfile_dict['リンゴ']
print(value) # 'ply3d/ply/food/apple.ply'
'''
create_plyfile_and_folder_dict(plyfolder_path, type_folder)

# Webサーバ
app = dash.Dash(__name__, static_folder='static')

colors = {
    'background': '#ffffff',
    'plot_area': '#ffffff',
    'text': '#000000',
}

# ページの描写
app.title = 'Nagasaka Lab'
app.layout = html.Div([html.Meta(
    content='width=device-width, initial-scale=1.0'),
    html.Div([
        html.Div('3Dモデル切り替え',
                 style={'color': 'blue',
                        'fontsize': 16,
                        'font-weight': 'bold'}),
        html.Div(id='live-update-text'),
        dcc.RadioItems(
            id='type-dropdown',
            options=[{'label': k, 'value': k}
                     for k in folder_dict.keys()],
            value=sorted(folder_dict.keys())[0]
        ),
        dcc.RadioItems(
            id='filename-dropdown',
        ),
        html.Div([
            dcc.Graph(id='live-update-model3d',)
            # config={'displayModeBar': False})
        ]),
        html.Div([
            dcc.Graph(id='live-update-graph',)
            # config={'displayModeBar': False})
        ]),
        dcc.Interval(
            id='refresh_interval1',
            interval=3*1000,  # in milliseconds
            n_intervals=0,
        ),
        dcc.Interval(
            id='refresh_interval2',
            interval=2*1000,  # in milliseconds
        ),
    ]),
], style={'backgroundColor': colors['background'], 'color': colors['text']})


class Context:
    def __init__(self):
        self.t = []  # X-axis time
        self.pyroelectric_sensor = []

    @classmethod
    @jit
    def append_data(cls, d1, d2):
        n = len(d1)
        if n > 100:
            del d1[0: n - 99]
        d1.append(d2)


# Instance
context = Context()


class Random_data:
    def __init__(self):
        self.single_val = 0
        self.x = 0
        self.y = 0
        self.z = 0

    def start_sensor(self):
        self.single_val = np.random.randint(0, 100)
        self.x = int(np.random.randint(0, 999) / 3.92)
        self.y = int(np.random.randint(0, 999) / 3.92)
        self.z = int(np.random.randint(0, 999) / 3.92)

    def update_sensor(self):
        self.single_val = np.random.randint(0, 100)
        self.x = int(np.random.randint(0, 999) / 3.92)
        self.y = int(np.random.randint(0, 999) / 3.92)
        self.z = int(np.random.randint(0, 999) / 3.92)

    def three_axis(self):
        return [self.x, self.y, self.z]

    def zero_to_hundred(self):
        return self.single_val


# Instance
sensor = Random_data()
sensor.start_sensor()


@app.callback(Output('live-update-text', 'children'),
              events=[Event('refresh_interval1', 'interval')])
def update_metrics():
    x_axis, y_axis, z_axis = sensor.three_axis()
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('X: {}'.format(x_axis), style=style),
        html.Span('Y: {}'.format(y_axis), style=style),
        html.Span('Z: {}'.format(z_axis), style=style)
    ]


@app.callback(
    Output('filename-dropdown', 'options'),
    [Input('type-dropdown', 'value')])
def set_folder(selected_type):
    return [{'label': i, 'value': i} for i in folder_dict[selected_type]]


@app.callback(
    Output('filename-dropdown', 'value'),
    [Input('filename-dropdown', 'options')])
def set_filename(available_options):
    return available_options[0]['value']


@app.callback(
    Output('live-update-model3d', 'figure'),
    [Input('filename-dropdown', 'value'),
     Input('type-dropdown', 'value')],
    events=[Event('refresh_interval1', 'interval')])
def three_demention_model_viewer(selected_filename, selected_type):
    global plyfile_dict
    fig = plotly.tools.make_subplots(
        rows=1,
        cols=1,
        specs=[[{'is_3d': True}]]
    )
    sensor.update_sensor()
    vc.viewer(fig, sensor.three_axis(), selected_filename,
              plyfile_dict)  # view_control.py
    return fig


@app.callback(Output('live-update-graph', 'figure'),
              events=[Event('refresh_interval2', 'interval')])
def graph_setting():
    fig = plotly.tools.make_subplots(rows=1, cols=1)
    plot_colorful_graph(fig)
    # plot_colorful_cercle(fig)
    return fig


def plot_colorful_graph(fig):
    x_axis, y_axis, z_axis = sensor.three_axis()
    context.append_data(context.t, datetime.datetime.now())
    context.append_data(context.pyroelectric_sensor, np.random.randint(0, 100))

    # Create the graph with subplots
    fig['layout']['margin'] = {
        'l': 30, 'r': 20, 'b': 50, 't': 30
    }
    fig['layout']['plot_bgcolor'] = colors['plot_area']
    fig['layout']['paper_bgcolor'] = colors['background']
    fig['layout']['font'] = {'color': colors['text']}
    fig['layout']['yaxis1'].update(
        range=[0, 119]
    )
    fig['layout']['showlegend'] = False
    fig['layout'].update(
        dict(
            autosize=True,
            # width=900,  # autosize or manual size
            height=300,
        )
    )
    next_graph_setting = dict(
        x=context.t,
        y=context.pyroelectric_sensor,
        name='sensor',
        mode='lines+markers+text',
        text=context.pyroelectric_sensor,
        textposition='top center',
        fill='tonexty',
        # color setting
        fillcolor='rgba({0},{1},{2},{3})'.format(x_axis, y_axis, z_axis, 0.5),
        line=dict(color='rgba({0},{1},{2},{3})'.format(
            x_axis, y_axis, z_axis, 1.0)),
    )

    fig.append_trace(next_graph_setting, 1, 1)


'''
def plot_colorful_cercle(fig):
    # Create the cercle with subplots
    trace1 = go.Scatter(
        x=[0],
        y=[0],
        mode='markers',
        marker=dict(
            size=200,
            color='rgb({0},{1},{2},{3})'.format(
                sensor.rgb_val[0],
                sensor.rgb_val[1],
                sensor.rgb_val[2],
                0.5),
            colorscale='Viridis',
            line=dict(color='rgba({0},{1},{2},{3})'.format(
                sensor.rgb_val[0],
                sensor.rgb_val[1],
                sensor.rgb_val[2],
                1.0))
        )
    )
    fig['layout']['margin'] = {
        'l': 30, 'r': 20, 'b': 50, 't': 30
        # 'l': 30, 'r': 10, 'b': 30, 't': 15
    }
    fig['layout']['plot_bgcolor'] = colors['plot_area']
    fig['layout']['paper_bgcolor'] = colors['background']
    fig['layout']['showlegend'] = False
    fig['layout'].update(
        dict(
            autosize=True,
            # height=300,
        )
    )
    fig['layout']['xaxis1'].update(
        # range=[-20, 40],
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=False
    )
    fig['layout']['yaxis1'].update(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=False
    )
    fig.append_trace(trace1, 1, 2)
'''