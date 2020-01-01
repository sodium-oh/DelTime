import sys
import time
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QDesktopWidget, QGridLayout, QLineEdit, QTextEdit, QTextBrowser, 
    QPushButton, QApplication, QMessageBox, QLabel)
from PyQt5.QtGui import (QIcon, QFont, QPainter, QPen, QColor)
from PyQt5.QtCore import (QCoreApplication, Qt, QTranslator, QThread, pyqtSignal, QSize)

class AllTime(QThread):

	updateTimeTwo = pyqtSignal(str)

	def __init__(self, parent=None):
		super().__init__()

	def run(self):

		minute = 0
		hEnd = ''
		mEnd = ''
		while True:
			if minute > 59:
				self.updateTimeTwo.emit(f'{minute//60} час{hEnd} и {minute%60} минут{mEnd}')
			else:
				self.updateTimeTwo.emit(f'{minute} минут{mEnd}')
			time.sleep(60)
			minute += 1
			if (minute//60)%10 in [5,6,7,8,9,0] or minute//60 in [11,12,13,14]:
				hEnd = 'ов'
			elif (minute//60)%10 in [2,3,4] and minute//60 not in [12,13,14]:
				hEnd = 'а'
			else:
				hEnd = ''

			if 4 < minute%60 < 21 or (minute%60)%10 in [0,5,6,7,8,9]:
				mEnd = ''
			elif (minute%60)%10 in [2,3,4] and minute%60 not in [11,12,13,14]:
				mEnd = 'ы'
			else:
				mEnd = 'у'	

class TimeLeft(QThread): #поток считает время до отдыха

	updateTimeOne = pyqtSignal(str)
	finishTimeOne = pyqtSignal()

	def __init__(self, delayCounter, parent=None):
		super().__init__()
		self.delayCounter = delayCounter

	def run(self):

		if self.delayCounter > 0: #счётчик отложений времени
			self.updateTimeOne.emit('1 минута')
			time.sleep(60)
			self.updateTimeOne.emit('0 минут')
		else:	
			for minute in range(20, -1, -1): #Заменить 2 на 20 потом
				if minute > 4 or minute == 0:
					self.updateTimeOne.emit(str(minute) + ' минут') #Отправляет сигнал с каждой минутой
				elif minute > 1:
					self.updateTimeOne.emit(str(minute) + ' минуты')
				else:
					self.updateTimeOne.emit(str(minute) + ' минута')
				time.sleep(60)
		self.finishTimeOne.emit()	


class RelaxWindow(QWidget):

	updateTime = pyqtSignal()
	updateCounter = pyqtSignal(int)

	def __init__(self, delayCounter, parent=None):
		super().__init__(parent, Qt.Window)

		self.delayCounter = delayCounter

		self.setWindowFlags(Qt.FramelessWindowHint) #окно без стандартной рамки
		self.setWindowFlag(Qt.WindowStaysOnTopHint) #поверх всех окон флаг
		self.setAttribute(Qt.WA_TranslucentBackground) #прозрачное окно
		self.paintEvent()
		self.build()

	def paintEvent(self, event=None):

		painter = QPainter(self)
		painter.setOpacity(0.8)
		painter.setBrush(Qt.black)  
		painter.drawRect(self.rect())

	def build(self):

		text = QLabel('Дай отдохнуть глазам 20 секунд')
		text.setFont(QFont("ChipnDale2", 30))
		text.setMinimumSize(100, 200)

		self.btnRelax = QPushButton('Сделано', self)
		self.btnRelax.setFont(QFont("ChipnDale2", 30))
		self.btnRelax.setStyleSheet('QPushButton:hover{color: green;} QPushButton{color: white;}')
		self.btnRelax.clicked.connect(self.relax)

		if self.delayCounter != 4:
			self.btnDelay = QPushButton('''Отложить
на минуту''', self)
			self.btnDelay.setFont(QFont("ChipnDale2", 30))
			if self.delayCounter == 0:
				self.btnDelay.setStyleSheet('QPushButton:hover{color: red;} QPushButton{color: white;}')
			elif self.delayCounter == 1:
				self.btnDelay.setStyleSheet('''
												QPushButton{
													color: #ffcccc;
													}
												QPushButton:hover{
													color: red;
												}
											''')
												
			elif self.delayCounter == 2:
				self.btnDelay.setStyleSheet('''
												QPushButton{
													color: #ff8282;
													}
												QPushButton:hover{
													color: red;
												}
											''')
			else: #если 3
				self.btnDelay.setStyleSheet('''
												QPushButton{
													color: #ff5252;
													}
												QPushButton:hover{
													color: red;
												}
											''')
			self.btnDelay.clicked.connect(self.delay)
		else:
			self.btnDelay = QPushButton('Хватит', self)
			self.btnDelay.setFont(QFont("ChipnDale2", 30))
			self.btnDelay.setStyleSheet('QPushButton{color: red;}')

		self.grid = QGridLayout()
		self.grid.setSpacing(1)
		self.grid.setColumnStretch(0, 1)
		self.grid.setColumnStretch(3, 1)
		self.grid.setRowStretch(0, 1)
		self.grid.setRowStretch(3, 1)


		self.grid.addWidget(text, 1, 1, 1, 2)
		self.grid.addWidget(self.btnRelax, 2, 1)
		self.grid.addWidget(self.btnDelay, 2, 2)

		self.setLayout(self.grid)
		self.resize(400, 200)
		self.move(200, 200)

	def relax(self):

		self.close()
		self.updateCounter.emit(0)
		self.updateTime.emit()

	def delay(self):

		self.close()
		self.updateCounter.emit(self.delayCounter + 1)
		self.updateTime.emit()



class MainWindow(QWidget):

	def __init__(self):
		super().__init__()
		
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		
		self.oldPosition = None
		self.relaxWindow = None
		self.timeLeft = None
		self.delayCounter = 0

		self.initUI()

	def initUI(self):

		self.ico = QPushButton(self)
		self.ico.setIcon(QIcon("eye.png"))
		self.ico.setIconSize(QSize(70, 70))
		self.ico.setMinimumSize(70, 70)
		self.ico.setMaximumSize(70, 70)
		self.ico.setStyleSheet('QPushButton:hover{background-image: url("eyehover.png");}')
		self.icoSet = True
		self.ico.clicked.connect(self.changeIco)

		title = QLabel('DelTime')
		title.setFont(QFont("ChipnDale2", 44))
		title.setMinimumSize(100, 68)
		title.setAlignment(Qt.AlignVCenter)
		title.setContentsMargins(0, 0, 0, 2)

		textOne = QTextBrowser()
		textOne.setPlainText('До перерыва осталось:')
		textOne.setMinimumSize(500, 70)
		textOne.setFont(QFont("ChipnDale2", 36))

		self.timeOne = QTextBrowser()
		self.timeOne.setPlainText('20 минут')
		self.timeOne.setAlignment(Qt.AlignRight)
		self.timeOne.setMinimumSize(500, 70)
		self.timeOne.setFont(QFont("ChipnDale2", 40))

		textTwo = QTextBrowser()
		textTwo.setPlainText('Ты за компьютером:')
		textTwo.setMinimumSize(500, 70)
		textTwo.setFont(QFont("ChipnDale2", 36))

		self.timeTwo = QTextBrowser()
		self.timeTwo.setPlainText('0 минут')
		self.timeTwo.setAlignment(Qt.AlignRight)
		self.timeTwo.setMinimumSize(500, 70)
		self.timeTwo.setFont(QFont("ChipnDale2", 40))

		self.btnClose = QPushButton(self)
		self.btnClose.setIcon(QIcon("close.png"))
		self.btnClose.setIconSize(QSize(70, 70))
		self.btnClose.setMinimumSize(70, 70)
		self.btnClose.setMaximumSize(70, 70)
		self.btnClose.setStyleSheet('QPushButton:hover{background-image: url("closehover.png");}')
		self.btnClose.clicked.connect(QCoreApplication.instance().quit)

		self.btnCollapse = QPushButton(self)
		self.btnCollapse.setIcon(QIcon("sleep.png"))
		self.btnCollapse.setIconSize(QSize(70, 70))
		self.btnCollapse.setMinimumSize(70, 70)
		self.btnCollapse.setMaximumSize(70, 70)
		self.btnCollapse.setStyleSheet('QPushButton:hover{background-image: url("sleephover.png");}')
		self.btnCollapse.clicked.connect(self.collapse)

		self.grid = QGridLayout()
		self.grid.setSpacing(0)

		self.grid.addWidget(self.ico, 1, 0)
		self.grid.addWidget(title, 1, 1)
		self.grid.addWidget(self.btnCollapse, 1, 2)
		self.grid.addWidget(self.btnClose, 1, 3)
		self.grid.addWidget(textOne, 2, 1, 1, 2)
		self.grid.addWidget(self.timeOne, 3, 1, 1, 2)
		self.grid.addWidget(textTwo, 4, 1, 1, 2)
		self.grid.addWidget(self.timeTwo, 5, 1, 1, 2)

		self.setLayout(self.grid)
		self.resize(640, 350)
		self.center()
		self.show()

		self.startTimeLeft() #Запускаем метод для запуска отсчёта
		self.startAllTime() #Счётчик всего времени

		self.setWindowTitle('DelTime')
		self.setWindowIcon(QIcon('logo.png'))

	def startAllTime(self):

		self.allTime = AllTime()
		self.allTime.updateTimeTwo.connect(self.updateMinuteTimeTwo)
		self.allTime.start()

	def updateMinuteTimeTwo(self, text):

		self.timeTwo.setPlainText(text)
		self.timeTwo.setAlignment(Qt.AlignRight)

	def startTimeLeft(self):

		self.timeLeft = TimeLeft(delayCounter=self.delayCounter) #Создаём экземпляр потока
		self.timeLeft.updateTimeOne.connect(self.updateMinuteTimeOne) #Ловим изменение времени
		self.timeLeft.finishTimeOne.connect(self.message) #Запускаем метод для вывода окошка об отдыхе
		self.timeLeft.start()

	def updateMinuteTimeOne(self, text):

		self.timeOne.setPlainText(text)
		self.timeOne.setAlignment(Qt.AlignRight)

	def message(self): #Этот метод запускает окно с просьбой отдохнуть

		self.relaxWindow = RelaxWindow(delayCounter=self.delayCounter)
		self.relaxWindow.updateTime.connect(self.startTimeLeft)
		self.relaxWindow.updateCounter.connect(self.updCounter)
		self.relaxWindow.showMaximized()

	def updCounter(self, number):

		self.delayCounter = number
		print(number)

	def changeIco(self):

		if self.icoSet:
			self.ico.setIcon(QIcon("eye2.png"))
			self.ico.setIconSize(QSize(70, 70))
			self.ico.setStyleSheet('QPushButton:hover{background-image: url("eye2hover.png");}')
			self.icoSet = False
		else:
			self.ico.setIcon(QIcon("eye.png"))
			self.ico.setIconSize(QSize(70, 70))
			self.ico.setStyleSheet('QPushButton:hover{background-image: url("eyehover.png");}')
			self.icoSet = True

	def mousePressEvent(self, event):

		if event.button() == Qt.LeftButton:
			self.oldPosition = event.pos()

	def mouseReleaseEvent(self, event):

		if event.button() == Qt.LeftButton:
			self.oldPosition = None

	def mouseMoveEvent(self, event):

		if not self.oldPosition:
			return

		delta = event.pos() - self.oldPosition
		self.move(self.pos() + delta)

	def paintEvent(self, event):

		painter = QPainter(self)

		painter.setOpacity(0.8)
		painter.setBrush(QColor(0, 0, 0, 200))
		painter.setPen(QPen(Qt.darkGreen, 5))

		painter.drawRect(self.rect())


	def center(self):
        
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def collapse(self):

		self.showMinimized()


if __name__ == '__main__':

	app = QApplication(sys.argv)
	stylesheet = '''
    	QWidget{
	    	background: black;
	    }
	    QLabel{
	    	background: none;
	    	color: white;

	    }
	    QPushButton{
	    	background: transparent;
	    }
	    QTextBrowser{
	    	background: transparent;
	    	color: white;
	    	border: none;
	    	margin: 0px;
	    }
	    '''
	app.setStyleSheet(stylesheet)
	main = MainWindow()
	sys.exit(app.exec_())