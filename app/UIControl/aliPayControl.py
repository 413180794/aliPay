import ast
import json

import selenium
from PyQt5 import QtWebSockets
from PyQt5.QtCore import pyqtSlot, QUrl, QObject, QThread, pyqtSignal
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from configobj import ConfigObj
from selenium import webdriver
from app.UIControl import logger
from app.UIView.aliPayMainWindow import Ui_MainWindow
from profile import profile


class autoWork(QObject):
    set_title_signal = pyqtSignal(str)
    close_driver_signal = pyqtSignal()
    start_work_signal = pyqtSignal(dict)
    warn_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(autoWork, self).__init__(parent)
        self.option = webdriver.ChromeOptions()
        self.title = ""
        self.option.add_argument('disable-infobars')
        self.driver = webdriver.Chrome(profile.WEB_DRIVER_PATH, chrome_options=self.option)  #
        self.driver.implicitly_wait(20)  # 所有的加载页面隐式等待20秒
        self.set_title_signal.connect(self.on_set_title_signal)
        self.close_driver_signal.connect(self.on_close_driver_signal)
        self.start_work_signal.connect(self.on_start_work_signal)

    def in_ali_login_page(self):
        '''判断是否在阿里支付宝页面'''
        return self.driver.current_url == profile.ALI_LOGIN_PATH

    def ready_for_login(self):
        if not self.in_ali_login_page():
            logger.info("未登录的cookies" + str(self.driver.get_cookies()))
            self.driver.get(profile.ALI_LOGIN_PATH)
            self.driver.execute_script(f"document.title='{self.title}'")

    @pyqtSlot(dict)
    def on_start_work_signal(self, recv_json):
        '''开始工作流程'''
        # 判断是否还是在登录页面，如果还在提示用户登录
        if self.in_ali_login_page():
            self.warn_signal.emit()
        else:
            # TODO 开始工作流程
            # 如果登陆后页面在 http://www.alipay.com下，需要选择（我是合作伙伴、我是上架用户、我是个人用户）
            # 点击我是个人用户以后，点击进入我的支付宝
            # 点击充值
            # 选择充值到余额
            #
            if not self.driver.get_cookies():  # 如果cookies失效，重回到登录界面
                self.driver.get(profile.ALI_LOGIN_PATH)
            logger.info("已经登录的cookies" + str(self.driver.get_cookies()))
            try:
                print(self.driver.window_handles)
                content_dict = ast.literal_eval(recv_json.get("content"))
                self.click_work(content_dict.get("bankcode"), content_dict.get("money"))
            except selenium.common.exceptions.NoSuchElementException as e:
                logger.error("网速太慢，无法加载出网页，导致元素无法定位或者元素的class已经被修改" + str(e))

    def click_work(self, bank_code, money):
        self.driver.find_element_by_xpath("/html/body/div/div[2]/div[1]/div/div[2]/div/a[3]").click()  # 点击个人用户
        self.driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/ul[2]/li[3]/a").click()  # 点击进入我的支付宝
        self.driver.find_element_by_xpath("//*[@id='J-assets-balance']/div[1]/div/div[2]/ul/li[1]/a").click()  # 点击充值按钮
        print(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[1])
        if self.driver.find_element_by_xpath("//*[@id='content']/div[1]/ul/li[1]/a"):
            logger.info("已经选择了充值到余额")
        else:
            self.driver.find_element_by_xpath("//*[@id='container']/div[1]/ul/li[2]/a").click()  # 点击充值到余额,有可能已经点过了，那就不点了
        href = self.driver.find_element_by_xpath("//*[@id='J-DEbank']/div/form/div[2]/div/ul/li/a").get_attribute("href")
        self.driver.get(href)
        self.driver.find_element_by_xpath(f"//input[@value='{bank_code}']").click() # 选择银行
        # self.driver.execute_script(f"document.getElementById('{profile.BAND_CODE_IDget(bank_code)}').click()")
        self.driver.find_element_by_xpath("//*[@id='bankCardForm']/div/input").click() # 选择下一步
        self.driver.find_element_by_xpath("//*[@id='J-depositAmount']").send_keys(money)

    @pyqtSlot()
    def on_close_driver_signal(self):
        self.driver.quit()

    @pyqtSlot(str)
    def on_set_title_signal(self, title):
        print(f"document.title={title}")
        self.driver.execute_script(f"document.title='{title}'")


class aliPayControl(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(aliPayControl, self).__init__()
        self.setupUi(self)
        self.show()

        self.config = ConfigObj(profile.CONFIG_INI_URL, encoding=profile.ENCODING)
        self.websocket = QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)  # 与直播服务器的连接
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_textMessageReceived)
        self.websocket.error.connect(self.on_error)
        self.websocket.stateChanged.connect(self.on_stateChanged)

        self.autoWork = autoWork()
        self.autoWork.warn_signal.connect(self.on_warn_signal)
        self.work_thread = QThread(self)

    @pyqtSlot()
    def on_warn_signal(self):
        QMessageBox.warning(self, "错误", "请扫码登录支付宝")

    def closeEvent(self, QCloseEvent):
        self.autoWork.close_driver_signal.emit()
        self.websocket.close()
        QCloseEvent.accept()

    def send_to_websocket(self, data: dict):
        '''向CTP服务器发送数据'''
        logger.info("向服务器发送数据" + str(data))
        if isinstance(data, dict):
            d = json.dumps(data)
        else:
            d = str(data)
        self.websocket.sendTextMessage(d)

    @pyqtSlot()
    def on_disconnected(self):
        '''与CTP服务器断开连接'''
        logger.info("与服务器断开连接")

    @pyqtSlot(str)
    def on_textMessageReceived(self, message: str):
        '''直播服务器收到数据'''

        logger.info("接收服务器消息" + str(message))
        if message.startswith("0"):
            logger.info("engine.io is OPENED")
            logger.info(json.loads(message[1:]))
        elif message == "40":
            pass
        elif message.startswith("42"):
            msg = json.loads(ast.literal_eval(message[2:])[1])
            logger.info("接收服务器有效数据包" + str(msg))
            self.autoWork.start_work_signal.emit(msg)

    @pyqtSlot(QAbstractSocket.SocketError)
    def on_error(self, error_code):
        '''CTP连接错误码'''
        if error_code == 0:
            logger.error("服务器，连接被拒绝（或者超时）")
        elif error_code == 1:
            logger.error("服务器，连接被远程服务器断开，请注意，在发送远程关闭通知后，将关闭客户端套接字（即此套接字）")
            # self.change_loginDialog_lineedit_empty_label_text("连接被远程服务器断开，请注意，在发送远程关闭通知后，将关闭客户端套接字（即此套接字）")
        elif error_code == 2:
            logger.error("服务器，找不到主机地址")
            # self.change_loginDialog_lineedit_empty_label_text("找不到主机地址")
        elif error_code == 3:
            logger.error("服务器，套接字操作失败，因为应用程序缺少必需的权限。")
            # self.change_loginDialog_lineedit_empty_label_text("套接字操作失败，因为应用程序缺少必需的权限。")
        elif error_code == 4:
            logger.error("服务器，本地系统耗尽资源（例如，套接字太多）。")
            # self.change_loginDialog_lineedit_empty_label_text("本地系统耗尽资源（例如，套接字太多）。")
        elif error_code == 5:
            logger.error("服务器，套接字操作超时。")
            # self.change_loginDialog_lineedit_empty_label_text("套接字操作超时。")
        elif error_code == 6:
            logger.error("服务器，数据报大于操作系统的限制（可以低至8192字节）。")
            # self.change_loginDialog_lineedit_empty_label_text("数据报大于操作系统的限制（可以低至8192字节）。")
        elif error_code == 7:
            logger.error("服务器，网络发生错误（例如，网络电缆意外拔出）。")
            # self.change_loginDialog_lineedit_empty_label_text("网络发生错误（例如，网络电缆意外拔出）。")
        elif error_code == 8:
            logger.error("服务器，为QAbstractSocket :: bind（）指定的地址已被使用，并被设置为独占。")
            # self.change_loginDialog_lineedit_empty_label_text("为QAbstractSocket :: bind（）指定的地址已被使用，并被设置为独占。")
        elif error_code == 9:
            logger.error("服务器，指定给QAbstractSocket :: bind（）的地址不属于主机。")
            # self.change_loginDialog_lineedit_empty_label_text("指定给QAbstractSocket :: bind（）的地址不属于主机。")
        elif error_code == 10:
            logger.error("服务器，本地操作系统不支持请求的套接字操作（例如，缺乏IPv6支持）。")
            # self.change_loginDialog_lineedit_empty_label_text("本地操作系统不支持请求的套接字操作（例如，缺乏IPv6支持）。")
        elif error_code == 11:
            logger.error("服务器，仅由QAbstractSocketEngine使用，最后一次尝试操作尚未完成（后台仍在进行中）。")
            # self.change_loginDialog_lineedit_empty_label_text("仅由QAbstractSocketEngine使用，最后一次尝试操作尚未完成（后台仍在进行中）。")
        elif error_code == 12:
            logger.error("服务器，套接字使用代理，代理需要身份验证。")
            # self.change_loginDialog_lineedit_empty_label_text("套接字使用代理，代理需要身份验证。")
        elif error_code == 13:
            logger.error("服务器，SSL / TLS握手失败，因此连接已关闭（仅在QSslSocket中使用）")
            # self.change_loginDialog_lineedit_empty_label_text("SSL / TLS握手失败，因此连接已关闭（仅在QSslSocket中使用）")
        elif error_code == 14:
            logger.error("服务器，无法联系代理服务器，因为与该服务器的连接被拒绝")
            # self.change_loginDialog_lineedit_empty_label_text("无法联系代理服务器，因为与该服务器的连接被拒绝")
        elif error_code == 15:
            logger.error("服务器，与代理服务器的连接意外关闭（在建立与最终对等体的连接之前）")
            # self.change_loginDialog_lineedit_empty_label_text("与代理服务器的连接意外关闭（在建立与最终对等体的连接之前）")
        elif error_code == 16:
            logger.error("服务器，与代理服务器的连接超时或代理服务器在身份验证阶段停止响应。")
            # self.change_loginDialog_lineedit_empty_label_text("与代理服务器的连接超时或代理服务器在身份验证阶段停止响应。")
        elif error_code == 17:
            logger.error("服务器，未找到使用setProxy（）（或应用程序代理）设置的代理地址。")
            # self.change_loginDialog_lineedit_empty_label_text("未找到使用setProxy（）（或应用程序代理）设置的代理地址。")
        elif error_code == 18:
            logger.error("服务器，与代理服务器的连接协商失败，因为无法理解代理服务器的响应。")
            # self.change_loginDialog_lineedit_empty_label_text("与代理服务器的连接协商失败，因为无法理解代理服务器的响应。")
        elif error_code == 19:
            logger.error("服务器，当套接字处于不允许它的状态时，尝试进行操作。")
            # self.change_loginDialog_lineedit_empty_label_text("当套接字处于不允许它的状态时，尝试进行操作。")
        elif error_code == 20:
            logger.error("服务器，正在使用的SSL库报告了内部错误。这可能是由于安装错误或库配置错误造成的。")
            # self.change_loginDialog_lineedit_empty_label_text("正在使用的SSL库报告了内部错误。这可能是由于安装错误或库配置错误造成的。")
        elif error_code == 21:
            logger.error("服务器，提供了无效数据（证书，密钥，密码等），并且其使用导致SSL库中的错误。")

        elif error_code == 22:
            logger.error("服务器，发生临时错误（例如，操作将阻塞并且套接字是非阻塞的）。")

        elif error_code == -1:
            logger.error("服务器，发生了一个未识别的错误。")

    @pyqtSlot(QAbstractSocket.SocketState)
    def on_stateChanged(self, state_code):
        '''内网服务器状态码'''
        if state_code == 0:
            # 连接未建立
            logger.info("服务器，连接未建立")
            # self.change_loginDialog_lineedit_empty_label_text("连接未建立")
        elif state_code == 1:
            logger.info("服务器，套接字正在执行主机名查找")
            # self.change_loginDialog_lineedit_empty_label_text("套接字正在执行主机名查找")
        elif state_code == 2:
            logger.info("服务器，套接字已经开始建立连接")
            # self.change_loginDialog_lineedit_empty_label_text("套接字已经开始建立连接")
        elif state_code == 3:
            logger.info("服务器连接已经建立")
            # self.change_loginDialog_lineedit_empty_label_text("连接已经建立")
        elif state_code == 4:
            logger.info("服务器，套接字绑定到地址和端口")
            # self.change_loginDialog_lineedit_empty_label_text("套接字绑定到地址和端口")
        elif state_code == 6:
            logger.info("服务器，套接字即将关闭（数据可能仍在等待写入）")
            # self.change_loginDialog_lineedit_empty_label_text("套接字即将关闭（数据可能仍在等待写入）")

    @pyqtSlot()
    def on_connected(self):
        '''与服务器连接上以后，判断一下使用的是不是本地服务器'''
        logger.info("与服务器建立连接")

    @pyqtSlot()
    def on_start_pushButton_clicked(self):
        '''开始'''
        if not self.work_thread.isRunning():
            key_name = self.key_name_lineEdit.text()
            token_value = self.token_value_lineEdit.text()
            if not key_name or not token_value:
                QMessageBox.warning(self, "错误", "请输入")
                return
            address = f"ws://{self.config['SOCKET']['IP']}:{self.config['SOCKET']['PORT']}/socket.io/?EIO=3&transport=websocket&token={token_value}"
            logger.info(f"尝试与{address}建立连接")
            self.websocket.open(QUrl(address))  # 建立连接
            self.autoWork.title = key_name
            self.autoWork.moveToThread(self.work_thread)
            self.work_thread.started.connect(self.autoWork.ready_for_login)
            self.work_thread.start()
            self.token_value_lineEdit.setEnabled(False)
            # self.start_pushButton.setEnabled(False)

    @pyqtSlot()
    def on_set_title_pushButton_clicked(self):
        '''设置页面title'''

        self.autoWork.set_title_signal.emit(self.key_name_lineEdit.text())
