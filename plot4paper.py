
"""
Python class to automate the generation of beautiful plots at
academic publication standard.
"""


import numpy as np
import sys

#matplotlib.use('Agg')
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
    
import configparser


# load the configuration containing the tex column- page- and line-widths
config = configparser.ConfigParser(
    allow_no_value=True
)
config.read( "config.ini" )

# list of all implemented templates
astronomy_journal = ['mnras', 'apj', 'aa', 'iau']
university_thesis = ['lmu']





###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
###                 CLASS FOR PUBLICATION QUALITY FIGURES                    ###
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###

class qualfig(object) :

    """Class to automate basic formatting of plots to ensure consistency.
    """

    def __init__(self,
                 ncols=1,
                 hf="gr",
                 wf=None,
                 key=None,
                 verbose=False) :

        """
        :param ncols: Number of columns the plot should span. Default: 1
        :param hf: The fractional height of the plot relative to the width. Default: Golden Ratio
        :param wf: The fractional width of the plot relative to full page width. Default: None
        :param key: The publication template name. Default: None
        :param verbose: Print general helper descriptions during plotting process. Default: False
        """
        
        permitted_keys = astronomy_journal + university_thesis
        self.__verbose = verbose
        
        # load the configuration for the plot type we are using...
        if key is not None:
            if key not in permitted_keys:
                raise KeyError("Selected key '"+"{}".format(key)+"' is not yet implemented...\n"+\
                               "Permitted keys are:\n{}".format(permitted_keys))
            else :
                plot_conf = config.__getitem__(key.upper())
                
        else :
            if self.__verbose : 
                print("Using the DEFAULT configuration...")
        
        
        # load the save file suffix
        self.__save_suffix = plot_conf.get( "savesuf" ) + ".pdf"
        
        
        # define the plot width
        if ncols == 1 :
            # plot should span one column
            self.__width = plot_conf.getfloat( "texcolumnwidth" )
            
        elif ncols == 2 :
            # plot should span both columns
            self.__width = plot_conf.getinfloat( "texlinewidth" )
            
        elif ncols is None:
            # plot should span a defined fraction of the full-page width
            if wf is not None :
                self.__width = plot_conf.getfloat( "texlinewidth" ) * wf
            else :
                raise ValueError("Please define the full-page width fraction you wish to use...")
        
        else :
            raise ValueError("Value of argument ncols, {}, is invalid".format(ncols))
            
            
        # define the plot height
        max_height = plot_conf.getfloat( "texheight" )
        if hf is None :
            # if height fraction isn't specified provide space for a caption
            self.__height = 0.80 * max_height
            
        elif hf=="gr" :
            # make the plot have golden ratio size
            golden_ratio = 2.0 / (1.0 + np.sqrt(5.0))
            self.__height = self.__width * golden_ratio
            
        else :
            # else we set the height as a fraction of the plot width
            self.__height = self.__width * hf

        if self.__height > max_height :
            raise ValueError("Figure height exceeds page height..."+\
                             "\n"+\
                             "Maximum possible value of hf is {:4.3f}".format(max_height/self.__width))
            
        
        # convert width and height to matplotlib inch units
        self.__inches_to_points = 72.27# define the conversion from inch to pt length measurements
        
        if self.__verbose :
            print("Figure size in inches: {w} x {h}".format(
                w=self.__width / self.__inches_to_points,
                h=self.__height / self.__inches_to_points
            ))

        
        # Plot border settings for nice publication worthy plots
        rcParams['figure.subplot.top'] = 0.95
        
        if ncols==1:
            rcParams['figure.subplot.bottom'] = 0.2
            rcParams['figure.subplot.left'] = 0.16
            rcParams['figure.subplot.right'] = 0.84

        elif ncols==2 :
            rcParams['figure.subplot.bottom'] = 0.1
            rcParams['figure.subplot.left'] = 0.08
            rcParams['figure.subplot.right'] = 0.92
            
        else :
            print("Using a fractional plot width will likely require manually setting the plot borders")
            rcParams['figure.subplot.bottom'] = 0.2
            rcParams['figure.subplot.left'] = 0.16
            rcParams['figure.subplot.right'] = 0.84

        

        rcParams['figure.figsize'] = (
            self.__width / self.__inches_to_points, 
            self.__height / self.__inches_to_points
        )
        
        # configure text and line widths
        font_size =  8
        linewidth = 0.5

        rcParams['font.size'] = font_size
        rcParams['axes.labelsize'] = font_size
        rcParams['axes.titlesize'] = font_size

        rcParams['xtick.major.width'] = linewidth-0.1
        rcParams['xtick.minor.width'] = linewidth-0.1
        rcParams['ytick.major.width'] = linewidth-0.1
        rcParams['ytick.minor.width'] = linewidth-0.1
        rcParams["lines.linewidth"] = linewidth 
        rcParams["grid.linewidth"]  = linewidth 

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

        self.__dpi=1000

        
    def is_colorbar_axis(self,AXIS) :
        """Function to tell script an axis is a colourbar axis. 
        Reconfigures the tick settings.
        
        """

        AXIS.minorticks_off()
        AXIS.tick_params(which="major",direction="out")


    def set_label_spaces(self,side=None,bottom=None,top=None,left=None,right=None):
        """Function to customise the plot whitespace borders 
        
        """
        
        # check for conflicting instructions
        side_is_not_None = side is not None
        left_is_not_None = left is not None
        right_is_not_None = right is not None
        
        if side_is_not_None and ( left_is_not_None or right_is_not_None ) :
            print("WARNING: Defaulting to the setting for --side--")

        if side_is_not_None  :
            rcParams['figure.subplot.left'] = side
            rcParams['figure.subplot.right'] = 1-side
            
        else: 

            if left_is_not_None :
                rcParams['figure.subplot.left'] = left

            if right_is_not_None :
                rcParams['figure.subplot.right'] = 1-right

        if bottom is not None :
            rcParams['figure.subplot.bottom'] = bottom

        if top is not None :
            rcParams['figure.subplot.top'] = 1.-top


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
        print(bbox)
        os.system("pdfcrop %s %s --bbox \" %.6f %.6f %.6f %.6f \" " % (name, fname,0, bbox[1], self.__width, bbox[3]))
        command = 'rm %s'%(name)
        os.system(command)

    def save(self, fname, extension="pdf", dpi=None ):

        if dpi is None :
            dpi=self.__dpi
                  
        # strip the .pdf extension if it is there
        if fname[-4:] == ".pdf":
            fname = fname[:-4]
                  
        # now construct the save name we will use...
        savename = fname+self.__save_suffix
                  
        # initially crop the figure
        self._crop_figure(savename,dpi=dpi)
                  
        if extension=="eps":
            # now convert to eps
            command = 'pdftops -eps %s'%(savename)
            os.system(command)
            command = 'rm %s'%(savename)
            os.system(command)
