from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QDialog, QMessageBox, QMainWindow, QApplication
from PySide2.QtGui import QIcon, QPixmap
# from mainwindow import Ui_MainWindow
import robinhoodBot as r
import robin_stocks.helper as helper
import robin_stocks.authentication as auth
import robin_stocks.urls as urls
import pickle
import getpass
import os
import keyring as k
import sys
#MFA Verification Code
class MFACode(QDialog):
    def __init__(self, data, url, payload, sess_data, parent=None):
        super(MFACode, self).__init__(parent)
        self.code = QLineEdit(self)
        self.code.setPlaceholderText("MFA Verification Code")
        self.buttonConfirm = QPushButton('Confirm', self)
        self.buttonConfirm.clicked.connect(self.handleCode)

        self.setWindowTitle("MaxTrade MFA Verification")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))

        #Data ported from newLogin method
        self.url = url
        self.data = data
        self.payload = payload
        self.sess_data = sess_data

        layout = QVBoxLayout(self)
        layout.addWidget(self.code)
        layout.addWidget(self.buttonConfirm)
    def handleCode(self):
        mfa_token = self.code.text()
        self.payload['mfa_code'] = mfa_token
        res = helper.request_post(self.url, self.payload, jsonify_data=False)
        print("MFA RES: "+str(res.json()))
        if (res.status_code != 200):
            QMessageBox.warning(self, 'Error', 'Incorrect MFA Verfication Number. Try again.')
            return False
            # mfa_token = input(
            #     "That MFA code was not correct. Please type in another MFA code: ")
            # self.payload['mfa_code'] = mfa_token
            # res = helper.request_post(self.url, self.payload, jsonify_data=False)
        self.data = res.json()
        # auth.respond_to_challenge(urls.challenge_url)
        self.endLogin(self.data, self.sess_data[0],self.sess_data[1],self.sess_data[2])
        return True
    def endLogin(self, data, store_session, pickle_path, device_token):
        # Update Session data with authorization or raise exception with the information present in data.
        if 'access_token' in data:
            print("Logging in!!")
            token = '{0} {1}'.format(data['token_type'], data['access_token'])
            helper.update_session('Authorization', token)
            helper.set_login_state(True)
            data['detail'] = "logged in with brand new authentication code."
            if store_session:
                with open(pickle_path, 'wb') as f:
                    pickle.dump({'token_type': data['token_type'],
                                'access_token': data['access_token'],
                                'refresh_token': data['refresh_token'],
                                'device_token': device_token}, f)
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect MFA Verfication Number')
            raise Exception(data['detail'])
        return(data)
#SMS Verification Code
class SMSCode(QDialog):
    def __init__(self, data, url, payload, sess_data, parent=None):
        super(SMSCode, self).__init__(parent)
        self.code = QLineEdit(self)
        self.code.setPlaceholderText("SMS Verification Code")
        self.buttonConfirm = QPushButton('Confirm', self)
        self.buttonConfirm.clicked.connect(self.handleCode)

        self.setWindowTitle("MaxTrade SMS Verification")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))

        #Data ported from newLogin method
        self.url = url
        self.data = data
        self.payload = payload
        self.sess_data = sess_data

        layout = QVBoxLayout(self)
        layout.addWidget(self.code)
        layout.addWidget(self.buttonConfirm)
    def handleCode(self):
        challenge_id = self.data['challenge']['id']
        # sms_code = input('Enter Robinhood code for validation: ')
        sms_code = self.code.text()
        res = auth.respond_to_challenge(challenge_id, sms_code)
        if 'challenge' in res and res['challenge']['remaining_attempts'] > 0:
            QMessageBox.warning(self, 'Error', 'Incorrect SMS Verfication Number. {} tries remaining.'.format(
                res['challenge']['remaining_attempts']))
            # sms_code = input('That code was not correct. {0} tries remaining. Please type in another code: '.format(
            #     res['challenge']['remaining_attempts']))
            # res = auth.respond_to_challenge(challenge_id, sms_code)
            return False
        elif 'challenge' in res and res['challenge']['remaining_attempts'] <= 0:
            print("No more tries remaining")
            QMessageBox.warning(self, 'Error', 'No more tries remaining. Try again')
        helper.update_session(
            'X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
        self.data = helper.request_post(self.url, self.payload)
        # auth.respond_to_challenge(urls.challenge_url)
        self.endLogin(self.data, self.sess_data[0],self.sess_data[1],self.sess_data[2])
        return True
    def endLogin(self, data, store_session, pickle_path, device_token):
        # Update Session data with authorization or raise exception with the information present in data.
        if 'access_token' in data:
            token = '{0} {1}'.format(data['token_type'], data['access_token'])
            helper.update_session('Authorization', token)
            helper.set_login_state(True)
            data['detail'] = "logged in with brand new authentication code."
            if store_session:
                with open(pickle_path, 'wb') as f:
                    pickle.dump({'token_type': data['token_type'],
                                'access_token': data['access_token'],
                                'refresh_token': data['refresh_token'],
                                'device_token': device_token}, f)
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect SMS Verfication Number')
            raise Exception(data['detail'])
        return(data)
class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        # try:
        #     a=self.login()
        #     if(a):
        #         print("ACCEPTING")
        #         self.accept()
        #         QCoreApplication.quit()
        # except:
        #     print("Auto login failed, manual login initiated")
        #     sys.exit()
        self.robinhood = r.Robinhood()

        self.textName = QLineEdit(self)
        self.textName.setPlaceholderText("Robinhood Username/Email")
        self.textPass = QLineEdit(self)
        self.textPass.setPlaceholderText("Robinhood Password")
        self.textPass.setEchoMode(QLineEdit.Password)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.setWindowTitle("MaxTrade Login")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

        

    def handleLogin(self):
        self.setUsernamePW(self.textName.text(), self.textPass.text())
        
        if(self.login()):
                self.accept()
        
        #     QMessageBox.warning(
        #         self, 'Error', 'Incorrect username or password')
        # else:
        #     authCode = SMSCode()
        #     if(authCode.exec_() == QDialog.Accepted):
        #         self.accept()

    def getUserInfo(self):
        username = k.get_password("MaxTradeBot", "BotUserName")
        return {"username":username, "password":k.get_password("MaxTrade", username)}
    #Sets stored username and password based on input
    def setUsernamePW(self, username, password):
        k.set_password("MaxTradeBot", "BotUserName", username)
        k.set_password("MaxTrade", k.get_password("MaxTradeBot", "BotUserName"), password)

    def login(self):
        if(k.get_password("MaxTradeBot", "BotUserName") == None):
            return False
        else:
            # print("Username stored:{}, Password Stored:{}".format(self.getUserInfo()["username"], self.getUserInfo()["password"]))
            a = self.newLogin(username=self.getUserInfo()["username"],password=self.getUserInfo()["password"], store_session = True)
            print("Login result: "+str(a))
            return a
    

    def newLogin(self, username=None, password=None, expiresIn=86400, scope='internal', by_sms=True, store_session=True, mfa_code=None):
        """This function will effectively log the user into robinhood by getting an
        authentication token and saving it to the session header. By default, it
        will store the authentication token in a pickle file and load that value
        on subsequent logins.

        :param username: The username for your robinhood account, usually your email.
            Not required if credentials are already cached and valid.
        :type username: Optional[str]
        :param password: The password for your robinhood account. Not required if
            credentials are already cached and valid.
        :type password: Optional[str]
        :param expiresIn: The time until your login session expires. This is in seconds.
        :type expiresIn: Optional[int]
        :param scope: Specifies the scope of the authentication.
        :type scope: Optional[str]
        :param by_sms: Specifies whether to send an email(False) or an sms(True)
        :type by_sms: Optional[boolean]
        :param store_session: Specifies whether to save the log in authorization
            for future log ins.
        :type store_session: Optional[boolean]
        :param mfa_code: MFA token if enabled.
        :type mfa_code: Optional[str]
        :returns:  A dictionary with log in information. The 'access_token' keyword contains the access token, and the 'detail' keyword \
        contains information on whether the access token was generated or loaded from pickle file.

        """
        device_token = auth.generate_device_token()
        home_dir = os.path.expanduser("~")
        data_dir = os.path.join(home_dir, ".tokens")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        creds_file = "robinhood.pickle"
        pickle_path = os.path.join(data_dir, creds_file)
        # Challenge type is used if not logging in with two-factor authentication.
        if by_sms:
            challenge_type = "sms"
        else:
            challenge_type = "email"

        url = urls.login_url()
        payload = {
            #This ID is from robin_stocks, not specific to user
            'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
            'expires_in': expiresIn,
            'grant_type': 'password',
            'password': password,
            'scope': scope,
            'username': username,
            'challenge_type': challenge_type,
            'device_token': device_token
        }

        if mfa_code:
            payload['mfa_code'] = mfa_code

        # If authentication has been stored in pickle file then load it. Stops login server from being pinged so much.
        if os.path.isfile(pickle_path):
            # If store_session has been set to false then delete the pickle file, otherwise try to load it.
            # Loading pickle file will fail if the acess_token has expired.
            if store_session:
                try:
                    with open(pickle_path, 'rb') as f:
                        pickle_data = pickle.load(f)
                        access_token = pickle_data['access_token']
                        token_type = pickle_data['token_type']
                        refresh_token = pickle_data['refresh_token']
                        # Set device_token to be the original device token when first logged in.
                        pickle_device_token = pickle_data['device_token']
                        payload['device_token'] = pickle_device_token
                        # Set login status to True in order to try and get account info.
                        helper.set_login_state(True)
                        helper.update_session(
                            'Authorization', '{0} {1}'.format(token_type, access_token))
                        # Try to load account profile to check that authorization token is still valid.
                        res = helper.request_get(
                            urls.portfolio_profile(), 'regular', payload, jsonify_data=False)
                        # Raises exception is response code is not 200.
                        res.raise_for_status()
                        return({'access_token': access_token, 'token_type': token_type,
                                'expires_in': expiresIn, 'scope': scope, 'detail': 'logged in using authentication in {0}'.format(creds_file),
                                'backup_code': None, 'refresh_token': refresh_token})
                except:
                    print(
                        "ERROR: There was an issue loading pickle file. Authentication may be expired - logging in normally.", file=helper.get_output())
                    helper.set_login_state(False)
                    helper.update_session('Authorization', None)
            else:
                os.remove(pickle_path)

        # Try to log in normally.
        if not username:
            username = input("Robinhood username: ")
            payload['username'] = username

        if not password:
            password = getpass.getpass("Robinhood password: ")
            payload['password'] = password

        data = helper.request_post(url, payload)
        print("DATA: "+str(data))
        # Handle case where mfa or challenge is required.
        if data:
            if 'mfa_required' in data:
                print("MFA CHALLENGED, OPENING MFA-V-CODE TAB")
                authCode = MFACode(data, url, payload, [store_session,pickle_path,device_token])
                # print("MFA CODE: "+authCode)
                if(authCode.exec_() == QDialog.Accepted):
                    self.accept()
            elif 'challenge' in data:
                print("SMS CHALLENGED, OPENING SMS-V-CODE TAB")
                authCode = SMSCode(data, url, payload, [store_session,pickle_path,device_token])
                if(authCode.exec_() == QDialog.Accepted):
                    self.accept()
            elif(data['detail']):
                QMessageBox.warning(self, 'Error', 'Incorrect Username or Password. Try again')