import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event
import numpy as np
import os
import plotly
from plyfile import PlyData, PlyElement

# my module
import ply3d.ply_trisurf as trisurf


def viewer(fig, rgb_val, filename, plyfile_dict):
    # Plotly 公式ページのコピー始まり
    # https://plot.ly/matplotlib/trisurf/
    plydata = PlyData.read(plyfile_dict[filename])  # Ply file open
    nr_points = plydata.elements[0].count
    nr_faces = plydata.elements[1].count
    points = np.array([plydata['vertex'][k]
                       for k in range(nr_points)])
    x, y, z = zip(*points)
    faces = [plydata['face'][k][0] for k in range(nr_faces)]
    data3 = trisurf.plotly_trisurf(
        x, y, z, faces, colormap=trisurf.cm.RdBu, plot_edges=None)
    # 終わり

    # Setting(Axis, Plot area)
    # 枠線、罫線なし
    noaxis = dict(
        showbackground=False,
        showline=False,
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title=''
    )

    x_cam = rgb_val[0]/150.0
    y_cam = rgb_val[1]/150.0
    z_cam = rgb_val[2]/150.0

    if -1.0 < x_cam and x_cam < 1.0:
        x_cam = 1.0
    if -1.0 < y_cam and y_cam < 1.0:
        y_cam = -1.0
    if -1.0 < z_cam and z_cam < 1.0:
        z_cam = 1.0

    fig['layout'].update(
        dict(
            autosize=True,
            # width=900,  # autosize or manual size
            height=550,
            scene=dict(
                xaxis=noaxis,
                yaxis=noaxis,
                zaxis=noaxis,
                aspectratio=dict(x=1.6, y=1.6, z=0.8),  # Front position
                camera=dict(
                    eye=dict(
                        x=x_cam,  # 1.25 -> x_cam
                        y=y_cam,  # 1.25 -> y_cam
                        z=z_cam,  # 1.25 -> z_cam
                    )
                )
            )
        )
    )

    fig['layout']['margin'] = {'l': 0, 'r': 0, 'b': 20, 't': 32}

    # Subplot descript
    fig.append_trace(data3[0], 1, 1)
