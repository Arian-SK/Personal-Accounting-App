from PyQt6.QtWidgets import * #to import every tools from QtWidgets
from PyQt6.QtCore import QUrl #to define path
from PyQt6.QtGui import QIcon #for icons
from PyQt6 import uic # for loading ui seperate from source code(qt designer)
from PyQt6.QtMultimedia import QSoundEffect #for soundtracks
import sys
import re #regex
import time #cooldown
import os #to fine the path
import pandas as pd

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
        self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
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
        self.buttonMute.clicked.connect(self.play_mute_background)
        self.lineCity.textChanged.connect(self.change_text)

        #attributes:
        self.city_list = ['Tehran', 'ُSari', 'Karaj', 'Babol', 'Esfahan',
         'Shiraz', 'Yazd', 'Tabriz', 'Kerman', 'Qom', 'Mashhad', 'Ahvaz',
          'Zahedan', 'Kashan', 'Arak', 'Zanjan', 'Ardabil', 'Rasht', 'Amirkola',
           'Hamedan', 'Gorgan', 'Eslamshahr', 'Bandar Abbas', 'Oromieh']
        
        #auto completer:
        self.completer = QCompleter(self.city_list)
        self.lineCity.setCompleter(self.completer)
        
    def change_text(self):
        city = self.lineCity.text()
        new_city = city.capitalize()
        self.lineCity.setText(new_city)

    def open_login_page(self):
        windowLogin.show()
        windowSignUp.close()

    #function to check inputs:
    def check(self):
        self.labelException.setVisible(True)
        
        if self.check_fname() == False:
            return
        if self.check_lname() == False:
            return
        if self.check_pnumber() == False:
            return
        if self.check_username() == False:
            return
        if self.check_email() == False:
            return
        if self.check_password()== False:
            return
        if self.confirm_password() == False:
            return
        if self.check_city() == False:
            return
        if self.check_date() == False:
            return
        if self.checkBoxTerms.isChecked() == False:
            self.labelException.setText('you have to agree with our TOS')
            return
        else:
            self.labelException.setText('')

        self.add_memeber()
        self.reset_inputs()
        windowSignUp.close()
        windowMain.show()

    def reset_inputs(self):
        self.lineFname.setText('')
        self.lineLname.setText('')
        self.linePnumber.setText('')
        self.lineEmail.setText('')
        self.linePass.setText('')
        self.lineUsername.setText('')
        self.lineCity.setText('')
        self.labelException.setVisible(False)

    def add_memeber(self):
        fname = self.lineFname.text()
        lname = self.lineLname.text()
        pnumber = self.linePnumber.text()
        email = self.lineEmail.text()
        password = self.linePass.text()
        username = self.lineUsername.text()
        city = self.lineCity.text()
        date = self.date
        memeber_info = {'first name': [fname], 'last name': [lname], 'phone number':[pnumber], 'username':[username],
        'email':[email], 'password':[password], 'city':[city], 'date':[date]}

        database_path = project_path + '//database//members_info.xlsx'

        df_new = pd.DataFrame(memeber_info)
    
        # Read existing data
        df_database = pd.read_excel(database_path)
        
        # Append new data
        df_combined = df_database._append(df_new, ignore_index=True)
        
        # Save the combined data to Excel
        df_combined.to_excel(database_path, index=False)

    def check_fname(self):
        fname = self.lineFname.text()
        if fname.isalpha():
            self.labelException.setText('')
            self.labelFname.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            return True
        else:
            self.labelException.setText('invalid first name')
            self.labelFname.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
        """)
            return False

    def check_lname(self):
        lname = self.lineLname.text()
        if lname.isalpha():
            self.labelException.setText('')
            self.labelLname.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            return True
        else:
            self.labelException.setText('invalid last name')
            self.labelLname.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    def check_pnumber(self):
        pnumber = self.linePnumber.text()
        if pnumber.startswith('09') and pnumber.isnumeric() and len(pnumber) == 11 and pnumber :
            self.labelException.setText('')
            self.labelPnumber.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            df = pd.read_excel(project_path + '//database//members_info.xlsx')
            if int(pnumber) in df['phone number'].values:
                self.labelException.setText('phone number already in use')
                self.labelPnumber.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                return False
            else:
                self.labelException.setText('')
                self.labelPnumber.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                return True
        else:
            self.labelException.setText('invalid phone number')
            self.labelPnumber.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    def check_email(self):
        email = self.lineEmail.text()
        valid_email = r'^[a-zA-Z0-9._%+-]+@(gmail|yahoo)\.com$'
        if re.match(valid_email, email):
            self.labelException.setText('')
            self.labelEmail.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            df = pd.read_excel(project_path + '//database//members_info.xlsx')
            if email in df['email'].values:
                self.labelException.setText('email already in use')
                self.labelEmail.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                return False
            else:
                self.labelException.setText('')
                self.labelEmail.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                return True
        else:
            self.labelException.setText('invalid email')
            self.labelEmail.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    def check_password(self):
        valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        password = self.linePass.text()
        if re.match(valid_password, password):
            self.labelException.setText('')
            self.labelPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            return True
        else:
            self.labelException.setText('invalid password')
            self.labelPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False
    
    def check_username(self):
        username = self.lineUsername.text()
        if len(username) > 0:
            self.labelException.setText('')
            self.labelUsername.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            df = pd.read_excel(project_path + '//database//members_info.xlsx')
            if username in df['username'].values:
                self.labelException.setText('username taken')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                return False
            else:
                self.labelException.setText('')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                return True
        else:
            self.labelException.setText("invalid username")
            self.labelUsername.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

        

    def confirm_password(self):
        password = self.linePass.text()
        retyped_password = self.lineConfirmPass.text()
        if retyped_password == password:
            self.labelException.setText('')
            self.labelConfirmPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            return True
        else: 
            self.labelException.setText("Retyped password doesn't match the original one")
            self.labelConfirmPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False
                     
    def check_city(self):
        city = self.lineCity.text()
        if city in self.city_list:
            self.labelException.setText('')
            self.labelCity.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
            """)
            return True
        else:
            self.labelException.setText('invalid date')
            self.labelPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    def check_date(self):
        day = int(self.comboDay.currentText())
        month = self.comboMonth.currentText()
        year = int(self.comboYear.currentText())
        if 0 < day <= self.return_max_day(month, year):
            self.labelException.setText('')
            self.labelFname.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            self.date = str(year) + '/' + month + '/' + str(day)
            return True
        else:
            self.labelException.setText('invalid date')
            self.labelPass.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
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
    
    def play_mute_background(self):
        global effect
        if effect.isMuted() == True:
            effect.setMuted(False)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
            windowLogin.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
        else:
            effect.setMuted(True)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            windowLogin.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))

#Login ui:
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//LoginPage.ui", self)
        self.setWindowIcon(QIcon(project_path + "//resources//login icon.ico"))
        self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
        self.setWindowTitle('Login')

        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(starBackgroundPath)
        self.labelPic.lower()

        #exception handling label:
        self.labelException.setVisible(False)
        self.attempts = 0

        #signal handling:
        self.labelPassForgot.mousePressEvent = self.open_passForgot
        self.buttonLogin.clicked.connect(self.check_login_input)
        self.buttonSignUp.clicked.connect(self.open_signUp_page)
        self.buttonMute.clicked.connect(self.play_mute_background)

    def open_passForgot(self,*arg, **kwargs):
        windowLogin.close()
        windowPassRecovery.show()

    def open_signUp_page(self):
        windowSignUp.show()
        windowLogin.close()

    #function to check inputs:
    def check_login_input(self):
        if self.attempts < 3:
            username = self.lineUsername.text()
            password = self.linePassword.text()
            valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
            if 0 < len(username):
                self.labelException.setVisible(False)
                self.labelException.setText('')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
            else:
                self.labelException.setVisible(True)
                self.labelException.setText('invalid username')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                self.lock()
                return

            if re.match(valid_password, password):
                self.labelException.setVisible(False)
                self.labelException.setText('')
                self.labelPassword.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                if self.check_login(username, password):
                    windowLogin.close()
                    windowMain.show()
                else:
                    self.lock()
                    return
            else:
                self.labelException.setVisible(True)
                self.labelException.setText('invalid password')
                self.labelPassword.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                self.lock()
                return
                
        else:
            self.countdown()
    
    def check_login(self, username, password):
        try:
            # Read the Excel file
            df = pd.read_excel(project_path + '//database//members_info.xlsx')
            
            # Check if the DataFrame has the required columns
            if 'username' not in df.columns or 'password' not in df.columns:
                self.labelException.setVisible(True)
                self.labelException.setText('Corrupted database')
                return False
       
            # Check if there is a matching row
            user_row = df[(df['username'] == username) & (df['password'] == password)]
            if not user_row.empty:
                self.labelException.setText('')
                print('loging seccessful...')
                return True
            else:
                self.labelException.setVisible(True)
                self.labelException.setText('password or username not found')
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
            
    def lock(self):
        print(self.attempts)
        self.attempts += 1
        if self.attempts == 3:
            self.labelException.setText("max attemts reached!")
            self.stored_time1 = time.time()
            self.countdown()

    def countdown(self):
        self.stored_time2 = time.time()
        self.time_difference = self.stored_time2 - self.stored_time1
        if int(self.time_difference) < 60:
            self.labelException.setVisible(True)
            self.labelException.setText('please try again in: ' + str(int(60 - self.time_difference)) + ' second(s)') 
        else:
            self.attempts = 0
            self.labelException.setText('')
            self.check_login_input()

    def play_mute_background(self):
        global effect
        if effect.isMuted() == True:
            effect.setMuted(False)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
            windowSignUp.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
        else:
            effect.setMuted(True)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            windowSignUp.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            
class PassRecovery(QWidget):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//PasswordRecoveryPage.ui", self)
        self.setWindowTitle('Recovery')
        self.setWindowIcon(QIcon(project_path + "//resources//login icon.ico"))
        
        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(starBackgroundPath)  
        self.labelPic.lower()

        #signal handling:
        self.labelException.setVisible(False)
        self.buttonVia.clicked.connect(self.send_via)
        self.buttonBack.clicked.connect(self.go_back)
        self.buttonSend.clicked.connect(self.check)

    def send_via(self):
        self.labelException.setVisible(False)
        self.lineInput.setText('')
        if self.labelInput.text() == 'Email:':
            self.labelInput.setText('Phone number:')
            self.buttonVia.setText('Send via Email')
        else:
            self.labelInput.setText('Email:')
            self.buttonVia.setText('Send via SMS')
            
    def check(self):
        self.labelException.setVisible(True)
        if self.labelInput.text() == 'Email:':
            if self.check_email():
                self.labelException.setText('we have sent a message to your email address seccessfully')
            else:
                self.labelException.setText('email not found')
        else:
            if self.check_pnumber():
                self.labelException.setText('we have sent a SMS to your number seccessfully')
            else:
                self.labelException.setText('phone number not found')

    def check_pnumber(self):
        pnumber = self.lineInput.text()
        df = pd.read_excel(project_path + '//database//members_info.xlsx')
        if int(pnumber) in df['phone number'].values:
            return True
        else:
            return False
    
    def check_email(self):
        email = self.lineInput.text()
        df = pd.read_excel(project_path + '//database//members_info.xlsx')
        if email in df['email'].values:
            return True
        else:
            return False

    def go_back(self):
        windowPassRecovery.close()
        windowLogin.show()

effect = QSoundEffect()
#main:
if __name__ == '__main__':
    app = QApplication(sys.argv)

    #sound part:
    file_path = project_path + '//resources//background music.wav'
    effect.setSource(QUrl.fromLocalFile(file_path))
    effect.setLoopCount(-2)
    effect.play()

    #define windows:
    windowLogin = LoginPage()
    windowMain = MainApp()
    windowSignUp = SignUp()
    windowPassRecovery = PassRecovery()
    
    #show window(s):
    windowLogin.show()

    #exit:
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')