
"""
This file is a python setup to generate beautiful plots at
publication standard

written: J P Clarke
"""

"""
import utils.plot4paper as p4p
"""

#matplotlib.use('Agg')

import numpy as np
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from cycler import cycler

import os
import re

try:
    import commands   as comsub
except:
    import subprocess as comsub


def colors(key=None) :

    colors = [[.2, .2, .5], [0., .4, 1.], [0., .8, 1.],[1., .8, 0.], [1., .4, 0.], [1.,0.,0.]][::-1]

    if isinstance( key , type(None) )==True :
        return colors

    #define set of nice colors
    keys = ["r","o","y","lb","b","db"]
    if key not in keys:
        raise ValueError( "Key not recognised. Acceptable values are ","r ","o ","y ","lb ","b ","db " )

    return colors[ key==keys ]


def setFigSize( height, width, verbose) :
    w = width  / 72.27
    h = height / 72.27
    if verbose :
        print("Figure size in inches: ", [w,h])
    return (w,h)

def getPageSetups(key) :
    """
    This could all be moved to a config file along with the save appendix label
    """
    if key=="mnras" :
        texcolumnwidth = 240.
        texlinewidth   = 504.0
        texheight      = 682.
    elif key=="AA" :
        texcolumnwidth = 256.0748
        texlinewidth   = 523.5307
        texheight      = 705.0
    elif key=="apj" :
        texcolumnwidth = 245.26653
        texlinewidth   = 513.11743
        texheight      = 675.83984
    elif key=="iau" :
        texcolumnwidth = 384.0
        texlinewidth   = 384.0
        texheight      = 595.5
    elif key=="lmu" :
        texcolumnwidth = 460.72124
        texlinewidth   = texcolumnwidth
        texheight      = 621.0

    else :
        raise ValueError("Key not recognised. Options are ['mnras','AA','apj','iau','lmu']")
    return [texcolumnwidth,texlinewidth,texheight]




###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
###                 CLASS FOR PUBLICATION QUALITY FIGURES                    ###
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###

class qualfig(object) :

    """
    import utils.plot4paper as p4p
    qualfig = p4p.qualfig()
    """

    def __init__(self,key=None,ncols=1,heightFrac="gr",verbose=False) :

        """
        initialisation function
        key - the journal for which the figure is being produced
        ncols -  the number of columns for the figure to span
        heightFrac - the fraction of the page the figure should occupy
        verbose - print various messages at run time
        """

        # now get the savename...
        if key is None :
            key="mnras"
            self.saveapp=".pdf"
        elif key=="mnras" :
            self.saveapp="_ForMNRAS.pdf"
        elif key=="lmu" :
            self.saveapp="_ForThesis.pdf"
        else :
            self.saveapp=".pdf"

        self._verbose=verbose

        #Get the
        [texcolumnwidth,texlinewidth,texheight] = getPageSetups(key)

        #Settings for nice plots in mnras publications
        font_size =  8
        linewidth = 0.5
        self.__lw = linewidth
        rcParams['figure.subplot.top'] = 0.95
        if ncols==1:
            self.width = texcolumnwidth

            rcParams['figure.subplot.bottom'] = 0.2
            rcParams['figure.subplot.left'] = 0.16
            rcParams['figure.subplot.right'] = 0.84

        elif ncols==2 :
            self.width = texlinewidth

            rcParams['figure.subplot.bottom'] = 0.1
            rcParams['figure.subplot.left'] = 0.08
            rcParams['figure.subplot.right'] = 0.92

        elif ncols==1./3. :
            self.width = texlinewidth/3.

            rcParams['figure.subplot.bottom'] = 0.2
            rcParams['figure.subplot.left'] = 0.16
            rcParams['figure.subplot.right'] = 0.84

        else :
            raise ValueError("Don't understand the input number of columns...")

        if isinstance( heightFrac , type(None) )==True :
            figheight = 0.85*texheight # we will of course require some space for the caption
        elif heightFrac=="gr" :
            # make the plot have golden ratio size
            figheight = self.width * 2./(1.+np.sqrt(5.)) / (1.-rcParams['figure.subplot.bottom'])
        else :
            figheight = self.width * heightFrac

        if figheight>texheight :
            raise ValueError("Figure height exceeds page height...\nMaximum heightFrac value is {:4.3f}".format(texheight/self.width))

        rcParams['figure.figsize'] = setFigSize(height=figheight,width=self.width,verbose=self._verbose)


        rcParams['font.size'] = font_size
        rcParams['axes.labelsize'] = font_size
        rcParams['axes.titlesize'] = font_size

        rcParams['xtick.major.width'] = linewidth-0.1
        rcParams['xtick.minor.width'] = linewidth-0.1
        rcParams['ytick.major.width'] = linewidth-0.1
        rcParams['ytick.minor.width'] = linewidth-0.1
        rcParams["lines.linewidth"] = linewidth # thickness of contour plots ets
        rcParams["grid.linewidth"]  = linewidth # thickness of contour plots ets

        rcParams['xtick.minor.visible'] = True
        rcParams['ytick.minor.visible'] = True

        rcParams["xtick.bottom"]=True
        rcParams["xtick.top"]=True

        rcParams["ytick.left"]=True
        rcParams["ytick.right"]=True

        rcParams["xtick.direction"]="in"
        rcParams["ytick.direction"]="in"

        rcParams["errorbar.capsize"] = 4

        rcParams['legend.fontsize'] = font_size
        rcParams['legend.framealpha'] = 0.
        rcParams['legend.edgecolor'] = "w"

        rcParams['xtick.labelsize'] = font_size - 1
        rcParams['ytick.labelsize'] = font_size - 1

        rcParams['font.family'] = 'sans-serif'   # default
        rcParams['text.usetex'] = True
        plt.rc('text.latex', preamble=r'\usepackage{underscore}')

        rcParams['contour.negative_linestyle'] = 'solid'

        # determine the new cycling order
        rcParams['axes.prop_cycle'] = cycler(color='brckmgy')

        self.dpi=1000

    def is_colorbar_axis(self,AXIS) :

        AXIS.minorticks_off()
        AXIS.tick_params(which="major",direction="out")



    @property
    def linewidth(self) :
        return self.__lw

    def set_label_spaces(self,side=None,bottom=None,top=None,left=None,right=None):
        if (isinstance( side , type(None) )==False) & ( (isinstance( left , type(None) )==False) | (isinstance( right , type(None) )==False) ) :
            raise ValueError("side and left/right are simultaneously defined...")

        if isinstance( side , type(None) )==False :
            rcParams['figure.subplot.left'] = side
            rcParams['figure.subplot.right'] = 1-side

        if (isinstance( left , type(None) )==False) :
            rcParams['figure.subplot.left'] = left

        if (isinstance( right , type(None) )==False) :
            rcParams['figure.subplot.right'] = 1-right

        if isinstance( bottom , type(None) )==False :
            rcParams['figure.subplot.bottom'] = bottom

        if isinstance( top , type(None) )==False :
            rcParams['figure.subplot.top'] = 1.-top

    def printLabelSpaces(self):
        print("side : ", rcParams['figure.subplot.left'])
        print("bottom : ", rcParams['figure.subplot.bottom'])
        print("top : ", rcParams['figure.subplot.top'])

    def _crop_figure(self,fname,dpi) :
        """
        function to crop figures correctly
        work initially in pdf format but can then convert to other file formats
        """
        name = 'dum.pdf'
        plt.savefig(name,dpi=dpi)
        command = 'gs -sDEVICE=bbox -dNOPAUSE -dBATCH %s'%name
        r = comsub.getoutput(command).split()
        bbox = [float(a) for a in r[-4:]]
        os.system("pdfcrop %s %s --bbox \" %.6f %.6f %.6f %.6f \" " % (name, fname,0, bbox[1], self.width, bbox[3]))
        command = 'rm %s'%(name)
        os.system(command)

    def save(self, fname, extension="pdf", dpi=None ):

        if dpi is None :
            dpi=self.dpi
        # strip the extension if it is there
        if fname[-4:] ==".pdf":
            fname = fname[:-4]
        # now construct the save name we will use...
        savename = fname+self.saveapp
        # initially crop the figure
        self._crop_figure(savename,dpi=dpi)
        if extension=="pdf":
            return
        elif extension=="eps":
            # now convert to eps
            command = 'pdftops -eps %s'%(savename)
            os.system(command)
            command = 'rm %s'%(savename)
            os.system(command)
            return
        else :
            return
