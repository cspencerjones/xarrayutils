import matplotlib as mpl
mpl.use('Agg')
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from xmitgcm import open_mdsdataset
# import argparse
# from dask.diagnostics import ProgressBar
# from dask.array import from_array

def mitgcm_Movie(ddir,
                prefix=['tracer_snapshots'],
                maskname='hFacC',
                varname='TRAC01',
                clim =[-5,40]):
    ds   = open_mdsdataset(ddir,prefix=prefix,
                            swap_dims=False)
    ds   = ds[varname].where(ds[maskname]==1)
    odir = ddir+'/movie'
    Movie(ds,odir,clim=clim)

def Movie(da,odir,
            varname     = None,
            framedim    = 'time',
            moviename   = 'movie',
            plotstyle   = 'simple',
            clim        = None,
            cmap        = None,
            bgcolor     = np.array([1,1,1])*0.9,
            framewidth  = 1280,
            frameheight = 720,
            dpi         = 100
            ):
    # Set defaults:

    if not isinstance(da,xr.DataArray):
        raise RuntimeError('input has to be an xarray DataStructure, instead\
        is '+str(type(da)))

    if not os.path.exists(odir):
        os.makedirs(odir)

    # Infer defaults from data
    if not clim:
        print('clim will be inferred from data, this can take very long...')
        clim = [da.min(),da.max()]
    if not cmap:
        cmap = plt.cm.RdYlBu_r

    # Annnd here we go
    print('+++ Execute plot function +++')
    # do it with a simple for loop...can this really be quicker?
    for ii in range(0,len(da.time)):
        start_time = time.time()
        da_slice = da[{framedim:ii}]
        fig,ax,h = FramePrint(da_slice,
                                frame       = ii,
                                odir        = odir,
                                cmap        = cmap,
                                clim        = clim,
                                framewidth  = framewidth,
                                frameheight = frameheight,
                                dpi         = dpi
                                )
        if ii % 100 == 0:
            remaining_time = (len(da.time)-ii)/(time.time() - start_time)/60
            print('FRAME---%04d---' %ii)
            print('Estimated time left : %d minutes' %remaining_time)



    print('+++ Convert frames to video +++')
    query = 'ffmpeg -y -i "frame_%05d.png" -c:v libx264 -preset veryslow \
        -crf 2 -pix_fmt yuv420p \
        -framerate 15 \
        "'+moviename+'.mov"'

    with cd(odir):
        os.system(query)
        os.system('rm *.png')

def FramePrint(da,odir=None,
                    frame=0,
                    cmap=None,
                    clim = None,
                    bgcolor = np.array([1,1,1])*0.3,
                    facecolor = np.array([1,1,1])*0.3,
                    framewidth  = 1280,
                    frameheight = 720,
                    dpi         = 100
                    ):
    """Prints the plotted picture to file


    """

    if not odir:
        raise RuntimeError('need an output directory')

    fig = MovieFrame(framewidth,frameheight,dpi)
    # TODO plotsyle options
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.set_facecolor(facecolor)
    ax.set_aspect(1, anchor = 'C')
    fig.add_axes(ax)
    h = SimplePlot(da.data,ax,
                    cmap=cmap,
                    clim=clim,
                    bgcolor=bgcolor)
    #
    fig.savefig(odir+'/frame_%05d.png' %frame, dpi=fig.dpi)
    plt.close('all')
    return fig,ax,h

def SimplePlot(data,ax,cmap = None,
                        clim = None,
                        bgcolor = np.array([1,1,1])*0.3):
    if not cmap:
        cmap = plt.cm.Blues
    if not clim:
        print('clim not defined. Will be deduced from data. \
        This could have undesired effects for videos')
        clim = [data.min(),data.max()]

    cmap.set_bad(bgcolor, 1)
    pixels = np.squeeze(np.ma.array(data, mask=np.isnan(data)))
    h = ax.imshow(pixels,cmap=cmap,clim=clim,aspect='auto')
    ax.invert_yaxis()
    return h

def MovieFrame(framewidth,frameheight,dpi):
    fig = plt.figure(frameon=False)
    fig.set_size_inches(framewidth/dpi,
                        frameheight/dpi)
    return fig

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='xarray Movie script')
#
#     parser.add_argument('ddir',help='input array')
#
#     parser.add_argument('-odir','--outdir',
#         help='output directory',default=None)
#     parser.add_argument('-v','--varname',
#         help='diagnostic name',default='TRAC01')
#     parser.add_argument('-cl','--clim',
#         help='color limit',default=None)
#     parser.add_argument('-di','--framedim',
#         help='video time dim',default='time')
#     parser.add_argument('-n','--moviename',
#         help='output filename',default='movie')
#     parser.add_argument('-st','--plotstyle',
#         help='plotting style',default='simple_fullscreen')
#
#     args = parser.parse_args()
#
#     # ## show values ##
#     # print ("Grid Directory: %s" % args.grid_dir)
#     # print ("Delayed Time Directory: %s" % args.dt_dir)
#     # print ("Near Real Time Directory: %s" % args.nrt_dir)
#     # print ("Output Directory: %s" % args.out_dir)
#     # print ("Delayed Time Name: %s" % args.fid_dt)
#     # print ("Real Time Name: %s" % args.fid_nrt)
#     # print ("--- ---")
