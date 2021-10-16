import vedo
from vedo.addons import addScalarBar
from vedo.plotter import Plotter
from vedo.pyplot import cornerHistogram
from vedo.utils import mag, precision, linInterpolate, isSequence
from vedo.colors import printc, colorMap, getColor
from vedo.shapes import Text2D, Line, Ribbon, Spline
from vedo.pointcloud import Points, fitPlane
from vedo import settings
import numpy as np
import os


def IsosurfaceBrowserCustom(volume, c=None, alpha=1, lego=False, cmap='hot', pos=None,
                      delayed=False, qtWidget = None):
    """
    Generate a ``Plotter`` window for Volume isosurfacing using a slider.
    Returns the ``Plotter`` object.

    Set delayed=True to delay slider update on mouse release.

    :Example:
        .. code-block:: python

            from vedo import dataurl, Volume
            from vedo.applications import IsosurfaceBrowser
            vol = Volume(dataurl+'head.vti')
            plt = IsosurfaceBrowser(vol, c='gold')
            plt.show(axes=7, bg2='lb')
    """
    vp = settings.plotter_instance
    if not vp:
        vp = Plotter(axes=4, bg='w', title="Isosurface Browser", qtWidget=qtWidget)

    scrange = volume.scalarRange()
    threshold = (scrange[1] - scrange[0]) / 3.0 + scrange[0]

    if lego:
        sliderpos = ((0.79, 0.035), (0.975, 0.035))
        slidertitle = ""
        showval = False
        mesh = volume.legosurface(vmin=threshold, cmap=cmap).alpha(alpha)
        mesh.addScalarBar(horizontal=True)
    else:
        sliderpos = 4
        slidertitle = "threshold"
        showval = True
        mesh = volume.isosurface(threshold)
        mesh.color(c).alpha(alpha)

    if pos is not None:
        sliderpos = pos

    vp.actors = [mesh] + vp.actors

    ############################## threshold slider
    bacts = dict()
    def sliderThres(widget, event):

        prevact = vp.actors[0]
        wval =  widget.GetRepresentation().GetValue()
        wval_2 = precision(wval, 2)
        if wval_2 in bacts.keys():  # reusing the already available mesh
            mesh = bacts[wval_2]
        else:                       # else generate it
            if lego:
                mesh = volume.legosurface(vmin=wval, cmap=cmap)
            else:
                mesh = volume.isosurface(threshold=wval).color(c).alpha(alpha)
            bacts.update({wval_2: mesh}) # store it

        vp.renderer.RemoveActor(prevact)
        vp.renderer.AddActor(mesh)
        vp.actors[0] = mesh

    dr = scrange[1] - scrange[0]
    vp.addSlider2D( sliderThres,
                    scrange[0] + 0.02 * dr,
                    scrange[1] - 0.02 * dr,
                    value=threshold,
                    pos=sliderpos,
                    title=slidertitle,
                    showValue=showval,
                    delayed=delayed,
                    )
    return vp

def SlicerPlotterCustom(
           volume,
           alpha=1,
           cmaps=('gist_ncar_r', "hot_r", "bone_r", "jet", "Spectral_r"),
           map2cells=False,  # buggy
           clamp=True,
           useSlider3D=False,
           size=(1200,1000),
           screensize="auto",
           title="",
           bg="white",
           bg2="lightblue",
           axes=7,
           showHisto=True,
           showIcon=True,
           draggable=False,
           verbose=True,
           qtWidget = None
           ):
    """
    Generate a ``Plotter`` window with slicing planes for the input Volume.
    Returns the ``Plotter`` object.

    :param float alpha: transparency of the slicing planes
    :param list cmaps: list of color maps names to cycle when clicking button
    :param bool map2cells: scalars are mapped to cells, not intepolated.
    :param bool clamp: clamp scalar to reduce the effect of tails in color mapping
    :param bool useSlider3D: show sliders attached along the axes
    :param list size: rendering window size in pixels
    :param list screensize: size of the screen can be specified
    :param str title: window title
    :param bg: background color
    :param bg2: background gradient color
    :param int axes: axis type number
    :param bool showHisto: show histogram on bottom left
    :param bool showIcon: show a small 3D rendering icon of the volume
    :param bool draggable: make the icon draggable
    """
    global _cmap_slicer

    # if verbose: printc("Slicer tool", invert=1, c="m")
    ################################
    vp = Plotter(bg=bg, bg2=bg2,
                 size=size,
                 screensize=screensize,
                 title=title,
                 interactive=False,
                 qtWidget=qtWidget
                )

    ################################
    box = volume.box().wireframe().alpha(0)

    vp.show(box, viewup="z", axes=axes)
    if showIcon:
        vp.addInset(volume, pos=(.85,.85), size=0.15, c='w', draggable=draggable)

    # inits
    la, ld = 0.7, 0.3 #ambient, diffuse
    dims = volume.dimensions()
    data = volume.pointdata[0]
    rmin, rmax = volume.imagedata().GetScalarRange()
    if clamp:
        hdata, edg = np.histogram(data, bins=50)
        logdata = np.log(hdata+1)
        # mean  of the logscale plot
        meanlog = np.sum(np.multiply(edg[:-1], logdata))/np.sum(logdata)
        rmax = min(rmax, meanlog+(meanlog-rmin)*0.9)
        rmin = max(rmin, meanlog-(rmax-meanlog)*0.9)
        if verbose:
            printc('scalar range clamped to range: (' +
                    precision(rmin, 3) +', '+  precision(rmax, 3)+')', c='m', bold=0)
    _cmap_slicer = cmaps[0]
    visibles = [None, None, None]
    msh = volume.zSlice(int(dims[2]/2))
    msh.alpha(alpha).lighting('', la, ld, 0)
    msh.cmap(_cmap_slicer, vmin=rmin, vmax=rmax)
    if map2cells: msh.mapPointsToCells()
    vp.renderer.AddActor(msh)
    visibles[2] = msh
    addScalarBar(msh, pos=(0.04,0.0), horizontal=True, titleFontSize=0)

    def sliderfunc_x(widget, event):
        i = int(widget.GetRepresentation().GetValue())
        msh = volume.xSlice(i).alpha(alpha).lighting('', la, ld, 0)
        msh.cmap(_cmap_slicer, vmin=rmin, vmax=rmax)
        if map2cells: msh.mapPointsToCells()
        vp.renderer.RemoveActor(visibles[0])
        if i and i<dims[0]: vp.renderer.AddActor(msh)
        visibles[0] = msh

    def sliderfunc_y(widget, event):
        i = int(widget.GetRepresentation().GetValue())
        msh = volume.ySlice(i).alpha(alpha).lighting('', la, ld, 0)
        msh.cmap(_cmap_slicer, vmin=rmin, vmax=rmax)
        if map2cells: msh.mapPointsToCells()
        vp.renderer.RemoveActor(visibles[1])
        if i and i<dims[1]: vp.renderer.AddActor(msh)
        visibles[1] = msh

    def sliderfunc_z(widget, event):
        i = int(widget.GetRepresentation().GetValue())
        msh = volume.zSlice(i).alpha(alpha).lighting('', la, ld, 0)
        msh.cmap(_cmap_slicer, vmin=rmin, vmax=rmax)
        if map2cells: msh.mapPointsToCells()
        vp.renderer.RemoveActor(visibles[2])
        if i and i<dims[2]: vp.renderer.AddActor(msh)
        visibles[2] = msh

    cx, cy, cz, ch = 'dr', 'dg', 'db', (0.3,0.3,0.3)
    if np.sum(vp.renderer.GetBackground()) < 1.5:
        cx, cy, cz = 'lr', 'lg', 'lb'
        ch = (0.8,0.8,0.8)

    if not useSlider3D:
        vp.addSlider2D(sliderfunc_x, 0, dims[0], title='X', titleSize=0.5,
                       pos=[(0.8,0.12), (0.95,0.12)], showValue=False, c=cx)
        vp.addSlider2D(sliderfunc_y, 0, dims[1], title='Y', titleSize=0.5,
                       pos=[(0.8,0.08), (0.95,0.08)], showValue=False, c=cy)
        vp.addSlider2D(sliderfunc_z, 0, dims[2], title='Z', titleSize=0.6,
                       value=int(dims[2]/2),
                       pos=[(0.8,0.04), (0.95,0.04)], showValue=False, c=cz)
    else: # 3d sliders attached to the axes bounds
        bs = box.bounds()
        vp.addSlider3D(sliderfunc_x,
            pos1=(bs[0], bs[2], bs[4]),
            pos2=(bs[1], bs[2], bs[4]),
            xmin=0, xmax=dims[0],
            t=box.diagonalSize()/mag(box.xbounds())*0.6,
            c=cx,
            showValue=False,
        )
        vp.addSlider3D(sliderfunc_y,
            pos1=(bs[1], bs[2], bs[4]),
            pos2=(bs[1], bs[3], bs[4]),
            xmin=0, xmax=dims[1],
            t=box.diagonalSize()/mag(box.ybounds())*0.6,
            c=cy,
            showValue=False,
        )
        vp.addSlider3D(sliderfunc_z,
            pos1=(bs[0], bs[2], bs[4]),
            pos2=(bs[0], bs[2], bs[5]),
            xmin=0, xmax=dims[2],
            value=int(dims[2]/2),
            t=box.diagonalSize()/mag(box.zbounds())*0.6,
            c=cz,
            showValue=False,
        )


    #################
    def buttonfunc():
        global _cmap_slicer
        bu.switch()
        _cmap_slicer = bu.status()
        for mesh in visibles:
            if mesh:
                mesh.cmap(_cmap_slicer, vmin=rmin, vmax=rmax)
                if map2cells:
                    mesh.mapPointsToCells()
        vp.renderer.RemoveActor(mesh.scalarbar)
        mesh.scalarbar = addScalarBar(mesh,
                                      pos=(0.04,0.0),
                                      horizontal=True,
                                      titleFontSize=0)
        vp.renderer.AddActor(mesh.scalarbar)

    bu = vp.addButton(buttonfunc,
        pos=(0.27, 0.005),
        states=cmaps,
        c=["db"]*len(cmaps),
        bc=["lb"]*len(cmaps),  # colors of states
        size=14,
        bold=True,
    )

    #################
    hist = None
    if showHisto:
        hist = cornerHistogram(data, s=0.2,
                               bins=25, logscale=1, pos=(0.02, 0.02),
                               c=ch, bg=ch, alpha=0.7)

    comment = None
    if verbose:
        comment = Text2D("Use sliders to slice volume\nClick button to change colormap",
                         font='', s=0.8)

    vp.show(msh, hist, comment, interactive=False)
    vp.interactive = True
    return vp