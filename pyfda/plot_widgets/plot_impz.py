# -*- coding: utf-8 -*-
"""
Widget for plotting impulse response

Author: Christian Muenker 2015
"""
from __future__ import print_function, division, unicode_literals, absolute_import

from PyQt4 import QtGui
import numpy as np

import pyfda.filterbroker as fb
from pyfda.pyfda_lib import impz
from pyfda.plot_widgets.plot_utils import MplWidget
#from mpl_toolkits.mplot3d.axes3d import Axes3D


class PlotImpz(QtGui.QWidget):

    def __init__(self, parent):
        super(PlotImpz, self).__init__(parent)

        self.ACTIVE_3D = False

        self.lblLog = QtGui.QLabel(self)
        self.lblLog.setText("Log.")
        self.chkLog = QtGui.QCheckBox(self)
        self.chkLog.setObjectName("chkLog")
        self.chkLog.setToolTip("Show logarithmic impulse / step response.")
        self.chkLog.setChecked(False)

        self.lblLogBottom = QtGui.QLabel("Log. bottom:")

        self.ledLogBottom = QtGui.QLineEdit(self)
        self.ledLogBottom.setText("-80")
        self.ledLogBottom.setToolTip("Minimum display value for log. scale.")

        self.lblPltStim = QtGui.QLabel(self)
        self.lblPltStim.setText("Plot Stimulus")
        self.chkPltStim = QtGui.QCheckBox(self)
        self.chkPltStim.setChecked(False)
        
        self.lblStimulus = QtGui.QLabel("Signal Type")
        self.cmbStimulus = QtGui.QComboBox(self)
        self.cmbStimulus.addItems(["Impulse","Step","Sine", "Rect", "Sawtooth"])
        self.cmbStimulus.setToolTip("Select stimulus type.")
        
        self.lblFreq = QtGui.QLabel("Freq.")

        self.ledFreq = QtGui.QLineEdit(self)
        self.ledFreq.setText("0.02")
        self.ledFreq.setToolTip("Stimulus frequency.")


        self.lblNPoints = QtGui.QLabel("<i>N</i> =")

        self.ledNPoints = QtGui.QLineEdit(self)
        self.ledNPoints.setText("0")
        self.ledNPoints.setToolTip("Number of points to calculate and display.\n"
                                   "N = 0 chooses automatically.")

        self.layHChkBoxes = QtGui.QHBoxLayout()
        self.layHChkBoxes.addStretch(10)
        
        self.layHChkBoxes.addWidget(self.lblNPoints)
        self.layHChkBoxes.addWidget(self.ledNPoints)
        self.layHChkBoxes.addStretch(1)
        self.layHChkBoxes.addWidget(self.lblLog)
        self.layHChkBoxes.addWidget(self.chkLog)
        self.layHChkBoxes.addStretch(1)
        self.layHChkBoxes.addWidget(self.lblLogBottom)
        self.layHChkBoxes.addWidget(self.ledLogBottom)
        self.layHChkBoxes.addStretch(1)
        self.layHChkBoxes.addWidget(self.lblPltStim)
        self.layHChkBoxes.addWidget(self.chkPltStim)
        self.layHChkBoxes.addStretch(1)
        self.layHChkBoxes.addWidget(self.lblStimulus)
        self.layHChkBoxes.addWidget(self.cmbStimulus)
        self.layHChkBoxes.addStretch(1)
        self.layHChkBoxes.addWidget(self.lblFreq)
        self.layHChkBoxes.addWidget(self.ledFreq)

        self.layHChkBoxes.addStretch(10)

        #----------------------------------------------------------------------
        # mplwidget
        #----------------------------------------------------------------------
        self.mplwidget = MplWidget(self)

        self.mplwidget.layVMainMpl.addLayout(self.layHChkBoxes)

        self.setLayout(self.mplwidget.layVMainMpl)

        #----------------------------------------------------------------------
        # SIGNALS & SLOTs
        #----------------------------------------------------------------------
        self.chkLog.clicked.connect(self.draw)
        self.ledNPoints.editingFinished.connect(self.draw)
        self.ledLogBottom.editingFinished.connect(self.draw)
        self.chkPltStim.clicked.connect(self.draw)
        self.cmbStimulus.currentIndexChanged.connect(self.draw)
        self.ledFreq.editingFinished.connect(self.draw)

        self.draw() # initial calculation and drawing

#------------------------------------------------------------------------------
    def _init_axes(self):
        # clear the axes and (re)draw the plot
        #
        try:
            self.mplwidget.fig.delaxes(self.ax_r)
            self.mplwidget.fig.delaxes(self.ax_i)
        except (KeyError, AttributeError, UnboundLocalError):
            pass

        if self.cmplx:
            self.ax_r = self.mplwidget.fig.add_subplot(211)
            self.ax_r.clear()
            self.ax_i = self.mplwidget.fig.add_subplot(212, sharex = self.ax_r)
            self.ax_i.clear()
        else:
            self.ax_r = self.mplwidget.fig.add_subplot(111)
            self.ax_r.clear()

        self.mplwidget.fig.subplots_adjust(hspace = 0.5)  

        if self.ACTIVE_3D: # not implemented / tested yet
            self.ax3d = self.mplwidget.fig.add_subplot(111, projection='3d')

#------------------------------------------------------------------------------
    def update_view(self):
        """
        place holder; should update only the limits without recalculating
        the impulse respons
        """
        self.draw()

#------------------------------------------------------------------------------
    def draw(self):
        if self.mplwidget.mplToolbar.enable_update:
            self.draw_impz()

#------------------------------------------------------------------------------
    def draw_impz(self):
        """
        (Re-)calculate h[n] and draw the figure
        """
        log = self.chkLog.isChecked()
        step = self.chkStep.isChecked()
        self.lblLogBottom.setEnabled(log)
        self.ledLogBottom.setEnabled(log)

        self.bb = fb.fil[0]['ba'][0]
        self.aa = fb.fil[0]['ba'][1]

        self.f_S  = fb.fil[0]['f_S']
        

        # calculate h[n]
        [h, t] = impz(self.bb, self.aa, self.f_S, step=step,
                      N=int(self.ledNPoints.text()))

        if step:
            title_str = r'Step Response'
            H_str = r'$h_{\epsilon}[n]$'
        else:
            title_str = r'Impulse Response'
            H_str = r'$h[n]$'

        self.cmplx = np.any(np.iscomplex(h))
        if self.cmplx:
            h_i = h.imag
            h = h.real
            H_i_str = r'$\Im\{$' + H_str + '$\}$'
            H_str = r'$\Re\{$' + H_str + '$\}$'
        if log:
            bottom = float(self.ledLogBottom.text())
            H_str = r'$\log$ ' + H_str + ' in dB'
            h = np.maximum(20 * np.log10(abs(h)), bottom)
            if self.cmplx:
                h_i = np.maximum(20 * np.log10(abs(h_i)), bottom)
                H_i_str = r'$\log$ ' + H_i_str + ' in dB'
        else:
            bottom = 0

        self._init_axes()


        #================ Main Plotting Routine =========================
        [ml, sl, bl] = self.ax_r.stem(t, h, bottom=bottom,
                                      markerfmt='bo', linefmt='r')
        self.ax_r.set_xlim([min(t), max(t)])
        expand_lim(self.ax_r, 0.02)
        self.ax_r.set_title(title_str)

        if self.cmplx:
            [ml_i, sl_i, bl_i] = self.ax_i.stem(t, h_i, bottom=bottom,
                                                markerfmt='rd', linefmt='b')
            self.ax_i.set_xlabel(fb.fil[0]['plt_tLabel'])
            # self.ax_r.get_xaxis().set_ticklabels([]) # removes both xticklabels
            # plt.setp(ax_r.get_xticklabels(), visible=False) 
            # is shorter but imports matplotlib, set property directly instead:
            [label.set_visible(False) for label in self.ax_r.get_xticklabels()]
            self.ax_r.set_ylabel(H_str + r'$\rightarrow $')
            self.ax_i.set_ylabel(H_i_str + r'$\rightarrow $')
        else:
            self.ax_r.set_xlabel(fb.fil[0]['plt_tLabel'])
            self.ax_r.set_ylabel(H_str + r'$\rightarrow $')


        if self.ACTIVE_3D: # not implemented / tested yet

            # plotting the stems
            for i in range(len(t)):
              self.ax3d.plot([t[i], t[i]], [h[i], h[i]], [0, h_i[i]],
                             '-', linewidth=2, color='b', alpha=.5)

            # plotting a circle on the top of each stem
            self.ax3d.plot(t, h, h_i, 'o', markersize=8,
                           markerfacecolor='none', color='b', label='ib')

            self.ax3d.set_xlabel('x')
            self.ax3d.set_ylabel('y')
            self.ax3d.set_zlabel('z')

        self.mplwidget.redraw()

#------------------------------------------------------------------------------        
    def calc_n_points(self, N_user = 0):
        """
        Calculate number of points to be displayed, depending on type of filter 
        (FIR, IIR) and user input. If the user selects 0 points, the number is
        calculated automatically.
        
        An improvement would be to calculate the dominant pole and the corresponding
        settling time.
        """

        if len(self.aa) == 1:
            if len(self.bb) == 1:
                raise TypeError(
                'No proper filter coefficients: len(a) = len(b) = 1 !')
            else:
                IIR = False
        else:
            if len(self.bb) == 1:
                IIR = True
            # Test whether all elements except first are zero
            elif not np.any(self.aa[1:]) and self.aa[0] != 0:
                #  same as:   elif np.all(a[1:] == 0) and a[0] <> 0:
                IIR = False
            else:
                IIR = True
    
        if N_user == 0: # set number of data points automatically
            if IIR:
                N = 100 # TODO: IIR: more intelligent algorithm needed
            else:
                N = min(len(self.bb),  100) # FIR: N = number of coefficients (max. 100)
        else:
            N = N_user
    
        return N


#------------------------------------------------------------------------------

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    mainw = PlotImpz(None)
    app.setActiveWindow(mainw) 
    mainw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
