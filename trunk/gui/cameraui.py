from .common import *
from . import cameracontrols
from . import imageviewer
from . import processing 
import log

try:
	from . import calibrate
except:
	log.logException('Unable to import calibration tools',log.WARNING)
	calibrate = None



class CameraControls(BaseWidget,QtGui.QTabWidget):

	def setup(self,camera):
		self.camera = camera
		self.controls = []
		self.tabs = {}

		tab = GeneralTab(self)
		self.addTab(tab,'General')
		self.tabs['General'] = tab
		
		for property in camera.getProperties():
			
			section = property.getSection()
			if section not in self.tabs:
				tab = CameraControlsTab(self)
				self.addTab(tab,section)
				self.tabs[section] = tab
				tab._up = self 
				
			tab = self.tabs[section]
			cls = cameracontrols.controlTypeToClass[property.getControlType()]
			control = cls(qtparent=tab.CameraControlsTabScroll.CameraControlsTabMainArea,cameraProperty=property)
			self.controls.append(control)

		self.refreshFromCamera()
		
		for tab in self.tabs.values():
			tab.CameraControlsTabScroll.CameraControlsTabMainArea.adjustSize()
		
	def refreshFromCamera(self):
		for control in self.controls:
			control.fromCamera()



class CameraControlsTab(BaseWidget,QtGui.QWidget):
	
	class Layout(BaseLayout,QtGui.QVBoxLayout):
		def init(self):
			self._up.setLayout(self)
			self.setSpacing(0)
			self.setContentsMargins(0,0,0,0)
			
	class CameraControlsTabScroll(BaseWidget,QtGui.QScrollArea):
		def init(self):
			self._up.Layout.addWidget(self,1)
			self.setContentsMargins(0,0,0,0)
			
		class CameraControlsTabMainArea(BaseWidget,QtGui.QWidget):
			
			class Layout(BaseLayout,QtGui.QFormLayout):
				def init(self):
					self._up.setLayout(self)
		
			def init(self):
				self._up.setWidget(self)



class GeneralTab(CameraControlsTab):

	class CameraControlsTabScroll(CameraControlsTab.CameraControlsTabScroll):
			
		class CameraControlsTabMainArea(CameraControlsTab.CameraControlsTabScroll.CameraControlsTabMainArea):
			
			def init(self):
				CameraControlsTab.CameraControlsTabScroll.CameraControlsTabMainArea.init(self)
				
			def getCameraIndex(self):
				return self.app.cameras.index(self._up._up._up.camera)+1
				
				
			class Rotate(BaseWidget,QtGui.QComboBox):
				
				def init(self):
					self._up.Layout.addRow(self.tr('Rotation'),self)
					self.addItem(self.tr('No rotation'),0)
					self.addItem(self.tr('90 CW'),90)
					self.addItem(self.tr('180'),180)
					self.addItem(self.tr('90 CCW'),270)
					if self._up.getCameraIndex() in self.app.settings.rotate: 
						self.setCurrentIndex(self.findData(self.app.settings.rotate[self._up.getCameraIndex()]))
				def oncurrentIndexChanged(self,index):
					angle = self.itemData(index)
					self.app.settings.rotate[self._up.getCameraIndex()] = angle
			
					
			class CalibrationControlsBox(BaseWidget,QtGui.QGroupBox):
				
				def init(self):
					self._up.Layout.addRow(self)
	
				class Layout(BaseLayout,QtGui.QFormLayout):
					def init(self):
						self._up.setLayout(self)
			
				class CalbrationStateLabel(BaseWidget,QtGui.QLabel):
					
					def init(self):
						self._up.Layout.addRow(self)
						self.update()
						self.app.calibrationDataChanged.connect(self.update)
						
					def update(self):
						cameraIndex = self._up._up.getCameraIndex()
						if self.app.settings.calibrators[cameraIndex] and self.app.settings.calibrators[cameraIndex].isReady():
							self.setText(self.tr('<p>Calibration configured</p>'))
						else:
							self.setText(self.tr('<p>No calibration configured</p>'))
	
	
				class CorrectCheckbox(BaseWidget,QtGui.QCheckBox):
					def init(self):
						self._up.Layout.addRow(self)
						self.setText(self.tr('Correct images using calibration data'))
						self.app.calibrationDataChanged.connect(self.update)
						cameraIndex = self._up._up.getCameraIndex()
						if self.app.settings.calibrators[cameraIndex] and self.app.settings.calibrators[cameraIndex].isActive():
							self.setChecked(True)
						else:
							self.setChecked(False) 
						
						
					def onstateChanged(self):
						cameraIndex = self._up._up.getCameraIndex()
						if self.app.settings.calibrators[cameraIndex]:
							self.app.settings.calibrators[cameraIndex].setActive(self.isChecked())
							
	
					def update(self):
						cameraIndex = self._up._up.getCameraIndex()
						if self.app.settings.calibrators[cameraIndex] and self.app.settings.calibrators[cameraIndex].isReady():
							self.show()
						else:
							self.hide()
	
					
				class CalibrateButton(BaseWidget,QtGui.QPushButton):
					def init(self):
						self._up.Layout.addRow(self)
						self.setText(self.tr('Calibrate with current image'))
						self.setChecked(self.app.settings.crop.get('enabled',False))
						
					def onclicked(self):
						if calibrate is None:
							e = QtGui.QMessageBox.critical(
								self.app.SetupWindow,
								self.tr('Error'),
								self.tr("""
									<p>Calibration is not available on your system. If you're <i>not</i> running on Windows check that you have
									OpenCV 2.3 for Python and NumPy installed and that the OpenCV Python bindings are on your Python path.</p> 
								""")
							)
							return
						
						cameraIndex = self._up._up.getCameraIndex()
						preview = self.app.previews[cameraIndex]
						
						if not preview.raw.hasImage():
							return
						
						dialog = calibrate.CalibrateDialog(self)
						dialog.setModal(True)
						dialog.open()
						dialog.go(preview.raw._pm,cameraIndex=cameraIndex)
	
	
			class CropControlsBox(BaseWidget,QtGui.QGroupBox):
				
				def init(self):
					self._up.Layout.addRow(self)
	
				class Layout(BaseLayout,QtGui.QFormLayout):
					def init(self):
						self._up.setLayout(self)
			
	
				class CropCheckbox(BaseWidget,QtGui.QCheckBox): 
					def init(self):
						self._up.Layout.addRow(self)
						self.setText(self.tr('Crop images'))
						self.setChecked(self.app.settings.crop.get('enabled',False))
						
					def onstateChanged(self):
						if self.isChecked():
							self._up.CropSpinners.update()
							self.app.settings.crop.enabled = True
						else:
							self.app.settings.crop.enabled = False
					
					
				class CropSpinners(BaseWidget,QtGui.QWidget):
					def init(self):
						self._up.Layout.addRow(self)
						cameraIndex = self._up._up.getCameraIndex()
						if not self.app.settings.crop.get('coords',None) or cameraIndex not in self.app.settings.crop.coords:
							return
						c = self.app.settings.crop.coords[cameraIndex]
						self.Left.setValue(c[0])
						self.Top.setValue(c[1])
						self.Right.setValue(c[2])
						self.Bottom.setValue(c[3])
						
					def update(self):
						cameraIndex = self._up._up.getCameraIndex()
						if not self.app.settings.crop.get('coords',None):
							self.app.settings.crop.coords = {}
						self.app.settings.crop.coords[cameraIndex] = (self.Left.value(),self.Top.value(),self.Right.value(),self.Bottom.value())
					
					class Layout(BaseLayout,QtGui.QGridLayout):
						def init(self):
							self.setContentsMargins(0,0,0,0)
							self._up.setLayout(self)
						
					class Top(BaseWidget,QtGui.QSpinBox):
						def init(self):
							self.setAccelerated(True)
							self.setMinimum(0)
							self.setMaximum(99999)
							self.localInit()
						def onvalueChanged(self):
							self._up.update()
						def localInit(self):
							self._up.Layout.addWidget(self,0,1)
							
					class Left(Top):
						def localInit(self):
							self._up.Layout.addWidget(self,1,0)
							
					class Right(Top):
						def localInit(self):
							self._up.Layout.addWidget(self,1,2)
							
					class Bottom(Top):
						def localInit(self):
							self._up.Layout.addWidget(self,2,1)
	
				
			class ReprocessButton(BaseWidget,QtGui.QPushButton):
				def init(self):
					self._up.Layout.addRow(self)
					self.setText(self.tr('Re-process current image'))
					
				def onclicked(self):
					ndx = self._up.getCameraIndex()
					image = self.app.imageManager.selected
					self.app.processingQueue.put(processing.PostCaptureJob(self.app,image,ndx))
