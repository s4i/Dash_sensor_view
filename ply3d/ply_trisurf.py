from functools import reduce
import matplotlib.cm as cm
import numpy as np
import os
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# https://plot.ly/matplotlib/trisurf/
# Plotly 公式ページのコピー


def map_z2color(zval, colormap, vmin, vmax):
    # map the normalized value zval to a corresponding color in the colormap
    if vmin > vmax:
        raise ValueError('incorrect relation between vmin and vmax')
    t = (zval-vmin)/float((vmax-vmin))  # normalize val
    R, G, B, alpha = colormap(t)  # need alpha.
    return 'rgb('+'{:d}'.format(int(R*255+0.5)) + ',' \
        + '{:d}'.format(int(G*255+0.5)) + ',' \
        + '{:d}'.format(int(B*255+0.5))+')'


# Plotly 公式ページのコピー
def tri_indices(simplices):
    # simplices is a numpy array defining
    # the simplices of the triangularization
    # returns the lists of indices i, j, k
    return ([triplet[c] for triplet in simplices] for c in range(3))


# Plotly 公式ページのコピー
def plotly_trisurf(x, y, z, simplices, colormap=cm.RdBu, plot_edges=None):
    # x, y, z are lists of coordinates of the triangle vertices
    # simplices are the simplices that define the triangularization;
    # simplices  is a numpy array of shape (no_triangles, 3)
    # insert here the  type check for input data

    points3D = np.vstack((x, y, z)).T
    # vertices of the surface triangles
    tri_vertices = map(lambda index: points3D[index], simplices)
    # mean values of z-coordinates of
    zmean = [np.mean(tri[:, 2]) for tri in tri_vertices]
    # triangle vertices
    min_zmean = np.min(zmean)
    max_zmean = np.max(zmean)
    facecolor = [map_z2color(zz,  colormap, min_zmean, max_zmean)
                 for zz in zmean]
    I, J, K = tri_indices(simplices)

    triangles = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        facecolor=facecolor,
        i=I,
        j=J,
        k=K,
        name=''
    )

    if plot_edges is None:  # the triangle sides are not plotted
        return [triangles]
    else:
        # define the lists Xe, Ye, Ze, of x, y, resp z coordinates of edge end points for each triangle
        # None separates data corresponding to two consecutive triangles
        lists_coord = [[[T[k % 3][c] for k in range(4)]+[None]
                        for T in tri_vertices] for c in range(3)]
        Xe, Ye, Ze = [reduce(lambda x, y: x+y, lists_coord[k])
                      for k in range(3)]

        # define the lines to be plotted
        lines = go.Scatter3d(
            x=Xe,
            y=Ye,
            z=Ze,
            mode='lines',
            line=dict(color='rgb(50, 50, 50)', width=1.5)
        )
        return [triangles, lines]
