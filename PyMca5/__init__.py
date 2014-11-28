#/*##########################################################################
# Copyright (C) 2004-2014 V.A. Sole, European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
__author__ = "V.A. Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
import os
import sys
__version__ = "5.0.0~rc7"

def version():
    return __version__

if os.path.exists(os.path.join(\
    os.path.dirname(os.path.dirname(__file__)), 'py2app_setup.py')):
    raise ImportError('PyMca cannot be imported from source directory')

# workaround matplotlib MPLCONFIGDIR issues under windows
if sys.platform.startswith("win"):
    try:
        #try to avoid matplotlib config dir problem under windows
        if os.getenv("MPLCONFIGDIR") is None:
            import ctypes
            from ctypes.wintypes import MAX_PATH
            # recipe based on: http://bugs.python.org/issue1763#msg62242
            dll = ctypes.windll.shell32
            buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
            if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
                directory = buf.value
            else:
                # the above should have worked
                home = os.getenv('USERPROFILE')
                try:
                    l = len(home)
                    directory = os.path.join(home, "My Documents")
                except:
                    home = '\\'
                    directory = '\\'
            if os.path.isdir('%s' % directory):
                directory = os.path.join(directory, "PyMca")
            else:
                directory = os.path.join(home, "PyMca")
            if not os.path.exists('%s' % directory):
                os.mkdir('%s' % directory)
            os.environ[ 'MPLCONFIGDIR' ] = directory
    except:
        print("WARNING: Could not set MPLCONFIGDIR.", sys.exc_info()[1])

# mandatory modules for compatibility
from .PyMcaCore import Plugin1DBase, StackPluginBase, PyMcaDirs, DataObject

#convenience modules that could be directly imported
# using from PyMca5.PyMca import
try:
    from .PyMcaIO import specfilewrapper, EdfFile, specfile, ConfigDict
except:
    print("WARNING importing IO directly")
    from PyMcaIO import specfilewrapper, EdfFile, specfile, ConfigDict

from .PyMcaMath.fitting import SpecfitFuns, Gefit, Specfit
from .PyMcaMath.fitting import SpecfitFunctions

from .PyMcaPhysics.xrf import Elements

#all the rest can be imported using from PyMca5.PyMca import ...
from . import PyMca
