from PyQt6.QtWidgets import * #to import every tools from QtWidgets
from PyQt6.QtCore import QUrl #to define path
from PyQt6.QtGui import QIcon #for icons
from PyQt6 import uic # for loading ui seperate from source code(qt designer)
from PyQt6.QtMultimedia import QSoundEffect #for soundtracks
import sys
import re #regex
import time #cooldown
import os

#finding path to project directory:
my_path = os.path.abspath(os.path.dirname(__file__))
#changing the path into readable form:
project_path = my_path.replace('\\','//')
#path to the background image:
starBackgroundPath = "background-image : url(" + str(project_path) + "//resources//star background2" + "); background-attachment: fixed"

class Cooldown:
    def __init__(self, cooldown_time):
        self.cooldown_time = cooldown_time
        self.last_called = None

    async def cooldown(self):
        now = asyncio.get_event_loop().time()
        if self.last_called is not None:
            elapsed = now - self.last_called
            remaining = self.cooldown_time - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)
        self.last_called = now 

#main menu ui:
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//MainWindow.ui", self)
        self.setWindowTitle('Main Menu')
        self.setWindowIcon(QIcon("resources//icon.ico"))
        
#sign up ui:        
class SignUp(QWidget):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//SignUpPage.ui", self)
        self.setWindowIcon(QIcon(project_path + "//resources//signup icon.ico"))
        self.setWindowTitle('Sign Up')

        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(starBackgroundPath)  
        self.labelPic.lower()
        
        #exception handling label:
        self.labelException.setVisible(False)

        #signal handling:
        self.buttonSignUp.clicked.connect(self.check)
        self.buttonLogin.clicked.connect(self.open_login_page)
    
    def open_login_page(self):
        windowLogin.show()
        windowSignUp.close()

    #function to check inputs:
    def check(self):
        self.labelException.setVisible(True)
        if self.check_date() == False:
            return False
        if self.check_fname() == False:
            return False
        if self.check_lname() == False:
            return False
        if self.check_pnumber() == False:
            return False
        if self.check_email() == False:
            return False
        if self.check_password()== False:
            return False
        if self.confirm_password() == False:
            return False

        #if nothing went wrong return True
        return True

    def check_fname(self):
        fname = self.lineFname.text()
        if fname.isalpha():
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('invalid first name')
            return False

    def check_lname(self):
        lname = self.lineLname.text()
        if lname.isalpha():
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('invalid last name')
            return False

    def check_email(self):
        email = self.lineEmail.text()
        valid_email = r'^[a-zA-Z0-9]+@(gmail|yahoo)\.com$'
        if re.match(valid_email, email):
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('Invalid email')
            return False

    def check_password(self):
        valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        password = self.linePass.text()
        if re.match(valid_password, password):
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('Invalid password')
            return False

    def confirm_password(self):
        password = self.linePass.text()
        retyped_password = self.lineConfirmPass.text()
        if retyped_password == password:
            self.labelException.setText('')
            return True
        else: 
            self.labelException.setText("Retyped password doesn't match the original one")
            return False
                     
    def check_pnumber(self):
        pnumber = self.linePnumber.text()
        if pnumber.startswith('09') and pnumber.isnumeric() and len(pnumber) == 11:
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('invalid phone number')
            return False
    def check_city(self):
        pass

    def check_date(self):
        day = int(self.comboDay.currentText())
        month = self.comboMonth.currentText()
        year = int(self.comboYear.currentText())
        if 0 < day <= self.return_max_day(month, year):
            self.labelException.setText('')
            return True
        else:
            self.labelException.setText('invalid date')
            return False

    def isLeapYear(self, year):
        leapList = list()
        for i in range(1920, 2006, 4):
            leapList.append(i)
        if year in leapList:
            return True
        else:
            return False

    def return_max_day(self, month, year):
        month_dict = {
            'January' : 31,
            'February' : 28,
            'March' : 31,
            'April' : 30,
            'May' : 31,
            'June' : 30,
            'July' : 31,
            'August' : 31,
            'September' : 30,
            'October' : 31,
            'November' : 30,
            'December' : 31,
        }
        if self.isLeapYear(year) and month == 'February':
            return 29
        else:
            return month_dict[month]

#Login ui:
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//LoginPage.ui", self)
        self.setWindowIcon(QIcon(project_path + "//resources//login icon.ico"))
        self.setWindowTitle('Login')

        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(starBackgroundPath)
        self.labelPic.lower()

        #exception handling labelL:
        self.labelException.setVisible(False)
        self.attempts = 0

        #signal handling:
        self.labelPassForgot.mousePressEvent = self.open_passForgot
        self.buttonLogin.clicked.connect(self.check_login_input)
        self.buttonSignUp.clicked.connect(self.open_signUp_page)
        

    def open_passForgot(self,*arg, **kwargs):
        pass

    def open_signUp_page(self):
        windowSignUp.show()
        windowLogin.close()

    #function to check inputs:
    def check_login_input(self):
        if self.attempts < 3:
            username = self.lineUsername.text()
            password = self.linePassword.text()
            print("called")
            valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'

            #code for searching username in database:
                #code...
                #if it's found, set labelException's text to 'username found'
                #else return False
            self.labelException.setText('username found')

            if self.labelException.text() == 'username found':
                if re.match(valid_password, password):
                    self.labelException.setVisible(False)
                    self.labelException.setText('')
                else:
                    self.labelException.setVisible(True)
                    self.labelException.setText('Invalid password')
            
            #code for searching password in the database:
                #code...
                #if exsits then close the window and run the mainwindow(or for more security add more features...)
                #else:
                #call the lock function to do a +1 attempt(after 3 attempts it will set a cooldown)
                self.lock()
        else:
            self.countdown()
            
    def lock(self):
        self.attempts += 1
        if self.attempts == 3:
            self.labelException.setText("max attemts reached!")
            self.stored_time1 = time.time()
            self.countdown()

    def countdown(self):
        self.stored_time2 = time.time()
        self.time_difference = self.stored_time2 - self.stored_time1
        if int(self.time_difference) < 60:
            self.labelException.setText('please try again in: ' + str(int(60 - self.time_difference)) + ' second(s)') 
        else:
            self.attempts = 0
            self.labelException.setText('')
            self.check_login_input()

#main:
if __name__ == '__main__':
    app = QApplication(sys.argv)

    #sound part:
    file_path = project_path + '//resources//background music.wav'
    effect = QSoundEffect()
    effect.setSource(QUrl.fromLocalFile(file_path))
    effect.setLoopCount(-2)
    effect.play()

    #define windows:
    windowLogin = LoginPage()
    windowMain = MainApp()
    windowSignUp = SignUp()
    
    #show window(s):
    windowLogin.show()
    #windowMain.show()

    #exit:
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')