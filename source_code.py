from PyQt6.QtWidgets import * #to import every tools from QtWidgets (e.g. QPushButton, QLabel ...)
from PyQt6.QtCore import QUrl, QDate, Qt, QStringListModel, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QSize  #to define path, stringmodel for viewlist, animations ...
from PyQt6.QtGui import QIcon, QKeySequence, QDesktopServices, QPixmap, QDragEnterEvent, QDropEvent #Icon, shortcut keys, link directions, Images
from PyQt6 import uic, QtCore # for loading ui seperate from source code (Qt designer)
from PyQt6.QtMultimedia import QSoundEffect #for soundtracks
import sys #to run the app
import re #regex
import time #cooldown
from datetime import datetime, timedelta #time related works
import os #to find the path
import shutil #delete account
import sqlite3 #database

#finding path to project directory:
my_path = os.path.abspath(os.path.dirname(__file__))

#changing the path into readable form:
project_path = my_path.replace('\\','//')

#path to the background images:
star_theme_path = "background-image : url(" + str(project_path) + "//resources//star theme" + "); background-attachment: fixed"
light_theme_path = "background-image : url(" + str(project_path) + "//resources//light theme" + "); background-attachment: fixed"
dark_theme_path = "background-image : url(" + str(project_path) + "//resources//dark theme" + "); background-attachment: fixed"


class HoverButton(QPushButton):
    # Define custom signals for hover enter and leave
    hover_enter = pyqtSignal()
    hover_leave = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(HoverButton, self).__init__(*args, **kwargs)

    def enterEvent(self, event):
        # Emit the hover_enter signal
        self.hover_enter.emit()
        super(HoverButton, self).enterEvent(event)

    def leaveEvent(self, event):
        # Emit the hover_leave signal
        self.hover_leave.emit()
        super(HoverButton, self).leaveEvent(event)

#custom sound class:
class Sound:
    def __init__(self, name = ''):
        self.soundtracks_list = ['background music', 'Alert', 'Correct', 'Click']
        self.soundtrack = QSoundEffect()
        if name == '':
            pass
        else:
            self.setSoundtrack(name)

    def setSoundtrack(self, name):
        if name in self.soundtracks_list:
            file_path = project_path + '//resources//' + name + '.wav'
            self.soundtrack.setSource(QUrl.fromLocalFile(file_path))
        else:
            print('soundtrack not found')

    def Play(self):
        self.soundtrack.play()
    
    def Mute(self, condition): 
        if condition == False:
            self.soundtrack.setMuted(False)
        elif condition == True:
            self.soundtrack.setMuted(True)
        else:
            raise ValueError('condition must be bool')

    def IsMuted(self):
        return self.soundtrack.isMuted()

    def SetLoop(self, count = 1):
        self.soundtrack.setLoopCount(count)

#main menu Ui:
class MainApp(QMainWindow):
    def __init__(self,username = ''):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//MainWindow.ui", self)
        self.setWindowTitle('Personal accountant')
        self.setWindowIcon(QIcon(project_path + "//resources//main icon.ico"))
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.West)

        #online time:
        self.login_time = datetime.now()
        self.buttonOnlineTime.clicked.connect(lambda: (windowLogin.play_click(), self.online_time()))

        #username:
        self.username = windowLogin.username
        self.lineUsername.setText(self.username)

        #date:
        self.dateIncome.setCalendarPopup(True)
        self.dateIncome.setDate(QDate.currentDate())
        self.dateIncome.setDisplayFormat("yyyy/MM/dd")
        self.dateCost.setCalendarPopup(True)
        self.dateCost.setDate(QDate.currentDate())
        self.dateCost.setDisplayFormat("yyyy/MM/dd")
        
        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(star_theme_path)
        self.labelPic.lower()

        #View list Categories:
        self.model = QStringListModel()
        self.listViewCategories.setModel(self.model)
        self.listViewCategories.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        #View list Reports:
        self.model_2 = QStringListModel()
        self.listViewReports.setModel(self.model_2)
        self.listViewReports.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        #View list Search:
        self.model_3 = QStringListModel()
        self.listViewSearch.setModel(self.model_3)
        self.listViewSearch.setEditTriggers(QListView.EditTrigger.NoEditTriggers)


        #others:
        self.user_folder_path = project_path + f'//database//reports//{self.username}'
        self.incomes_db_path = self.user_folder_path + '//Incomes.db'
        self.costs_db_path = self.user_folder_path + '//Costs.db'
        self.categories_db_path = self.user_folder_path + '//Categories.db'
        self.ensure_user_folder_exists()
        self.db_path = project_path + '//database//members_info.db'
        self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
        self.buttonInstagram.setIcon(QIcon(project_path + "//resources//Instagram Icon.ico"))
        self.buttonTelegram.setIcon(QIcon(project_path + "//resources//Telegram Icon.ico"))
        self.buttonTwitter.setIcon(QIcon(project_path + "//resources//Twitter Icon.ico"))
        self.comboProfiles.addItem(QIcon(project_path + '//resources//p1.ico'), 'profile1')
        self.comboProfiles.addItem(QIcon(project_path + '//resources//p2.ico'), 'profile2')
        self.comboProfiles.addItem(QIcon(project_path + '//resources//p3.ico'), 'profile3')
        self.comboProfiles.addItem(QIcon(project_path + '//resources//p4.ico'), 'profile4')
        self.comboProfiles.addItem(QIcon(project_path + '//resources//p5.ico'), 'profile5')
        self.light_theme_on = False
        self.dark_theme_on = False
        self.star_theme_on = True

        #to prevent database not found error:
        if self.username:
            self.make_incomes_table()
            self.make_costs_table()
            self.make_categories_table()
            self.load_combo_source()

        #set initial volume value
        self.sliderVolume.setValue(50)
        self.update_volume(50)

        #signal handling:

            #Main Menu:
        self.buttonRegCost.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_CostsTab()))
        self.buttonRegIncome.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_IncomeTab()))
        self.buttonSettings.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_SettingsTab()))
        self.buttonSearch.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_SearchTab()))
        self.buttonReports.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_ReportsTab()))
        self.buttonCategories.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_CategoriesTab()))
        self.buttonProfile.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_ProfileTab(), self.set_profile_pic(True)))

            #Profile:
        self.buttonPFP.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonPFP), self.open_file_dialog()))
        self.labelProfilePic.setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.comboProfiles.currentIndexChanged.connect(lambda : self.set_profile_pic(False))
        self.load_user_profile()
        self.buttonChange.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonChange), self.change_profile_details()))
        self.lineEmail.setEnabled(False)
        self.linePassword.setEnabled(False)
        self.lineFname.setEnabled(False)
        self.lineLname.setEnabled(False)
        self.linePnumber.setEnabled(False)
        self.buttonDelete.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonDelete), self.delete_account()))
        self.buttonDeleteAllSubs.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonDeleteAllSubs), self.delete_subs()))
        self.buttonLogOut.clicked.connect(lambda: (windowLogin.play_click(), self.log_out()))
        
            #Income:
        self.buttonIncomeSubmit.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonIncomeSubmit), self.check_Income_inputs()))
        self.labelExceptionIncome.setVisible(False)

            #Categories:
        self.buttonCategorySubmit.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonCategorySubmit), self.addCategory()))
        #self.reset_combo_source()
        
        self.update_list_view_category()

            #Cost:
        self.buttonCostSubmit.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonCostSubmit), self.check_Cost_inputs()))
        self.labelExceptionCost.setVisible(False)

            #back buttons:
        self.buttonBackFromIncome.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_MainMenu()))
        self.buttonBackFromCategories.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_MainMenu()))
        self.buttonBackFromProfile.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_MainMenu()))
        self.buttonBackFromSettings.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_MainMenu()))
        self.buttonBackFromCosts.clicked.connect(lambda: (windowLogin.play_click(), self.go_to_MainMenu()))
        self.buttonBackFromSearch.clicked.connect(lambda: (windowLogin.play_click(),self.go_to_MainMenu()))
        self.buttonBackFromReports.clicked.connect(lambda: (windowLogin.play_click(),self.go_to_MainMenu()))

            #Report:
        if self.username:
            self.load_incomes()
            self.load_costs()
            self.buttonProfile.click()
            self.buttonBackFromProfile.click()

        self.buttonReportsSubmit.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonReportsSubmit), self.perform_reports()))
        self.buttonGroupReports = QButtonGroup()
        self.buttonGroupReports.addButton(self.radioReportsPastD)
        self.buttonGroupReports.addButton(self.radioReportsPastM)
        self.buttonGroupReports.addButton(self.radioReportsPastY)
        self.buttonGroupReports.addButton(self.radioReportsNone)
        self.radioReportsNone.setChecked(True)
        self.buttonReportsRange.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonReportsRange), self.get_integer_values2()))
        self.buttonReportsReset.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonReportsReset), self.reset_reports()))
        self.first_range1 = 0
        self.second_range2 = 0

            #Search:
        self.buttonSearchSubmit.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonSearchSubmit), self.begin_search()))
        self.buttonGroupSearch1 = QButtonGroup()
        self.buttonGroupSearch1.addButton(self.radioSearchIncomesOnly)
        self.buttonGroupSearch1.addButton(self.radioSearchCostsOnly)
        self.buttonGroupSearch1.addButton(self.radioSearchNone1)
        self.radioSearchNone1.setChecked(True)
        self.buttonGroupSearch2 = QButtonGroup()
        self.buttonGroupSearch2.addButton(self.radioSearchPast1)
        self.buttonGroupSearch2.addButton(self.radioSearchPast3)
        self.buttonGroupSearch2.addButton(self.radioSearchNone2)
        self.radioSearchNone2.setChecked(True)
        self.buttonSearchRange.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonSearchRange), self.get_integer_values()))
        self.buttonSearchReset.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonSearchReset), self.reset_search()))
        self.firt_range = 0
        self.second_range = 0

            #setting:
        self.buttonMute.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonMute), windowLogin.play_mute_background()))
        self.sliderVolume.valueChanged.connect(self.update_volume)
        self.buttonChangeTheme.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonChangeTheme), self.change_theme()))
        self.buttonAbout.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonAbout),self.show_message_about()))
        self.buttonDonate.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonDonate), self.open_link_donation()))
        self.buttonInstagram.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonInstagram), self.open_link_instagram()))
        self.buttonTelegram.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonTelegram), self.open_link_telegram()))
        self.buttonTwitter.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonTwitter), self.open_link_twitter()))
        self.buttonReportBug.clicked.connect(lambda: (windowLogin.play_click(), self.animate_button(self.buttonReportBug), self.open_link_bug()))
        #self.tabWidget.tabBar().hide()
        
        #exception handling:
        self.labelExceptionCategory.setVisible(False)
        self.labelExceptionProfile.setVisible(False)

    #reinitialize the class
    def reinit(self):
        self.__init__()

    def animate_button(self, bname):
        # Disable the button to prevent multiple rapid clicks
        bname.setEnabled(False)

        original_rect = bname.geometry()
        larger_rect = original_rect.adjusted(-10, -10, 10, 10)
        
        pop_animation = QSequentialAnimationGroup(self)
        
        grow_animation = QPropertyAnimation(bname, b"geometry")
        grow_animation.setDuration(150)
        grow_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        grow_animation.setStartValue(original_rect)
        grow_animation.setEndValue(larger_rect)

        shrink_animation = QPropertyAnimation(bname, b"geometry")
        shrink_animation.setDuration(150)
        shrink_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        shrink_animation.setStartValue(larger_rect)
        shrink_animation.setEndValue(original_rect)
        
        pop_animation.addAnimation(grow_animation)
        pop_animation.addAnimation(shrink_animation)

        # Re-enable the button after the animation finishes
        pop_animation.finished.connect(lambda: bname.setEnabled(True))
        
        pop_animation.start()

    def online_time(self):
        self.logout_time = datetime.now()
        onlinetime = self.logout_time - self.login_time
        total_seconds = int(onlinetime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Print the time difference in the format HH:MM:SS
        QMessageBox.information(None, "online time", f" online time: \n {hours:02}:{minutes:02}:{seconds:02}")


    #profile tab:
    def load_user_profile(self):
        try:
            database_path = project_path + '//database//members_info.db'
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            string = cursor.execute("SELECT * FROM members_info WHERE username=?", (self.username,))
            info = cursor.fetchone()
            conn.close()

            self.email = str(info[5])
            self.password = str(info[6])
            self.fname = str(info[1])
            self.lname = str(info[2])
            self.pnumber = str(info[3])
            self.pfp_path = str(info[11])
            self.theme_name = str(info[12])
            self.labelLogo.setText('Hello,\n ' + self.fname + ' !')

            if self.pfp_path:
                self.set_profile_pic(True)

            if self.theme_name:
                self.load_theme()

            self.lineEmail.setText(self.email)
            self.linePassword.setText(self.password)
            self.lineUsername.setText(self.username)
            self.lineFname.setText(self.fname)
            self.lineLname.setText(self.lname)
            self.linePnumber.setText(self.pnumber)
        except TypeError:
            pass
    
    def load_theme(self):
        self.change_theme(self.theme_name)


    def set_profile_pic(self, isCostume = False):
        profile_name = self.comboProfiles.currentText()
        profile_path = project_path + '//resources//' + profile_name + '.jpg'

        if isCostume:
            try:
                profile_path = self.pfp_path
            except:
                pass

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET profile_pic = ? WHERE username = ?", (profile_path, self.username))
        conn.commit()
        conn.close()

        pixmap = QPixmap(profile_path)
        scaled_pixmap = pixmap.scaled(self.labelProfilePic.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.labelProfilePic.setPixmap(scaled_pixmap)
        self.labelProfilePic2.setPixmap(scaled_pixmap)
        self.labelProfilePic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelProfilePic2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def open_file_dialog(self):
        self.pfp_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'All Files (*)')
        if self.pfp_path:
            self.set_profile_pic(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_profile_pic(True)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.pfp_path = urls[0].toLocalFile()
            self.set_profile_pic(True)

    def change_profile_details(self):
        if self.buttonChange.text() == 'Change':
            #change
            self.lineEmail.setEnabled(True)
            self.linePassword.setEnabled(True)
            self.lineFname.setEnabled(True)
            self.lineLname.setEnabled(True)
            self.linePnumber.setEnabled(True)
            self.buttonChange.setText('Submit')
        else:
            #submit
            self.lineEmail.setEnabled(False)
            self.linePassword.setEnabled(False)
            self.lineFname.setEnabled(False)
            self.lineLname.setEnabled(False)
            self.linePnumber.setEnabled(False)
            self.buttonChange.setText('Change')
            self.check_changed_details()

    def check_changed_details(self):
        new_email = self.lineEmail.text()
        new_password = self.linePassword.text()
        new_fname = self.lineFname.text()
        new_lname = self.lineLname.text()
        new_pnumber = self.linePnumber.text()
        valid_email = r'^[a-zA-Z0-9._%+-]+@(gmail|yahoo)\.com$'
        valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        valid_pnumber = r'^09\d{9}$'
        valid_fname = r'^[a-zA-Z ]+$'
        valid_lname = r'^[a-zA-Z ]+$'
        self.labelExceptionProfile.setText('')
        database_path = project_path + '//database//members_info.db'
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members_info WHERE email=?", (new_email,))
        results = cursor.fetchone()
        conn.close()
        if new_email != self.email:
            if re.match(valid_email, new_email):
                if results:
                    self.labelExceptionProfile.setVisible(True)
                    self.labelExceptionProfile.setText('email already in use')
                else:
                    self.labelExceptionProfile.setVisible(False)
                    self.labelExceptionProfile.setText('')
                    self.save_changed_email(new_email)
        
        if new_password != self.password:
            if re.match(valid_password, new_password):
                self.labelExceptionProfile.setVisible(False)
                self.labelExceptionProfile.setText('')
                self.save_changed_password(new_password)

            else:
                self.labelExceptionProfile.setVisible(True)
                self.labelExceptionProfile.setText(str(self.labelExceptionProfile.text()) + ' invalid password')

        if new_fname != self.fname:
            if re.match(valid_fname, new_fname):
                self.labelExceptionProfile.setVisible(False)
                self.labelExceptionProfile.setText('')
                self.save_changed_fname(new_fname)
            else:
                self.labelExceptionProfile.setVisible(True)
                self.labelExceptionProfile.setText(str(self.labelExceptionProfile.text()) + ' invalid fname')
        
        if new_lname != self.lname:
            if re.match(valid_lname, new_lname):
                self.labelExceptionProfile.setVisible(False)
                self.labelExceptionProfile.setText('')
                self.save_changed_lname(new_lname)
            else:
                self.labelExceptionProfile.setVisible(True)
                self.labelExceptionProfile.setText(str(self.labelExceptionProfile.text()) + ' invalid lname')
        
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members_info WHERE phone_number=?", (new_pnumber,))
        results = cursor.fetchone()
        conn.close()

        if new_pnumber != self.pnumber:
            if re.match(valid_pnumber, new_pnumber):
                if results:
                    self.labelExceptionProfile.setVisible(True)
                    self.labelExceptionProfile.setText(str(self.labelExceptionProfile.text()) + ' phone number already in use')
                else:
                    self.labelExceptionProfile.setVisible(False)
                    self.labelExceptionProfile.setText('')
                    self.save_changed_pnumber(new_email)

        if self.labelExceptionProfile.text():
            windowLogin.play_wrong()
        self.load_user_profile()

    def save_changed_email(self, new_email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET email = ? WHERE username = ?", (new_email, self.username))
        conn.commit()

    def save_changed_password(self, new_password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET password = ? WHERE username = ?", (new_password, self.username))
        conn.commit()

    def save_changed_fname(self, new_fname):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET first_name = ? WHERE username = ?", (new_fname, self.username))
        conn.commit()

    def save_changed_lname(self, new_lname):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET last_name = ? WHERE username = ?", (new_lname, self.username))
        conn.commit()

    def save_changed_pnumber(self, new_pnumber):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE members_info SET phone_number = ? WHERE username = ?", (new_pnumber, self.username))
        conn.commit()

    def delete_account(self):
        reply = QMessageBox.question(
            self, "Delete Account", f"Are you sure you want to delete this account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            #Delete user from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members_info WHERE username = ?", (self.username,))
            conn.commit()
            conn.close()
            
            #Delete user's folder
            user_folder_path = project_path + '//database//reports//' + self.username
            if os.path.isdir(user_folder_path):
                shutil.rmtree(user_folder_path)

            #Close current window and show login window
            windowMain.close()
            windowLogin.show()
        
    def delete_subs(self):
        reply = QMessageBox.question(
        self, "Delete submissions", f"Are you sure you want to delete all the submissions ?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.user_folder_path = project_path + '//database//reports//' + self.username
            if os.path.isdir(self.user_folder_path):
                shutil.rmtree(self.user_folder_path)
                os_directory_path = self.user_folder_path
                os.makedirs(os_directory_path, exist_ok=True)
                self.make_incomes_table()
                self.make_costs_table()
                self.make_categories_table()
                self.reset_combo_source()
                self.update_list_view_reports([],0)
                self.update_list_view_category(0)

    def ensure_user_folder_exists(self):
        if not os.path.exists(self.user_folder_path):
            os.makedirs(self.user_folder_path)

    def make_incomes_table(self):
        conn = sqlite3.connect(self.incomes_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Income REAL,
                Date TEXT,
                Source TEXT,
                Details TEXT,
                Type TEXT,
                submit_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def make_costs_table(self):
        conn = sqlite3.connect(self.costs_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Cost REAL,
                Date TEXT,
                Source TEXT,
                Details TEXT,
                Type TEXT,
                submit_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def make_categories_table(self):
        conn = sqlite3.connect(self.categories_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Categories TEXT,
                submit_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def reset_combo_source(self, user_items = []):
        default_items = ['Groceries', 'Refueling', 'Decorations', 'Installment'] + user_items
        print(default_items)
        self.comboIncomeSource.clear()
        self.comboIncomeSource.addItems(default_items)
        self.comboIncomeSource.setCurrentIndex(0)
        self.comboCostSource.clear()
        self.comboCostSource.addItems(default_items)
        self.comboCostSource.setCurrentIndex(0)
        self.comboReportsSource.clear()
        self.comboReportsSource.addItems(default_items)
        self.comboReportsSource.setCurrentIndex(0)

    def load_combo_source(self):
        import sqlite3

        conn = sqlite3.connect(self.categories_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Categories FROM Categories")
        rows = cursor.fetchall()
        self.user_items = [row[0] for row in rows]
        conn.close()
        print(self.user_items)

        if self.username and self.user_items:
            self.reset_combo_source(self.user_items)

        
    def log_out(self):
        windowMain.close()
        windowLogin.show()

    #main menu tab:
    def go_to_MainMenu(self):
        self.tabWidget.setCurrentIndex(0)

    def go_to_IncomeTab(self):
        self.tabWidget.setCurrentIndex(1)

    def go_to_CostsTab(self):
        self.tabWidget.setCurrentIndex(2)
    
    def go_to_SearchTab(self):
        self.tabWidget.setCurrentIndex(3)
    
    def go_to_CategoriesTab(self):
        self.tabWidget.setCurrentIndex(4)
    
    def go_to_ReportsTab(self):
        self.tabWidget.setCurrentIndex(5)

    def go_to_SettingsTab(self):
        self.tabWidget.setCurrentIndex(6)
    
    def go_to_ProfileTab(self):
        self.tabWidget.setCurrentIndex(7)

    #income tab:
    def reset_Income_inputs(self):
        self.lineIncome.setText('')
        self.lineIncomeDate.setText('')
        self.lineIncomeDetails.setText('')
        self.lineIncomeSource.setText('')
    
    def check_Income_inputs(self):
        if self.check_Income() == False:
            windowLogin.play_wrong()
            self.labelExceptionIncome.setVisible(True)
            self.labelExceptionIncome.setText('invalid input for income')
            return
        else:
            self.labelExceptionIncome.setVisible(False)
            self.labelExceptionIncome.setText('')
        if self.check_Income_Date() == False:
            windowLogin.play_wrong()
            self.labelExceptionIncome.setVisible(True)
            self.labelExceptionIncome.setText('invalid date')
            return
        else:
            self.labelExceptionIncome.setVisible(False)
            self.labelExceptionIncome.setText('')

        self.submit('income')

    def check_Income(self):
        valid_Income = r'^\d+(\.\d+)?$'
        if re.match(valid_Income, self.lineIncome.text()):   
            return True
        else:
            return False

    def check_Income_Date(self):
        self.incomeDate = self.dateIncome.date().toString("yyyy/MM/dd")
        return True

    #Cost tab:
    def check_Cost_inputs(self):
        if self.check_Cost() == False:
            windowLogin.play_wrong()
            self.labelExceptionCost.setVisible(True)
            self.labelExceptionCost.setText('invalid input for cost')    
            return
        else:
            self.labelExceptionCost.setVisible(False)
            self.labelExceptionCost.setText('') 
        if self.check_Cost_Date() == False:
            windowLogin.play_wrong()
            self.labelExceptionCost.setVisible(True)
            self.labelExceptionCost.setText('invalid date') 
            return
        else:
            self.labelExceptionCost.setVisible(False)
            self.labelExceptionCost.setText('') 

        self.submit('cost')

    def check_Cost(self):
        valid_Cost = r'^\d+(\.\d+)?$'
        if re.match(valid_Cost, self.lineCost.text()):
            return True
        else:
            return False

    def check_Cost_Date(self):
        self.costDate = self.dateCost.date().toString("yyyy/MM/dd")
        return True

    #Submiting:
    def submit(self, Type):
        current_time = time.localtime()
        self.current_time = time.strftime('%Y/%m/%d', current_time)

        if Type == 'income':
            self.Income = self.lineIncome.text()
            self.IncomeDate = self.incomeDate
            self.IncomeSource = self.comboIncomeSource.currentText()
            self.IncomeDetails = self.lineIncomeDetails.text()
            self.IncomeType = self.comboIncomeType.currentText()

            conn = sqlite3.connect(self.incomes_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Incomes (Income, Date, Source, Details, Type, submit_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.Income, self.IncomeDate, self.IncomeSource, self.IncomeDetails, self.IncomeType, self.current_time))
            conn.commit()
            conn.close()

        elif Type == 'cost':
            self.Cost = self.lineCost.text()
            self.CostDate = self.costDate
            self.CostSource = self.comboCostSource.currentText()
            self.CostDetails = self.lineCostDetails.text()
            self.CostType = self.comboCostType.currentText()

            conn = sqlite3.connect(self.costs_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Costs (Cost, Date, Source, Details, Type, submit_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.Cost, self.CostDate, self.CostSource, self.CostDetails, self.CostType, self.current_time))
            conn.commit()
            conn.close()

        elif Type == 'category':
            category = self.lineNewCategory.text()
            self.new_category = category.capitalize()

            conn = sqlite3.connect(self.categories_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Categories (Categories, submit_date)
                VALUES (?, ?)
            ''', (self.new_category, self.current_time))
            conn.commit()
            conn.close()

        else:
            self.show_message_unsuccessful()
            return

        mod_info = {
            "Income": self.Income if Type == 'income' else None,
            "Cost": self.Cost if Type == 'cost' else None,
            "Category": self.new_category if Type == 'category' else None,
            "Date": self.IncomeDate if Type == 'income' else (self.CostDate if Type == 'cost' else None),
            "Source": self.IncomeSource if Type == 'income' else (self.CostSource if Type == 'cost' else None),
            "Details": self.IncomeDetails if Type == 'income' else (self.CostDetails if Type == 'cost' else None),
            "Type": self.IncomeType if Type == 'income' else (self.CostType if Type == 'cost' else None),
            "submit date": self.current_time
        }

        mod_info_str = "\n".join(f"{key}: {value}" for key, value in mod_info.items() if value is not None)
        self.update_list_view_reports(mod_info_str)
        self.show_message_successful()
        self.reset_inputs()

    def show_message_successful(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle('Success')
        msg_box.setText('submission was successful')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_message_unsuccessful(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle('Error')
        msg_box.setText('submission was unsuccessful')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def reset_inputs(self):
            self.lineIncome.setText('')
            self.lineIncomeDetails.setText('')
            self.dateIncome.setDate(QDate.currentDate())
            self.lineCost.setText('')
            self.dateCost.setDate(QDate.currentDate())
            self.lineCostDetails.setText('')

    #search tab:
    def begin_search(self):
        self.perform_search()

    def reset_search(self):
        self.radioSearchNone1.setChecked(True)
        self.radioSearchNone2.setChecked(True)
        self.first_range = 0
        self.second_range = 0
        self.labelSearchRange.setText('Range')

    def get_integer_values(self):
        # First dialog
        first_value, ok1 = QInputDialog.getInt(None, "Input Dialog", "Enter first integer value:")
        if not ok1:
            QMessageBox.critical(None, "Error", "First input was cancelled.")
            return
        
        while True:
            # Second dialog
            second_value, ok2 = QInputDialog.getInt(None, "Input Dialog", "Enter second integer value:")
            if not ok2:
                QMessageBox.critical(None, "Error", "Second input was cancelled.")
                return
            
            if second_value > first_value:
                break
            else:
                QMessageBox.warning(None, "Input Error", "Second value must be greater than the first value. Please try again.")
        
        self.labelSearchRange.setText('range: ' + str(first_value) + ' - ' + str(second_value))
        self.first_range = first_value
        self.second_range = second_value

    def perform_search(self):
        self.model_3.setStringList([''])
        self.results_combined = []

        #None1,None2
        if self.radioSearchNone1.isChecked() and self.radioSearchNone2.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path)
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path)
        
        #None1,Past 24 hours
        if self.radioSearchNone1.isChecked() and self.radioSearchPast1.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path, 1)
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path, 1)

        #None1,Past 3 days
        if self.radioSearchNone1.isChecked() and self.radioSearchPast3.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path, 3)
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path, 3)

        #IncomesOnly,None2
        if self.radioSearchIncomesOnly.isChecked() and self.radioSearchNone2.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path)

        #IncomesOnly, Past 24 hours
        if self.radioSearchIncomesOnly.isChecked() and self.radioSearchPast1.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path, 1)
        
        #IncomesOnly, Past 3 days
        if self.radioSearchIncomesOnly.isChecked() and self.radioSearchPast3.isChecked():
            if os.path.exists(self.incomes_db_path):
                self.Search(self.incomes_db_path, 3)

        #CostsOnly, None2
        if self.radioSearchCostsOnly.isChecked() and self.radioSearchNone2.isChecked():
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path)

        #CostsOnly, Past 24 hours
        if self.radioSearchCostsOnly.isChecked() and self.radioSearchPast1.isChecked():
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path, 1)

        #CostsOnly, Past 3 days
        if self.radioSearchCostsOnly.isChecked() and self.radioSearchPast3.isChecked():
            if os.path.exists(self.costs_db_path):
                self.Search(self.costs_db_path, 3)
        
        self.update_list_view_search(self.results_combined)

    def Search(self, file_path, time_range = ''):
        searched_string = self.lineSearch.text()
        result = []
        if searched_string:
            #search the key word:
            result = self.search_in_database(file_path, searched_string)
            if result:
                self.result_display = []
                new_results = []

                #check if it's withing the past 24 hours:
                if time_range == 1:
                    for i in range(len(result)):
                        current_time_str = result[i][1].strip("'Date: ")
                        valid_format = r'^\d{4}/\d{2}/\d{2}$'
                        if re.match(valid_format, current_time_str):
                            if self.is_within_past_days(current_time_str, 3):
                                new_results.append(result[i])
                    result = new_results

                #check if it's withing the past 3 days:
                elif time_range == 3:
                    for i in range(len(result)):
                        current_time_str = result[i][1].strip("'Date: ")
                        valid_format = r'^\d{4}/\d{2}/\d{2}$'
                        if re.match(valid_format, current_time_str):
                            if self.is_within_past_days(current_time_str, 3):
                                new_results.append(result[i])
                    result = new_results
                
                #money range check:
                if self.second_range > 0:
                    for i in range(len(result)):
                        money = result[i][0].strip("'Income: ").strip("'Cost: ")
                        valid_number = r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$'
                        if re.match(valid_number, money):
                            if self.is_within_range(int(float(money))):
                                new_results.append(result[i])
                    result = new_results
                new_results = []

                #if it's empty don't display, if not add \n to every element:
                if len(result) > 0:
                    for i in result:
                        new_results.append(i)
                        new_results.append('--------------------------------------')
                    result = new_results
                    self.result_display.append("\n".join([str(row) for row in result]))
                    self.results_combined.append(self.result_display)

    def is_within_range(self, money):
        return self.first_range < money < self.second_range

    def is_within_past_days(self, date_str, past_days):
        #Convert string to datetime object
        
        date_obj = datetime.strptime(date_str, "%Y/%m/%d")
        
        #Get current time
        current_time = datetime.now()
        
        # Calculate difference
        difference = current_time - date_obj
        
        # Define timedelta for x days
        Days = timedelta(days = past_days)

        # Check if difference is less than x days
        return difference < Days

    def search_in_database(self, db_path, search_string):
        search_string = f"%{search_string}%"
        results = []

        def search_table(conn, table_name):
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            query = f"SELECT * FROM {table_name} WHERE " + " OR ".join([f"{column} LIKE ?" for column in columns])
            cursor.execute(query, [search_string] * len(columns))
            rows = cursor.fetchall()
            if rows:
                column_headers = [description[0] for description in cursor.description]
                for row in rows:
                    results.append([f"{column_headers[i]}: {cell}" for i, cell in enumerate(row)])
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            search_table(conn, table[0])

        conn.close()
        return results

    def update_list_view_search(self, List):
        string_list = self.model_3.stringList()
        for i in List:
            for j in i:
                string_list.append(str(j).replace("'", "").replace('[','').replace(']','').replace(',','\n'))
        self.model_3.setStringList(string_list)

    #Categories tab:
    def addCategory(self):
        Category = self.lineNewCategory.text()
        valid_category = r'^[a-zA-Z ]+$'
        if Category.isalpha() and len(Category) <= 15:
            New_Category = Category.capitalize()
        else:
            self.labelExceptionCategory.setVisible(True)
            self.labelExceptionCategory.setText('invalid Category')
            return
        if re.match(valid_category , New_Category):
            if self.comboIncomeSource.findText(New_Category) == -1:
                self.comboIncomeSource.addItem(New_Category)
                self.comboCostSource.addItem(New_Category)
                self.submit('category')
                self.lineNewCategory.setText('')
                self.update_list_view_category()
                self.labelExceptionCategory.setVisible(False)
                self.labelExceptionCategory.setText('')
                return
            else:
                self.labelExceptionCategory.setVisible(True)
                self.labelExceptionCategory.setText('Category already exists!')
                return
        else:
            self.labelExceptionCategory.setVisible(True)
            self.labelExceptionCategory.setText('only English characters are acceptable')
            return 
    
    def update_list_view_category(self, code = 1):
        #code 0 is for clearing the view list
        if code == 0:
            self.model.setStringList([])
        else:
            items = [self.comboIncomeSource.itemText(i) for i in range(self.comboIncomeSource.count())]
            items2 = [self.comboReportsSource.itemText(i) for i in range(self.comboReportsSource.count())]
            print(items2)
            self.model.setStringList(items)
            new_items = []
            default_items = ['Groceries', 'Refueling', 'Decorations', 'Installment']
            for i in items:
                if i in default_items or i in items2:
                    pass
                else:
                    new_items.append(i)
            items = new_items
            self.comboReportsSource.addItems(items)

    #reports tab:
    def reset_reports(self):
        self.radioReportsNone.setChecked(True)
        self.labelReportsRange.setText('')
        self.first_range2 = 0
        self.second_range2 = 0
        self.comboReportsType.setCurrentText('Type(none)')
        self.comboReportsSource.setCurrentText('Source(none)')
        self.labelReportsRange.setText('Range')

    def update_list_view_reports(self, info, code = 1):
        if code == 0:
            self.model_2.setStringList([])
        else:
            string_list = self.model_2.stringList()
            string_list.append(info)
            string_list.append('--------------------------------------')
            self.model_2.setStringList(string_list)

    def load_incomes(self):
        db_path = project_path + f"//database//reports//{self.username}//Incomes.db"
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(self.incomes_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Incomes")
            incomes_list = cursor.fetchall()
            column_headers = [description[0] for description in cursor.description]
            conn.close()

            for income in incomes_list:
                info = {
                    "Income": income[1],
                    "Date": income[2],
                    "Source": income[3],
                    "Details": income[4],
                    "Type": income[5],
                    "submit date": income[6]
                }
                mod_info = "\n".join(f"{key}: {value}" for key, value in info.items())
                self.update_list_view_reports(mod_info)
        else:
            return

    def load_costs(self):
        db_path = project_path + f"//database//reports//{self.username}//Costs.db"
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(self.costs_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Costs")
            costs_list = cursor.fetchall()
            column_headers = [description[0] for description in cursor.description]
            conn.close()

            for cost in costs_list:
                info = {
                    "Cost": cost[1],
                    "Date": cost[2],
                    "Source": cost[3],
                    "Details": cost[4],
                    "Type": cost[5],
                    "submit date": cost[6]
                }
                mod_info = "\n".join(f"{key}: {value}" for key, value in info.items())
                self.update_list_view_reports(mod_info)
                
        else:
            return

    def get_integer_values2(self):
        first_value, ok1 = QInputDialog.getInt(None, "Input Dialog", "Enter first integer value:")
        if not ok1:
            QMessageBox.critical(None, "Error", "First input was cancelled.")
            return
        
        while True:
            # Second dialog
            second_value, ok2 = QInputDialog.getInt(None, "Input Dialog", "Enter second integer value:")
            if not ok2:
                QMessageBox.critical(None, "Error", "Second input was cancelled.")
                return
            
            if second_value > first_value:
                break
            else:
                QMessageBox.warning(None, "Input Error", "Second value must be greater than the first value. Please try again.")
        
        self.labelReportsRange.setText('range: ' + str(first_value) + ' - ' + str(second_value))
        self.first_range2 = first_value
        self.second_range2 = second_value

    def perform_reports(self):

        self.model_2.setStringList([''])
        self.results_combined = []

        if self.radioReportsNone.isChecked():
            self.filter_reports(self.incomes_db_path)
            self.filter_reports(self.costs_db_path)

        if self.radioReportsPastD.isChecked():
            self.filter_reports(self.incomes_db_path,'D')
            self.filter_reports(self.costs_db_path,'D')

        if self.radioReportsPastM.isChecked():
            self.filter_reports(self.incomes_db_path,'M')
            self.filter_reports(self.costs_db_path,'M')

        if self.radioReportsPastY.isChecked():
            self.filter_reports(self.incomes_db_path,'Y')
            self.filter_reports(self.costs_db_path,'Y')

        self.update_list_view_reports_filtered(self.results_combined)
        
    def filter_reports(self, file_path, time_range = ''):
        result = []
        searched_string = ''
        if self.comboReportsSource.currentText() != 'Source(none)':
            searched_string = self.comboReportsSource.currentText()

        if searched_string:
            result = self.search_in_database(file_path, searched_string)
        else:
            result = self.read_db_to_list(file_path)

        if result:
            self.result_display = []
            new_results = []
        
            if time_range == 'D':
                for i in range(len(result)):
                    current_time_str = result[i][2].strip("'Date: ")
                    if self.is_within_past_days(current_time_str, 1):
                        new_results.append(result[i])
                result = new_results
            elif time_range == 'M':
                for i in range(len(result)):
                    current_time_str = result[i][2].strip("'Date: ")
                    if self.is_within_past_days(current_time_str, 30):
                        new_results.append(result[i])
                result = new_results
            elif time_range == 'Y':
                for i in range(len(result)):
                    current_time_str = result[i][2].strip("'Date: ")
                    if self.is_within_past_days(current_time_str, 365):
                        new_results.append(result[i])
                result = new_results
            
            new_results = []
            if self.second_range2 > 0:
                for i in range(len(result)):
                    money = result[i][1].strip("'Income: ").strip("'Cost: ")
                    if self.is_within_range2(int(float(money))):
                        new_results.append(result[i])
                result = new_results
            
            new_results = []
            if self.comboReportsType.currentText() != 'Type(none)':
                Type = self.comboReportsType.currentText()
                for i in range(len(result)):
                    if Type in result[i][5]:
                        new_results.append(result[i])
                result = new_results
            new_results = []

            if len(result) > 0:
                for i in result:
                    new_results.append(i)
                    new_results.append('--------------------------------------')
                result = new_results
                self.result_display.append("\n".join([str(row) for row in result]))
                self.results_combined.append(self.result_display)

    def read_db_to_list(self, db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                print("No tables found in the database.")
                return None
            table_name = tables[0][0]

            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()

            data = []
            for row in rows:
                row_list = [f"{columns[i]}: {cell}" for i, cell in enumerate(row)]
                data.append(row_list)
            conn.close()
            return data
        except Exception as e:
            print(f"Error reading database: {e}")
            return None

    def is_within_range2(self, money):
        return self.first_range1 < money < self.second_range2

    def update_list_view_reports_filtered(self, List):
        string_list = self.model_2.stringList()
        for i in List:
            for j in i:
                string_list.append(str(j).replace("'", "").replace('[','').replace(']','').replace(',','\n'))
        self.model_2.setStringList(string_list)

    #settings:
    def change_theme(self, user_theme = ''):
        if user_theme == '':
            if self.star_theme_on:
                self.light_theme_on = True
                self.star_theme_on = False
                path = light_theme_path
                self.theme_name = 'Light'
                self.labelTheme.setText('Light')

            elif self.light_theme_on:
                self.light_theme_on = False
                self.dark_theme_on = True
                path = dark_theme_path
                self.theme_name = 'Dark'
                self.labelTheme.setText('Dark')

            elif self.dark_theme_on:
                self.star_theme_on = True
                self.dark_theme_on = False
                path = star_theme_path
                self.theme_name = 'Stars'
                self.labelTheme.setText('Stars')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE members_info SET theme = ? WHERE username = ?", (self.theme_name, self.username))
            conn.commit()
        else:
            if user_theme == 'Dark':
                path = dark_theme_path
                self.labelTheme.setText('Dark')

            elif user_theme == 'Light':
                path = light_theme_path
                self.labelTheme.setText('Light')

            else :
                path = star_theme_path
                self.labelTheme.setText('Star')


        self.labelPic.setStyleSheet(path)
        
    def show_message_about(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle('About')
        msg_box.setText('made by Erfan Ghasemian and Arian Saeed Kondori')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def update_volume(self, value):
        self.labelVolumeLevel.setText("Volume: " + str(value))
        backgroundSound.soundtrack.setVolume(value / 100.0)

    def open_link_donation(self):
        QDesktopServices.openUrl(QUrl('https://developer.paypal.com/'))

    def open_link_instagram(self):
        QDesktopServices.openUrl(QUrl('https://www.instagram.com/'))
    
    def open_link_telegram(self):
        QDesktopServices.openUrl(QUrl('https://telegram.org/'))
    
    def open_link_twitter(self):
        QDesktopServices.openUrl(QUrl('https://twitter.com/'))
    
    def open_link_bug(sefl):
        QDesktopServices.openUrl(QUrl('https://github.com/Arian-SK/Personal-Accounting-App'))


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
        self.labelPic.setStyleSheet(star_theme_path)
        self.labelPic.lower()
        
        #exception handling label:
        self.labelException.setVisible(False)

        #signal handling:
        self.buttonSignUp.clicked.connect(lambda: (windowLogin.play_click(), windowMain.animate_button(self.buttonSignUp), self.check()))
        self.buttonLogin.clicked.connect(lambda: (windowLogin.play_click(), self.open_login_page()))
        self.buttonMute.clicked.connect(lambda: (windowLogin.play_click(), windowMain.animate_button(self.buttonMute), windowLogin.play_mute_background()))
        self.lineCity.textChanged.connect(self.change_text)
        self.buttonSignUp.setShortcut("Return")
        self.labelTerms.mousePressEvent = self.open_terms_link

        #attributes:
        self.city_list = ['Tehran', 'ُSari', 'Karaj', 'Babol', 'Esfahan',
         'Shiraz', 'Yazd', 'Tabriz', 'Kerman', 'Qom', 'Mashhad', 'Ahvaz',
          'Zahedan', 'Kashan', 'Arak', 'Zanjan', 'Ardabil', 'Rasht', 'Amirkola',
           'Hamedan', 'Gorgan', 'Eslamshahr', 'Bandar Abbas', 'Oromieh']
        
        #auto completer:
        self.completer = QCompleter(self.city_list)
        self.lineCity.setCompleter(self.completer)

        #sound initilization:
        self.wrong_sound = Sound('Alert')
        self.wrong_sound_isMuted = False
        self.correct_sound = Sound('Correct')
        self.correct_sound_isMuted = False
        self.click_sound = Sound('Click')
        self.click_sound_isMuted = False

        #date:
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDisplayFormat("yyyy/MM/dd")
        self.dateEdit.setMaximumDate(QtCore.QDate(2005, 12, 31))

        #password line:
        self.linePass.textChanged.connect(self.update_labelPassHint)
        self.linePass.focusInEvent = self.on_password_focus_in
        self.linePass.focusOutEvent = self.on_password_focus_out
        self.labelPassHint.setVisible(False)
        self.buttonToggleEcho.clicked.connect(lambda: (windowLogin.play_click(), self.toggle_echo_mode()))
        self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//close eye.ico"))
        
    def change_text(self):
        city = self.lineCity.text()
        new_city = city.capitalize()
        self.lineCity.setText(new_city)

    def open_terms_link(self, *arg, **kwargs):
        QDesktopServices.openUrl(QUrl('https://www.freeprivacypolicy.com/live/ac906b41-df41-4439-b907-5c768138f3fa'))

    def open_login_page(self):
        windowLogin.show()
        windowSignUp.close() 

    def play_wrong(self):
        if self.wrong_sound_isMuted == False:
            self.wrong_sound.Play()
    
    def play_correct(self):
        if self.correct_sound_isMuted == False:
            self.correct_sound.Play()
    
    def play_click(self):
        if self.click_sound_isMuted == False:
            self.click_sound.Play()

    #function to check inputs:
    def check(self):
        self.labelException.setVisible(True)
        if self.check_fname() == False:
            self.play_wrong()
            return
        if self.check_lname() == False:
            self.play_wrong()
            return
        if self.check_pnumber() == False:
            self.play_wrong()
            return
        if self.check_username() == False:
            self.play_wrong()
            return
        if self.check_email() == False:
            self.play_wrong()
            return
        if self.check_password()== False:
            self.play_wrong()
            return
        if self.confirm_password() == False:
            self.play_wrong()
            return
        if self.check_city() == False:
            self.play_wrong()
            return
        if self.check_date() == False:
            self.play_wrong()
            return
        if self.checkBoxTerms.isChecked() == False:
            self.play_wrong()
            self.labelException.setVisible(True)
            self.labelException.setText('you have to agree with our TOS')
            return
        else:
            self.labelException.setText('')
            self.labelException.setVisible(False)
            self.show_message_box()

    def show_message_box(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Choose an Option")
        msg_box.setText("what do you want your security question be:")
        
        option1 = msg_box.addButton("city", QMessageBox.ButtonRole.AcceptRole)
        option2 = msg_box.addButton("pet name", QMessageBox.ButtonRole.AcceptRole)
        option3 = msg_box.addButton("favorite food", QMessageBox.ButtonRole.AcceptRole)

        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        windowLogin.play_click()

        if clicked_button == option1:
            self.show_input_dialog("city")
        elif clicked_button == option2:
            self.show_input_dialog("pet name")
        elif clicked_button == option3:
            self.show_input_dialog("favorite food")

    def show_input_dialog(self, option):
        self.option = option
        self.security_answer, ok = QInputDialog.getText(self, f"Input for {option}", f"Enter something for {option}:")
        if ok and self.security_answer.isalpha():
            self.labelException.setText('')
            self.play_correct()
            self.add_member()
            self.reset_inputs()
            windowSignUp.close()
            windowLogin.show()

    def reset_inputs(self):
        self.lineFname.setText('')
        self.lineLname.setText('')
        self.linePnumber.setText('')
        self.lineEmail.setText('')
        self.linePass.setText('')
        self.lineConfirmPass.setText('')
        self.lineUsername.setText('')
        self.lineCity.setText('')
        self.labelException.setVisible(False)

    def add_member(self):
        # Get data from input fields
        fname = self.lineFname.text()
        lname = self.lineLname.text()
        pnumber = self.linePnumber.text()
        email = self.lineEmail.text()
        password = self.linePass.text()
        username = self.lineUsername.text()
        city = self.lineCity.text()
        date = self.date
        security_answer = self.security_answer
        security_type = self.option
        # Connect to the database (or create it if it doesn't exist)
        database_path = project_path + '//database//members_info.db'
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS members_info (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            first_name TEXT,
                            last_name TEXT,
                            phone_number TEXT UNIQUE,
                            username TEXT UNIQUE,
                            email TEXT UNIQUE,
                            password TEXT,
                            city TEXT,
                            date TEXT,
                            security_type TEXT,
                            security_answer TEXT,
                            profile_pic TEXT,
                            theme TEXT
                        )''')

        # Insert the new member data
        cursor.execute('''INSERT INTO members_info (
                            first_name, last_name, phone_number, username, email, password, city, date, security_type, security_answer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (fname, lname, pnumber, username, email, password, city, date, security_type, security_answer))
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def check_fname(self):
        self.labelException.setVisible(True)
        fname = self.lineFname.text()
        valid_fname = r'^[a-zA-Z ]+$'
        if re.match(valid_fname, fname):
            self.labelException.setVisible(False)
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
        self.labelException.setVisible(True)
        lname = self.lineLname.text()
        valid_lname = r'^[a-zA-Z ]+$'
        if re.match(valid_lname, lname):
            self.labelException.setVisible(False)
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
        self.labelException.setVisible(True)
        if pnumber.startswith('09') and pnumber.isnumeric() and len(pnumber) == 11:
            # Define the path to the SQLite database
            database_path = project_path + '//database//members_info.db'
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            try:
                # Check if the phone number already exists
                cursor.execute("SELECT * FROM members_info WHERE phone_number=?", (pnumber,))
                if not cursor.fetchone():
                    self.labelException.setVisible(False)
                    self.labelException.setText('')
                    self.labelPnumber.setStyleSheet("""
                        background-color:rgba(255, 255, 255, 10%);
                        border-radius: 8px;
                        padding: 5px 15px;
                        border: 1px solid #e0e4e7;
                    """)
                    conn.close()
                    return True
                else:
                    self.labelException.setText('Phone number already exists')
                    self.labelPnumber.setStyleSheet("""
                        background-color:rgba(255, 255, 255, 10%);
                        border-radius: 8px;
                        padding: 5px 15px;
                        border: 1px solid #ff0000;
                    """)
                    conn.close()
                    return False
            except Exception as e:
                print(e)
            finally:
                conn.close()
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
        database_path = project_path + '//database//members_info.db'
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        self.labelException.setVisible(True)
        if re.match(valid_email, email):
            self.labelException.setText('')
            self.labelEmail.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            cursor.execute("SELECT * FROM members_info WHERE email=?", (email,))
            if not cursor.fetchone():
                self.labelException.setVisible(False)
                self.labelException.setText('')
                self.labelEmail.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                conn.close()
                return True
            else:
                self.labelException.setText('email already in use')
                self.labelEmail.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                conn.close()
                return False
        else:
            self.labelException.setText('invalid email')
            self.labelEmail.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    #check for changes in password and see if the condition is met:
    def update_labelPassHint(self):
        password = self.linePass.text()
        conditions = {
            'At least one uppercase letter': bool(re.search(r'[A-Z]', password)),
            'At least one lowercase letter': bool(re.search(r'[a-z]', password)),
            'At least one digit': bool(re.search(r'\d', password)),
            'At least one symbol character': bool(re.search(r'[!@#$%^&*()\-_=+{};:,<.>]', password)),
            'At least 8 characters long': len(password) >= 8
        }

        hint_text = ''
        for condition, met in conditions.items():
            color = 'green' if met else 'gray'
            hint_text += f'<span style="color: {color};">{condition}</span><br>'

        self.labelPassHint.setText(hint_text)
        self.labelPassHint.setVisible(True)

    #clicked on password:
    def on_password_focus_in(self, event):
        self.update_labelPassHint()
        self.labelPassHint.setVisible(True)

    #not clicked:
    def on_password_focus_out(self, event):
        self.labelPassHint.setVisible(False)

    #see/hide password:
    def toggle_echo_mode(self, mode = ''):
        if self.linePass.echoMode() == QLineEdit.EchoMode.Password:
            self.linePass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//open eye.ico"))
        else:
            self.linePass.setEchoMode(QLineEdit.EchoMode.Password)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//close eye.ico"))

        if mode == 'off':
            self.linePass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//open eye.ico"))
        elif mode == 'on':
            self.linePass.setEchoMode(QLineEdit.EchoMode.Password)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//close eye.ico"))
        self.on_password_focus_in(self.event)

    def check_password(self):
        self.labelException.setVisible(True)
        valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        password = self.linePass.text()
        if re.match(valid_password, password):
            self.labelException.setVisible(False)
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
        valid_username = r'^(?=.*[a-zA-Z])[a-zA-Z0-9_]+$'
        database_path = project_path + '//database//members_info.db'
        self.labelException.setVisible(True)
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        if re.match(valid_username, username):
            self.labelException.setText('')
            self.labelUsername.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
        """)
            cursor.execute("SELECT * FROM members_info WHERE username=?", (username,))
            if not cursor.fetchone():
                self.labelException.setVisible(False)
                self.labelException.setText('')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)
                conn.close()
                return True

            else:
                self.labelException.setText('username already taken')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                conn.close()
                return False
        else:
            self.labelException.setText("invalid username")
            self.labelUsername.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            conn.close()
            return False

    def confirm_password(self):
        self.labelException.setVisible(True)
        password = self.linePass.text()
        retyped_password = self.lineConfirmPass.text()
        if retyped_password == password:
            self.labelException.setVisible(False)
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
        self.labelException.setVisible(True)
        city = self.lineCity.text()
        if city in self.city_list:
            self.labelException.setVisible(False)
            self.labelException.setText('')
            self.labelCity.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #e0e4e7;
            """)
            return True
        else:
            self.labelException.setText('invalid city')
            self.labelCity.setStyleSheet("""
            background-color:rgba( 255, 255, 255, 10% );
            border-radius: 8px;
            padding: 5px 15px;
            border: 1px solid #ff0000;
            """)
            return False

    def check_date(self):
        self.date = self.dateEdit.date().toString("yyyy/MM/dd")
        return True

#Login ui:
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        #ui/tile/icon setup:
        uic.loadUi(project_path + "//LoginPage.ui", self)
        self.setWindowIcon(QIcon(project_path + "//resources//login icon.ico"))
        self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
        self.setWindowTitle('Login')

        #username:
        self.username = ''

        #background image setup:
        self.labelPic = QLabel(self)
        self.labelPic.resize(16777215, 16777215)
        self.labelPic.setStyleSheet(star_theme_path)
        self.labelPic.lower()

        #exception handling label:
        self.labelException.setVisible(False)
        self.attempts = 0

        #sound initilization:
        self.wrong_sound = Sound('Alert')
        self.wrong_sound_isMuted = False
        self.correct_sound = Sound('Correct')
        self.correct_sound_isMuted = False
        self.click_sound = Sound('Click')
        self.click_sound_isMuted = False

        #signal handling:
        self.labelPassForgot.mousePressEvent = self.open_passForgot
        self.buttonLogin.clicked.connect(lambda: (windowLogin.play_click(), self.check_login_input()))
        self.buttonSignUp.clicked.connect(lambda: (windowLogin.play_click(),self.open_signUp_page()))
        self.buttonMute.clicked.connect(lambda: (windowLogin.play_click(), self.play_mute_background()))
        self.buttonLogin.setShortcut("Return")
        self.buttonToggleEcho.clicked.connect(lambda: (windowLogin.play_click(), self.toggle_echo_mode()))
        self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//close eye.ico"))

    def reset_inputs(self):
        self.linePassword.setText('')
        self.lineUsername.setText('')

    def play_mute_background(self):
        if backgroundSound.IsMuted():
            backgroundSound.Mute(False)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
            windowSignUp.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
            windowMain.buttonMute.setIcon(QIcon(project_path + "//resources//sound.ico"))
            self.wrong_sound_isMuted = False
            self.correct_sound_isMuted = False
            self.click_sound_isMuted = False
            SignUp.wrong_sound_isMuted = False

        else:
            backgroundSound.Mute(True)
            self.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            windowSignUp.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            windowMain.buttonMute.setIcon(QIcon(project_path + "//resources//mute sound.ico"))
            self.wrong_sound_isMuted = True
            self.correct_sound_isMuted = True
            self.click_sound_isMuted = True
            SignUp.wrong_sound_isMuted = True

    def toggle_echo_mode(self):
        if self.linePassword.echoMode() == QLineEdit.EchoMode.Password:
            self.linePassword.setEchoMode(QLineEdit.EchoMode.Normal)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//open eye.ico"))
        else:
            self.linePassword.setEchoMode(QLineEdit.EchoMode.Password)
            self.buttonToggleEcho.setIcon(QIcon(project_path + "//resources//close eye.ico"))

    def play_wrong(self):
        if self.wrong_sound_isMuted == False:
            self.wrong_sound.Play()
    
    def play_correct(self):
        if self.correct_sound_isMuted == False:
            self.correct_sound.Play()
    
    def play_click(self):
        if self.click_sound_isMuted == False:
            self.click_sound.Play()

    def open_passForgot(self, *arg, **kwargs):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Recovery")
        msg_box.setText("choose a recovery option:")
        
        option1 = msg_box.addButton("send message", QMessageBox.ButtonRole.AcceptRole)
        option2 = msg_box.addButton("ask a question", QMessageBox.ButtonRole.AcceptRole)
        option3 = msg_box.addButton("cancel", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        windowLogin.play_click()

        if clicked_button == option1:
            windowLogin.close()
            windowPassRecovery.show()
        elif clicked_button == option2:
            self.show_message_recovery()
        elif clicked_button == option3:
            return

    def open_signUp_page(self):
        windowSignUp.show()
        windowLogin.close()
    
    def show_message_recovery(self):
        username, ok = QInputDialog.getText(self, 'Username Input', 'Enter username:')
        if not ok:
            return

        if not username:
            QMessageBox.warning(self, 'Input Error', 'Please enter a username.')
            return

        try:
            database_path = project_path + '//database//members_info.db'
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            cursor.execute("SELECT security_type, security_answer FROM members_info WHERE username=?", (username,))
            user_row = cursor.fetchone()
            
            if user_row is None:
                QMessageBox.warning(self, 'Input Error', 'Username not found.')
            else:
                self.username = username
                self.security_type, self.security_answer = user_row
                self.check_security_answer()
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Error accessing database: {e}')
        finally:
            conn.close()

    
    def check_security_answer(self):
        answer, ok = QInputDialog.getText(self, 'Answer Input', 'Enter your answer for ' + str(self.security_type) + ':')
        if not ok:
            return
        while(answer != self.security_answer):
            QMessageBox.warning(self, 'Input Error', 'Invalid answer')
            answer, ok = QInputDialog.getText(self, 'Answer Input', 'Enter your answer for ' + str(self.security_type) + ':')
            if not ok:
                break
        else:
            #welcome admin:
            if self.username == 'erfan' or self.username == 'arian':
                QMessageBox.information(self, "Welcome Message", "Welcome Admin", QMessageBox.StandardButton.Ok)

            self.play_correct()
            windowLogin.close()
            self.reset_inputs()
            windowMain.reinit()
            windowMain.show()
        return

    #function to check inputs:
    def check_login_input(self):
        if self.attempts < 3:
            self.username = self.lineUsername.text()
            self.password = self.linePassword.text()
            valid_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
            if 0 < len(self.username):
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
                self.labelException.setText('empty username')
                self.labelUsername.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #ff0000;
                """)
                self.play_wrong()
                self.lock()
                return

            if re.match(valid_password, self.password):
                self.labelException.setVisible(False)
                self.labelException.setText('')
                self.labelPassword.setStyleSheet("""
                background-color:rgba( 255, 255, 255, 10% );
                border-radius: 8px;
                padding: 5px 15px;
                border: 1px solid #e0e4e7;
                """)

                if self.check_login(self.username, self.password):

                    #welcome admin:
                    if self.username == 'erfan' or self.username == 'arian':
                        QMessageBox.information(self, "Welcome Message", "Welcome Admin", QMessageBox.StandardButton.Ok)

                    self.play_correct()
                    windowLogin.close()
                    self.reset_inputs()
                    windowMain.reinit()
                    windowMain.show()
                else:
                    self.lock()
                    self.play_wrong()
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
                self.play_wrong()
                self.lock()
                return
                
        else:
            self.countdown()

    def check_login(self, username, password):
        try:
            # Define the path to the SQLite database
            database_path = project_path + '//database//members_info.db'
            
            # Connect to the database
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            # Check if the table exists and has the required columns
            cursor.execute("PRAGMA table_info(members_info)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'username' not in columns or 'password' not in columns:
                self.labelException.setVisible(True)
                self.labelException.setText('Corrupted database')
                conn.close()
                return False
            
            # Query the database for the username and password
            cursor.execute("SELECT * FROM members_info WHERE username=? AND password=?", (username, password))
            user_row = cursor.fetchone()
            
            if user_row:
                self.labelException.setText('')
                conn.close()
                return True
            else:
                self.labelException.setVisible(True)
                cursor.execute("SELECT username FROM members_info WHERE username=?", (username,))
                is_string_present = cursor.fetchone() is not None
                if is_string_present:
                    self.labelException.setText('Password is incorrect (forgot your password?)')
                else:
                    self.labelException.setText('Username not found (you may want to sign up)')
                conn.close()
                return False
        except Exception as e:
            print(e)
            return False
            
    def lock(self):
        print(self.attempts)
        self.attempts += 1
        if self.attempts == 3:
            self.labelException.setText("max attempts reached!")
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
        self.labelPic.setStyleSheet(star_theme_path)
        self.labelPic.lower()

        #signal handling:
        self.labelException.setVisible(False)
        self.buttonVia.clicked.connect(lambda: (windowLogin.play_click(), self.send_via()))
        self.buttonBack.clicked.connect(lambda: (windowLogin.play_click(), self.go_back()))
        self.buttonSend.clicked.connect(lambda: (windowLogin.play_click(), self.check()))

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
        database_path = project_path + '//database//members_info.db'
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        self.labelException.setVisible(True)
        pnumber = self.lineInput.text()
        cursor.execute("SELECT * FROM members_info WHERE phone_number=?", (pnumber,))
        if pnumber.isnumeric() == False:
            return False
        else:
            if cursor.fetchone():
                return True
            else:
                return False
        conn.close()

    def check_email(self):
        database_path = project_path + '//database//members_info.db'
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        email = self.lineInput.text()
        cursor.execute("SELECT * FROM members_info WHERE email=?", (email,))
        if cursor.fetchone():
            return True
        else:
            return False
        conn.close()

    def go_back(self):
        windowPassRecovery.close()
        windowLogin.show()

#main:
if __name__ == '__main__':
    app = QApplication(sys.argv)

    #background music initialization:
    backgroundSound = Sound('background music')
    backgroundSound.SetLoop(-2)
    backgroundSound.Play()

    #define windows:
    windowLogin = LoginPage()
    windowMain = MainApp()
    windowSignUp = SignUp()
    windowPassRecovery = PassRecovery()
    
    #show window(s):
    windowLogin.show()
    #windowMain.show()

    #exit:
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing App...')