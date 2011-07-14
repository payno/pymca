import sys
import os
import traceback
import Plot1DQwt
qt = Plot1DQwt.qt
from PyMca_Icons import IconDict
QTVERSION = qt.qVersion()
DEBUG = 0

class Plot1DWindow(Plot1DQwt.Plot1DQwt):
    def __init__(self, parent=None, **kw):
        Plot1DQwt.Plot1DQwt.__init__(self, **kw)
        self._toggleCounter = 0
        self._initIcons()
        self._buildToolBar()

    def _initIcons(self):
        if QTVERSION < '4.0.0':
            self.normalIcon	= qt.QIconSet(qt.QPixmap(IconDict["normal"]))
            self.zoomIcon	= qt.QIconSet(qt.QPixmap(IconDict["zoom"]))
            self.roiIcon	= qt.QIconSet(qt.QPixmap(IconDict["roi"]))
            self.peakIcon	= qt.QIconSet(qt.QPixmap(IconDict["peak"]))

            self.zoomResetIcon	= qt.QIconSet(qt.QPixmap(IconDict["zoomreset"]))
            self.roiResetIcon	= qt.QIconSet(qt.QPixmap(IconDict["roireset"]))
            self.peakResetIcon	= qt.QIconSet(qt.QPixmap(IconDict["peakreset"]))
            self.refreshIcon	= qt.QIconSet(qt.QPixmap(IconDict["reload"]))

            self.logxIcon	= qt.QIconSet(qt.QPixmap(IconDict["logx"]))
            self.logyIcon	= qt.QIconSet(qt.QPixmap(IconDict["logy"]))
            self.xAutoIcon	= qt.QIconSet(qt.QPixmap(IconDict["xauto"]))
            self.yAutoIcon	= qt.QIconSet(qt.QPixmap(IconDict["yauto"]))
            self.togglePointsIcon = qt.QIconSet(qt.QPixmap(IconDict["togglepoints"]))
            self.fitIcon	= qt.QIconSet(qt.QPixmap(IconDict["fit"]))
            self.searchIcon	= qt.QIconSet(qt.QPixmap(IconDict["peaksearch"]))

            self.averageIcon	= qt.QIconSet(qt.QPixmap(IconDict["average16"]))
            self.deriveIcon	= qt.QIconSet(qt.QPixmap(IconDict["derive"]))
            self.smoothIcon     = qt.QIconSet(qt.QPixmap(IconDict["smooth"]))
            self.swapSignIcon	= qt.QIconSet(qt.QPixmap(IconDict["swapsign"]))
            self.yMinToZeroIcon	= qt.QIconSet(qt.QPixmap(IconDict["ymintozero"]))
            self.subtractIcon	= qt.QIconSet(qt.QPixmap(IconDict["subtract"]))
            self.printIcon	= qt.QIconSet(qt.QPixmap(IconDict["fileprint"]))
            self.saveIcon	= qt.QIconSet(qt.QPixmap(IconDict["filesave"]))
        else:
            self.normalIcon	= qt.QIcon(qt.QPixmap(IconDict["normal"]))
            self.zoomIcon	= qt.QIcon(qt.QPixmap(IconDict["zoom"]))
            self.roiIcon	= qt.QIcon(qt.QPixmap(IconDict["roi"]))
            self.peakIcon	= qt.QIcon(qt.QPixmap(IconDict["peak"]))

            self.zoomResetIcon	= qt.QIcon(qt.QPixmap(IconDict["zoomreset"]))
            self.roiResetIcon	= qt.QIcon(qt.QPixmap(IconDict["roireset"]))
            self.peakResetIcon	= qt.QIcon(qt.QPixmap(IconDict["peakreset"]))
            self.refreshIcon	= qt.QIcon(qt.QPixmap(IconDict["reload"]))

            self.logxIcon	= qt.QIcon(qt.QPixmap(IconDict["logx"]))
            self.logyIcon	= qt.QIcon(qt.QPixmap(IconDict["logy"]))
            self.xAutoIcon	= qt.QIcon(qt.QPixmap(IconDict["xauto"]))
            self.yAutoIcon	= qt.QIcon(qt.QPixmap(IconDict["yauto"]))
            self.togglePointsIcon = qt.QIcon(qt.QPixmap(IconDict["togglepoints"]))

            self.fitIcon	= qt.QIcon(qt.QPixmap(IconDict["fit"]))
            self.searchIcon	= qt.QIcon(qt.QPixmap(IconDict["peaksearch"]))

            self.averageIcon	= qt.QIcon(qt.QPixmap(IconDict["average16"]))
            self.deriveIcon	= qt.QIcon(qt.QPixmap(IconDict["derive"]))
            self.smoothIcon     = qt.QIcon(qt.QPixmap(IconDict["smooth"]))
            self.swapSignIcon	= qt.QIcon(qt.QPixmap(IconDict["swapsign"]))
            self.yMinToZeroIcon	= qt.QIcon(qt.QPixmap(IconDict["ymintozero"]))
            self.subtractIcon	= qt.QIcon(qt.QPixmap(IconDict["subtract"]))
            
            self.printIcon	= qt.QIcon(qt.QPixmap(IconDict["fileprint"]))
            self.saveIcon	= qt.QIcon(qt.QPixmap(IconDict["filesave"]))            

            self.pluginIcon     = qt.QIcon(qt.QPixmap(IconDict["plugin"])) 

    def _buildToolBar(self):
        self.toolBar = qt.QWidget(self)
        self.toolBarLayout = qt.QHBoxLayout(self.toolBar)
        self.toolBarLayout.setMargin(0)
        self.toolBarLayout.setSpacing(2)
        self.layout().insertWidget(0, self.toolBar)
        #Autoscale
        self._addToolButton(self.zoomResetIcon,
                            self._zoomReset,
                            'Auto-Scale the Graph')

        #y Autoscale
        self.yAutoScaleButton = self._addToolButton(self.yAutoIcon,
                            self._yAutoScaleToggle,
                            'Toggle Autoscale Y Axis (On/Off)',
                            toggle = True)
        if QTVERSION < '4.0.0':
            self.yAutoScaleButton.setState(qt.QButton.On)
        else:
            self.yAutoScaleButton.setChecked(True)
            self.yAutoScaleButton.setDown(True)


        #x Autoscale
        self.xAutoScaleButton = self._addToolButton(self.xAutoIcon,
                            self._xAutoScaleToggle,
                            'Toggle Autoscale X Axis (On/Off)',
                            toggle = True)
        if QTVERSION < '4.0.0':
            self.xAutoScaleButton.setState(qt.QButton.On)
        else:
            self.xAutoScaleButton.setChecked(True)
            self.xAutoScaleButton.setDown(True)

        #y Logarithmic
        self.yLogButton = self._addToolButton(self.logyIcon,
                            self._toggleLogY,
                            'Toggle Logarithmic Y Axis (On/Off)',
                            toggle = True)
        if QTVERSION < '4.0.0':
            self.yLogButton.setState(qt.QButton.Off)
        else:
            self.yLogButton.setChecked(False)
            self.yLogButton.setDown(False)

        #toggle Points/Lines
        tb = self._addToolButton(self.togglePointsIcon,
                             self._togglePointsSignal,
                             'Toggle Points/Lines')


        #fit icon
        self.fitButton = self._addToolButton(self.fitIcon,
                                 self._fitIconSignal,
                                 'Simple Fit of Active Curve')


        self.newplotIcons = False
        if self.newplotIcons:
            tb = self._addToolButton(self.averageIcon,
                                self._averageIconSignal,
                                 'Average Plotted Curves')

            tb = self._addToolButton(self.deriveIcon,
                                self._deriveIconSignal,
                                 'Take Derivative of Active Curve')

            tb = self._addToolButton(self.smoothIcon,
                                 self._smoothIconSignal,
                                 'Smooth Active Curve')

            tb = self._addToolButton(self.swapSignIcon,
                                self._swapSignIconSignal,
                                'Multiply Active Curve by -1')

            tb = self._addToolButton(self.yMinToZeroIcon,
                                self._yMinToZeroIconSignal,
                                'Force Y Minimum to be Zero')

            tb = self._addToolButton(self.subtractIcon,
                                self._subtractIconSignal,
                                'Subtract Active Curve')
        #save
        infotext = 'Save Active Curve or Widget'
        tb = self._addToolButton(self.saveIcon,
                                 self._saveIconSignal,
                                 infotext)

        if QTVERSION > '4.0.0':
            infotext = "Call/Load 1D Plugins"
            tb = self._addToolButton(self.pluginIcon,
                                 self._pluginClicked,
                                 infotext)

        self.toolBarLayout.addWidget(HorizontalSpacer(self.toolBar))

        # ---print
        tb = self._addToolButton(self.printIcon,
                                 self.printGraph,
                                 'Prints the Graph')

    def _addToolButton(self, icon, action, tip, toggle=None):
        tb      = qt.QToolButton(self.toolBar)            
        if QTVERSION < '4.0.0':
            tb.setIconSet(icon)
            qt.QToolTip.add(tb,tip) 
            if toggle is not None:
                if toggle:
                    tb.setToggleButton(1)
        else:
            tb.setIcon(icon)
            tb.setToolTip(tip)
            if toggle is not None:
                if toggle:
                    tb.setCheckable(1)
        self.toolBarLayout.addWidget(tb)
        self.connect(tb,qt.SIGNAL('clicked()'), action)
        return tb
                
    def _zoomReset(self):
        if DEBUG:
            print("_zoomReset")
        self.graph.zoomReset()

    def _yAutoScaleToggle(self):
        if DEBUG:
            print("_yAutoScaleToggle")
        if self.graph.yAutoScale:
            self.graph.yAutoScale = False
            self.yAutoScaleButton.setDown(False)
            if QTVERSION < '4.0.0':
                self.yButton.setState(qt.QButton.Off)
            else:
                self.yAutoScaleButton.setChecked(False)
            self.graph.setY1AxisLimits(*self.graph.getY1AxisLimits())
            y2limits = self.graph.getY2AxisLimits()
            if y2limits is not None:
                self.graph.setY2AxisLimits(*y2limits)
        else:
            self.graph.yAutoScale = True
            if QTVERSION < '4.0.0':
                self.yAutoScaleButton.setState(qt.QButton.On)
            else:
                self.yAutoScaleButton.setDown(True)
            self.graph.zoomReset()
                       
    def _xAutoScaleToggle(self):
        if DEBUG:
            print("_xAutoScaleToggle")
        if self.graph.xAutoScale:
            self.graph.xAutoScale = False
            self.xAutoScaleButton.setDown(False)
            if QTVERSION < '4.0.0':
                self.xAutoScaleButton.setState(qt.QButton.Off)
            else:
                self.xAutoScaleButton.setChecked(False)
            self.graph.setX1AxisLimits(*self.graph.getX1AxisLimits())
        else:
            self.graph.xAutoScale = True
            self.xAutoScaleButton.setDown(True)
            if QTVERSION < '4.0.0':
                self.xAutoScaleButton.setState(qt.QButton.On)
            else:
                self.xAutoScaleButton.setChecked(True)
            self.graph.zoomReset()
                       
    def _toggleLogY(self):
        if DEBUG:
            print("_toggleLogY")
        if self._logY:
            self._logY = False
        else:
            self._logY = True
        self.activeCurve = self.graph.getActiveCurve(justlegend=1)

        self.graph.clearCurves()    
        self.graph.toggleLogY()

        self.replot()

    def _togglePointsSignal(self):
        self._toggleCounter = (self._toggleCounter + 1) % 3
        if self._toggleCounter == 1:
            self.graph.setDefaultPlotLines(True)
            self.graph.setDefaultPlotPoints(True)
        elif self._toggleCounter == 2:
            self.graph.setDefaultPlotPoints(True)
            self.graph.setDefaultPlotLines(False)
        else:
            self.graph.setDefaultPlotLines(True)
            self.graph.setDefaultPlotPoints(False)
        self.graph.setActiveCurve(self.graph.getActiveCurve(justlegend=1))
        self.graph.replot()

    def _fitIconSignal(self):
        print("fit icon signal")

    def _averageIconSignal(self):
        print("average icon signal")

    def _deriveIconSignal(self):
        print("deriveIconSignal")

    def _smoothIconSignal(self):
        print("smoothIconSignal")

    def _swapSignIconSignal(self):
        print("_swapSignIconSignal")

    def _yMinToZeroIconSignal(self):
        print("_yMinToZeroIconSignal")

    def _subtractIconSignal(self):
        print("_subtractIconSignal")

    def _saveIconSignal(self):
        print("_saveIconSignal")

    def _pluginClicked(self):
        actionList = []
        menu = qt.QMenu(self)
        text = qt.QString("Reload")
        menu.addAction(text)
        actionList.append(text)
        menu.addSeparator()
        callableKeys = ["Dummy"]
        for m in self.pluginList:
            if m == "PyMcaPlugins.Plugin1DBase":
                continue
            module = sys.modules[m]
            if hasattr(module, 'MENU_TEXT'):
                text = qt.QString(module.MENU_TEXT)
            else:
                text = os.path.basename(module.__file__)
                if text.endswith('.pyc'):
                    text = text[:-4]
                elif text.endswith('.py'):
                    text = text[:-3]
                text = qt.QString(text)
            methods = self.pluginInstanceDict[m].getMethods(plottype="SCAN") 
            if not len(methods):
                continue
            menu.addAction(text)
            actionList.append(text)
            callableKeys.append(m)
        a = menu.exec_(qt.QCursor.pos())
        if a is None:
            return None
        idx = actionList.index(a.text())
        if idx == 0:
            n = self.getPlugins()
            if n < 1:
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Information)
                msg.setText("Problem loading plugins")
                msg.exec_()
            return        
        key = callableKeys[idx]
        methods = self.pluginInstanceDict[key].getMethods(plottype="SCAN")
        if len(methods) == 1:
            idx = 0
        else:
            actionList = []
            methods.sort()
            menu = qt.QMenu(self)
            for method in methods:
                text = qt.QString(method)
                pixmap = self.pluginInstanceDict[key].getMethodPixmap(method)
                tip = qt.QString(self.pluginInstanceDict[key].getMethodToolTip(method))
                if pixmap is not None:
                    action = qt.QAction(qt.QIcon(qt.QPixmap(pixmap)), text, self)
                else:
                    action = qt.QAction(text, self)
                if tip is not None:
                    action.setToolTip(tip)
                menu.addAction(action)
                actionList.append((text, pixmap, tip, action))
            qt.QObject.connect(menu, qt.SIGNAL("hovered(QAction *)"), self._actionHovered)
            a = menu.exec_(qt.QCursor.pos())
            if a is None:
                return None
            idx = -1
            for action in actionList:
                if a.text() == action[0]:
                    idx = actionList.index(action)
        try:
            self.pluginInstanceDict[key].applyMethod(methods[idx])    
        except:
            msg = qt.QMessageBox(self)
            msg.setIcon(qt.QMessageBox.Critical)
            if QTVERSION < '4.0.0':
                msg.setText("%s" % sys.exc_info()[1])
            else:
                msg.setWindowTitle("Plugin error")
                msg.setText("An error has occured while executing the plugin:")
                msg.setInformativeText(str(sys.exc_info()[1]))
                msg.setDetailedText(traceback.format_exc())
            msg.exec_()

    def _actionHovered(self, action):
        tip = action.toolTip()
        if str(tip) != str(action.text()):
            qt.QToolTip.showText(qt.QCursor.pos(), tip)

    def printGraph(self):
        print("prints the graph")

class HorizontalSpacer(qt.QWidget):
    def __init__(self, *args):
        qt.QWidget.__init__(self, *args)
      
        self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Expanding,
                           qt.QSizePolicy.Fixed))

    

if __name__ == "__main__":
    import numpy
    x = numpy.arange(100.)
    y = x * x
    app = qt.QApplication([])
    plot = Plot1DWindow(uselegendmenu=True)
    plot.show()
    plot.addCurve(x, y, "dummy")
    plot.addCurve(x+100, x*x)
    print("Active curve = ", plot.getActiveCurve())
    print("X Limits = ",     plot.getGraphXLimits())
    print("Y Limits = ",     plot.getGraphYLimits())
    print("All curves = ",   plot.getAllCurves())
    plot.removeCurve("dummy")
    plot.addCurve(x, y, "dummy 2")
    print("All curves = ",   plot.getAllCurves())
    app.exec_()
