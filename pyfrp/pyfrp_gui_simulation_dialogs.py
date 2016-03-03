#=====================================================================================================================================
#Copyright
#=====================================================================================================================================

#Copyright (C) 2014 Alexander Blaessle, Patrick Mueller and the Friedrich Miescher Laboratory of the Max Planck Society
#This software is distributed under the terms of the GNU General Public License.

#This file is part of PyFRAP.

#PyFRAP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#===========================================================================================================================================================================
#Module Description
#===========================================================================================================================================================================

#PyQT Dialogs for simulation class
#(1) 

#===========================================================================================================================================================================
#Importing necessary modules
#===========================================================================================================================================================================

#QT
from PyQt4 import QtGui, QtCore

#PyFRAP GUI classes
import pyfrp_gui_basics

#PyFRAP modules
from pyfrp_term_module import *
import pyfrp_img_module
import pyfrp_misc_module

#Numpy/Scipy
import numpy as np

#Misc 
import os


#===================================================================================================================================
#Dialog for editing simulation settings
#===================================================================================================================================

class simulationSettingsDialog(pyfrp_gui_basics.basicSettingsDialog):
	
	def __init__(self,simulation,parent):
		
		super(simulationSettingsDialog,self).__init__(parent)
		
		self.simulation = simulation
		
		#Labels
		self.lblD = QtGui.QLabel("D:", self)
		self.lblProd = QtGui.QLabel("Prod:", self)
		self.lblDegr = QtGui.QLabel("Degr:", self)
		
		self.lblSteps = QtGui.QLabel("Timesteps:", self)
		self.lblICmode = QtGui.QLabel("IC Mode:", self)
		self.lblTimeScale = QtGui.QLabel("Time Scaling:", self)
		
		#LineEdits
		self.qleD = QtGui.QLineEdit(str(self.simulation.D))
		self.qleProd = QtGui.QLineEdit(str(self.simulation.prod))
		self.qleDegr = QtGui.QLineEdit(str(self.simulation.degr))
		
		self.qleSteps = QtGui.QLineEdit(str(self.simulation.stepsSim))
		
		self.doubleValid=QtGui.QDoubleValidator()
		self.intValid=QtGui.QIntValidator()
		
		self.qleD.setValidator(self.doubleValid)
		self.qleProd.setValidator(self.doubleValid)
		self.qleDegr.setValidator(self.doubleValid)
		
		self.qleSteps.setValidator(self.intValid)
		
		self.qleD.editingFinished.connect(self.setD)
		self.qleProd.editingFinished.connect(self.setProd)
		self.qleDegr.editingFinished.connect(self.setDegr)
		self.qleSteps.editingFinished.connect(self.setSteps)
		
		#ComboBox
		self.comboIC = QtGui.QComboBox(self)
		self.comboIC.addItem("Ideal")
		self.comboIC.addItem("Radial")
		self.comboIC.addItem("Interpolation")
		
		self.comboTS = QtGui.QComboBox(self)
		self.comboTS.addItem("Linear")
		self.comboTS.addItem("Logarithmic")
		
		self.initComboIC()
		self.initComboTS()
		
		self.comboIC.activated[str].connect(self.setICMode)   
		self.comboTS.activated[str].connect(self.setTS)   
		
		#Layout
		self.grid.addWidget(self.lblD,1,1)
		self.grid.addWidget(self.lblProd,2,1)
		self.grid.addWidget(self.lblDegr,3,1)
		
		self.grid.addWidget(self.qleD,1,2)
		self.grid.addWidget(self.qleProd,2,2)
		self.grid.addWidget(self.qleDegr,3,2)
		
		self.grid.addWidget(self.lblSteps,1,3)
		self.grid.addWidget(self.lblTimeScale,2,3)
		
		self.grid.addWidget(self.qleSteps,1,4)
		self.grid.addWidget(self.comboTS,2,4)
		
		self.grid.addWidget(self.lblICmode,1,5)
		self.grid.addWidget(self.comboIC,1,6)
		
		self.setWindowTitle("Simulation Settings")
		
		self.show()
			
	def setD(self):
		self.simulation.setD(float(str(self.qleD.text())))
	
	def setProd(self):
		self.simulation.setProd(float(str(self.qleProd.text())))
	
	def setDegr(self):
		self.simulation.setDegr(float(str(self.qleDegr.text())))
	
	def setSteps(self):
		self.simulation.setTimesteps(int(str(self.qleSteps.text())))
	
	def setTS(self,text):
		text=str(text)
		if text=="Linear":
			self.simulation.toLinearTimeScale()
		if text=="Logarithmic":
			self.simulation.toLogTimeScale()
			
	def setICMode(self,text):
		self.simulation.setInterpolationMode(int(self.comboIC.currentIndex()))
		
	def initComboIC(self):
		self.comboIC.setCurrentIndex(self.simulation.ICmode-1)
			
	def initComboTS(self):
		if np.diff(self.simulation.tvecSim)[0]==np.diff(self.simulation.tvecSim)[-1]:
			self.comboTS.setCurrentIndex(0)
		else:
			self.comboTS.setCurrentIndex(0)


			
#===================================================================================================================================
#Dialogs for simulation progress
#===================================================================================================================================

class simulationProgressDialog(pyfrp_gui_basics.progressDialog):
	
	def __init__(self,parent):
		super(simulationProgressDialog,self).__init__(parent)
		
		#Labels
		self.lblName.setText("Simulation in progress...")
		
		#Window title
		self.setWindowTitle('Simulation progress')
		    
		self.show()	

class simulationThread(pyfrp_gui_basics.pyfrpThread):
	
	def __init__(self, embryo=None, parent=None):
		
		super(simulationThread,self).__init__(parent)
		self.obj=embryo
		self.embryo=embryo
		
			
	def runTask(self,debug=False):
		self.embryo.simulation.run(signal=self.progressSignal,embCount=None,debug=debug)
			
		
		
		