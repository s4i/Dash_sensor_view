import concurrent.futures as pool
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
from ply3d.class_sensor import Sensor_value
import time


def main():
    # Webサーバ起動
    app.run_server(host='localhost', port=5000, debug=True,
                   threaded=True)


'''
plyファイル(3Dオブジェクト)の検索
'''


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
app = dash.Dash(name=__name__)
app.css.append_css(
    {'external_url': 'https://rawgit.com/s4i/Sensor_view/master/static/css/config.css'})

colors = {
    'background': '#ffffff',
    'plot_area': '#ffffff',
    'text': '#000000',
}

'''
センサー値関連
'''
# Instance
sensor = Sensor_value()

'''
update_metrics関数で利用
'''


def update_sensor():
    '''
    isRandをTrueにするとclass_sensor.pyにおいて、
    乱数が生成され、それが使われる。
    Falseの場合、x,y,zに入った値を反映できる。
    '''
    sensor.update_sensor(isRandom=True,
                         single=100, x=1023, y=1023, z=1023,
                         )


'''
ページの描写関連
'''
app.title = 'Nagasaka Lab'
app.layout = html.Div([html.Meta(
    content='width=device-width, initial-scale=1.0'),
    html.Div([
        html.Div('センサ値',
                 style={'color': 'red',
                        'fontsize': 12,
                        'font-weight': 'bold'}),
        html.Div(id='live-update-text'),
        html.Div('3Dモデル切り替え',
                 style={'color': 'blue',
                        'fontsize': 12,
                        'font-weight': 'bold'}),
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
        ),
        dcc.Interval(
            id='refresh_interval2',
            interval=3*1000,  # in milliseconds
        ),
    ]),
], style={'backgroundColor': colors['background'], 'color': colors['text']})


@app.callback(Output('live-update-text', 'children'),
              events=[Event('refresh_interval1', 'interval')])
def update_metrics():
    update_sensor()
    pyro = sensor.get_zero_to_hundred()
    x_axis, y_axis, z_axis = sensor.get_three_axis()

    x_axis = x_axis-510
    y_axis = y_axis-510
    cameraThe = ((x_axis + (90-((1024/2)*(1.65/2.5))/4)) * np.pi/180)
    cameraPhi = ((y_axis - (((1024/2)*(1.65/2.5))/4-45)) * np.pi/180)
    x_cam = np.cos(cameraThe) * np.cos(cameraPhi)
    y_cam = np.sin(cameraPhi)
    z_cam = np.sin(cameraThe) * np.cos(cameraPhi)

    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('3軸加速度センサ:', style=style),
        html.Span('X軸({:4d})'.format(x_axis), style=style),
        html.Span('Y軸({:4d})'.format(y_axis), style=style),
        html.Span('Z軸({:4d})'.format(z_axis), style=style),
        html.Span('焦電センサ', style=style),
        html.Span('({:3d})'.format(pyro), style=style),
        html.Div(),
        html.Span(' カメラ位置:', style=style),
        html.Span('X軸({:3.3f})'.format(x_cam), style=style),
        html.Span('Y軸({:3.3f})'.format(y_cam), style=style),
        html.Span('Z軸({:3.3f})'.format(z_cam), style=style),
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
    x_axis, y_axis, z_axis = sensor.get_three_axis()

    fig = plotly.tools.make_subplots(
        rows=1,
        cols=1,
        specs=[[{'is_3d': True}]]
    )

    # 枠線、罫線なし
    noaxis = dict(
        showbackground=False,
        showline=False,
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title=''
    )

    '''
    x_cam = x_axis/150.0
    y_cam = y_axis/150.0
    z_cam = z_axis/150.0
    '''

    #cameraRadius = 0.1

    cameraThe = ((x_axis + (90-((1024/2)*(1.65/2.5))/4)) * np.pi/180)
    cameraPhi = ((y_axis - (((1024/2)*(1.65/2.5))/4-45)) * np.pi/180)
    # Z軸は使わない
    '''
    x_cam = cameraRadius * np.cos(cameraThe) * np.cos(cameraPhi)
    y_cam = cameraRadius * np.sin(cameraPhi)
    z_cam = cameraRadius * np.sin(cameraThe) * np.cos(cameraPhi)
    '''
    x_cam = np.cos(cameraThe) * np.cos(cameraPhi)
    y_cam = np.sin(cameraPhi)
    z_cam = np.sin(cameraThe) * np.cos(cameraPhi)

    '''
    if -1.0 < x_cam and x_cam < 1.0:
        x_cam = 1.0
    if -1.0 < y_cam and y_cam < 1.0:
        y_cam = -1.0
    if -1.0 < z_cam and z_cam < 1.0:
        z_cam = 1.0
    '''

    fig['layout'].update(
        dict(
            autosize=True,
            # width=900,  # autosize or manual size
            height=590,
            scene=dict(
                xaxis=noaxis,
                yaxis=noaxis,
                zaxis=noaxis,
                aspectratio=dict(x=1.6, y=1.6, z=0.8),  # Front position
                camera=dict(
                    eye=dict(
                        x=x_cam,
                        y=y_cam,
                        z=z_cam,
                    )
                )
            )
        )
    )

    fig['layout']['margin'] = {'l': 0, 'r': 0, 'b': 0, 't': 0}
    data3 = vc.viewer(fig, selected_filename, plyfile_dict)  # view_control.py

    # Subplot descript
    fig.append_trace(data3, 1, 1)

    return fig


@app.callback(Output('live-update-graph', 'figure'),
              events=[Event('refresh_interval2', 'interval')])
def graph_setting():
    fig = plotly.tools.make_subplots(rows=1, cols=1)
    plot_colorful_graph(fig)
    # plot_colorful_cercle(fig)
    return fig


class Context:
    def __init__(self):
        self.t = []  # X-axis time
        self.zero_to_hundred = []

    @classmethod
    @jit
    def append_data(cls, d1, d2):
        n = len(d1)
        if n > 8:
            del d1[0: n - 7]
        d1.append(d2)


# Instance
context = Context()


def plot_colorful_graph(fig):
    x_axis, y_axis, z_axis = sensor.get_three_axis()

    context.append_data(context.t, datetime.datetime.now())
    context.append_data(context.zero_to_hundred, sensor.get_zero_to_hundred())

    # Create the graph with subplots
    fig['layout']['margin'] = {
        'l': 30, 'r': 20, 'b': 30, 't': 0
    }
    fig['layout']['plot_bgcolor'] = colors['plot_area']
    fig['layout']['paper_bgcolor'] = colors['background']
    fig['layout']['font'] = {'color': colors['text']}
    fig['layout']['yaxis1'].update(
        range=[0, 115]
    )
    fig['layout']['showlegend'] = False
    fig['layout'].update(
        dict(
            autosize=True,
            # width=900,  # autosize or manual size
            height=200,
        )
    )
    next_graph_setting = dict(
        x=context.t,
        y=context.zero_to_hundred,
        name='sensor',
        mode='lines+markers+text',
        text=context.zero_to_hundred,
        textposition='top center',
        fill='tonexty',
        # color setting
        fillcolor='rgba({0},{1},{2},{3})'.format(
            int(x_axis >> 2),
            int(y_axis >> 2),
            int(z_axis >> 2),
             0.5),
        line=dict(color='rgba({0},{1},{2},{3})'.format(
            x_axis, y_axis, z_axis, 1.0)),
    )

    fig.append_trace(next_graph_setting, 1, 1)


'''
def plot_colorful_cercle(fig):
    x_axis,y_axis,z_axis = sensor.get_three_axis()
    # Create the cercle with subplots
    trace1 = go.Scatter(
        x=[0],
        y=[0],
        mode='markers',
        marker=dict(
            size=200,
            color='rgb({0},{1},{2},{3})'.format(
                int(x_axis>>2),
                int(y_axis>>2),
                int(z_axis>>2),
                0.5),
            colorscale='Viridis',
            line=dict(color='rgba({0},{1},{2},{3})'.format(
                int(x_axis>>2),
                int(y_axis>>2),
                int(z_axis>>2),
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
