import ast
import functools
import json
from collections import OrderedDict
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from PyQt5 import QtWebSockets
from PyQt5.QtCore import pyqtSlot, QUrl, pyqtSignal, QTimer, QTime
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from configobj import ConfigObj
from engineio.packet import MESSAGE
from selenium import webdriver

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from socketio.packet import EVENT
from app.tools.engineio.packet import EngineIoPacket
from app.tools.seleniumrequests import Chrome
from app.UIControl import logger
from app.UIView.aliPayMainWindow import Ui_MainWindow
from app.tools.socketio.packet import SocketIoPacket
from profile import profile


def get_query_dict(query):
    query_dict = OrderedDict()
    query_items = query.split('&') if '&' in query \
        else query.split(';')
    for k, v in map(lambda x: x.split('='), query_items):
        if k in query_dict:
            if isinstance(query_dict, list):
                query_dict[k].append(v)
            else:
                query_dict[k] = [query_dict[k], v]
        else:
            query_dict[k] = v
    return query_dict


class aliPayControl(QMainWindow, Ui_MainWindow):
    start_work_signal = pyqtSignal(dict)

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

        self.start_work_signal.connect(self.on_start_work_signal)  # 接收到服务器开始工作的指令

        self.option = webdriver.ChromeOptions()
        self.title = ""
        self.option.add_argument('disable-infobars')
        self.option.add_argument('--log-level=3')
        self.option.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = Chrome(chrome_options=self.option, executable_path=profile.WEB_DRIVER_PATH)
        self.driver.implicitly_wait(2)  # 所有的加载页面隐式等待20秒

        self.time = 2
        self.wait_time = 5
        self.exception = (Exception,)
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.on_flash_timer)
        self.flash_timer.setInterval(int(self.config['INTERVAL'])*1000)
        self.ping_timer = QTimer(self)
        self.ping_timer.timeout.connect(self.on_ping_timer)

        self.ping_timer.setInterval(20 * 1000)

    @pyqtSlot()
    def on_ping_timer(self):
        if self.websocket.isValid():
            self.websocket.sendBinaryMessage(b"2")

    @pyqtSlot()
    def on_flash_timer(self):
        # 定时刷新订单页面

        original_window_handle = self.driver.current_window_handle  # 拿到当前的窗口句柄
        for hande in self.driver.window_handles:
            self.driver.switch_to.window(hande)
            if self.driver.current_url == "https://render.alipay.com/p/s/alipay_site/wait":
                self.driver.get("https://my.alipay.com/portal/i.htm")  # 操作完一边 回到用户主页
            if str(self.driver.current_url) == "https://consumeprod.alipay.com/record/advanced.htm":
                self.driver.refresh()
                with open(profile.WORK_JS,"r") as f:

                    self.driver.execute_script("".join(f.readlines()))
            if str(self.driver.current_url).startswith("https://consumeprod.alipay.com/errorSecurity.htm"):
                self.driver.get("https://consumeprod.alipay.com/record/standard.htm")

            if str(self.driver.current_url).startswith("https://consumeprod.alipay.com/record/checkSecurity.htm"):
                QMessageBox.warning(self,"错误","被检测出非用户操作，请按要求登录")
            self.delayMsec(5*1000)
            ## TODO 安全检查
        if self.driver.current_window_handle != original_window_handle:
            self.driver.switch_to.window(original_window_handle)  # 并切回来

    def delayMsec(self, msec):
        dieTime = QTime.currentTime().addMSecs(msec)
        while QTime.currentTime() < dieTime:
            QApplication.processEvents()

    def retries(func):
        # 类中定义一个重试的装饰器


        @functools.wraps(func)
        def warpper(self, *args, **kwargs):
            for i in range(self.time + 1):

                try:
                    result = func(self, *args, **kwargs)
                except self.exception as e:
                    logger.info("启用重试器")
                    logger.error(str(func))
                    logger.error(e)
                    self.delayMsec(5*1000)
                    continue
                else:
                    return result
            # 如果重试几次还没有得到结果，那么可能是cookies失效了，回到主页
            self.driver.get("https://my.alipay.com/portal/i.htm")

        return warpper

    def in_ali_login_page(self):
        '''判断是否在阿里支付宝登录页面'''
        return self.driver.current_url == profile.ALI_LOGIN_PATH



    @pyqtSlot(dict)
    def on_start_work_signal(self, recv_json):
        '''开始工作流程'''

        if not self.driver.get_cookies():  # 如果cookies失效，重回到登录界面
            self.driver.get(profile.ALI_LOGIN_PATH)

        content_dict = ast.literal_eval(recv_json.get("content"))  # 开始工作，拿到服务器传来的消息
        logger.info("content_dict->" + str(content_dict))
        self.click_work(content_dict.get("bankcode"), content_dict.get("money"), recv_json.get("id"),
                        content_dict.get("mark"))

    @retries
    def go_to_charge_page(self):
        # 进入到充值页面
        self.driver.get("https://shenghuo.alipay.com/transfer/deposit/depositPreprocessGw.htm")

    @retries
    def click_charge_to_left(self):
        # 点击充值到余额
        self.driver.find_element_by_xpath(
            "//*[@id='container']/div[1]/ul/li[2]/a").click()

    @retries
    def go_to_next(self):
        # 点击选择其他，进入到选择银行页面
        href = self.driver.find_element_by_xpath("//*[@id='J-DEbank']/div/form/div[2]/div/ul/li/a").get_attribute(
            "href")
        self.driver.get(href)

    @retries
    def chose_bank(self, bank_code):
        self.driver.find_element_by_xpath(f"//input[@value='{bank_code}']").click()  # 选择银行

    @retries
    def click_chose_bank_button(self):
        self.driver.find_element_by_xpath("//*[@id='bankCardForm']/div/input").click()  # 选择下一步

    @retries
    def input_money(self, money):
        self.driver.find_element_by_xpath("//*[@id='J-depositAmount']").send_keys(money)

    @retries
    def click_submit(self):
        # 点击登陆到网上银行
        self.driver.find_element_by_xpath('//input[@id="J-deposit-submit"]').click()


    @retries
    def get_ua(self):
        # 得到UAID
        return self.driver.find_element_by_xpath("//*[@id='UA_InputId']").get_attribute("value")

    @retries
    def get_order_id(self):
        return self.driver.find_element_by_xpath("//*[@id='orderId']").get_attribute("value")

    @retries
    def get_form_token(self):
        return self.driver.find_element_by_xpath('//*[@id="ebankDepositForm"]/input[1]').get_attribute(
            "value")

    @retries
    def get_securityId(self):
        return self.driver.find_element_by_xpath("//*[@id='securityId']").get_attribute(
            "value")

    @retries
    def click_work(self, bank_code, money, msgid, mark):
        logger.info("开始")
        if self.in_ali_login_page():  # 每次任务开始前都要检查自己是不是在登陆页面，如果在登录界面，则直接提示用户登录，并结束本次流程
            QMessageBox.warning(self, "错误", "请登录支付宝")
            return

        if self.driver.current_url == "https://my.alipay.com/portal/i.htm":  # 如果在登录后的主页中，下一步期待进入充值页面
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")
            # self.driver.find_element_by_xpath("//*[@id='J-assets-balance']/div[1]/div/div[2]/ul/li[1]/a").click()  # 点击充值按钮
            logger.info("当前在个人用户主页:" + str(self.driver.current_url))

            if len(self.driver.window_handles) == 1:
                original_window_handle = self.driver.current_window_handle  # 拿到当前的窗口句柄
                print(self.driver.current_window_handle)
                self.driver.execute_script("window.open('https://consumeprod.alipay.com/record/advanced.htm');")
                QMessageBox.warning(self,"请登录","请登录后才点击确定")
                print(self.driver.current_window_handle)

                self.driver.switch_to.window(original_window_handle)  # 并切回来
                self.flash_timer.start()
            self.go_to_charge_page()

        if str(self.driver.current_url).startswith("https://cashiersu18.alipay.com/standard/deposit/cashier.htm"):
            logger.info("当前在支付宝充值主页是:" + str(self.driver.current_url))
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")
            try:
                self.driver.find_element_by_xpath("//*[@id='content']/div[1]/ul/li[1]/a")
                # 尝试获取这个元素，如果获取到了，则说明已经选择了充实到余额
                logger.info("已经选择了充值到余额")
            except Exception as e:
                # 如果出现了异常，则说明，没选，需要选一下
                self.click_charge_to_left()

            self.go_to_next()

        if str(self.driver.current_url).startswith("https://cashiersu18.alipay.com/standard/deposit/chooseBank.htm"):
            logger.info("当前在选择银行主页:" + str(self.driver.current_url))
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")
            self.chose_bank(bank_code)  # 选择银行
            # self.driver.execute_script(f"document.getElementById('{profile.BAND_CODE_ID.get(bank_code)}').click()")
            self.click_chose_bank_button()  # 选择下一步

        if str(self.driver.current_url).startswith("https://cashiersu18.alipay.com/standard/gateway/ebankDeposit.htm"):
            # 在这个页面操作完了，一定要回到登录后的主页页面 https://my.alipay.com/portal/i.htm
            logger.info("当前在充值金额页面")
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")
            self.input_money(money)  # 填写金额
            self.driver.execute_script("window.onbeforeunload = function() { return 'NUL'; }")
            self.click_submit()  # 点击登录到网上银行

            wait = WebDriverWait(self.driver, 5)  # 等待告警出现
            alert = wait.until(expected_conditions.alert_is_present())
            if alert:
                alert.dismiss()
            ua = self.get_ua()
            self.driver.execute_script("window.onbeforeunload = function() { return null; }")
            self.driver.refresh()  # 刷新
            orderId = self.get_order_id()  # 拿到orderId
            form_token = self.get_form_token()
            securityId = self.get_securityId()  # 拿到securityId
            ctoken = self.driver.get_cookie("ctoken").get("value")
            data = {
                "_form_token": form_token,
                "orderId": orderId,
                "securityId": securityId,
                "depositAmount": float(money),
                "depositType": "hasAmount",
                "ua": ua,
                "_input_charset": "utf-8",
                "ctoken": ctoken
            }
            response = self.driver.request("POST", "https://cashiersu18.alipay.com/standard/gateway/ebankDeposit.json",
                                           data=data, find_window_handle_timeout=5, page_load_timeout=5
                                           )

            url = json.loads(response.text).get("url").replace("\\", "")
            outBizNo = get_query_dict(urlparse(url).query).get("outBizNo")
            result = self.driver.request("GET", json.loads(response.text).get("url").replace("\\", ""))
            html = result.text
            soup = BeautifulSoup(html, features="html.parser")
            form = soup.select("form[id='ebankDepositForm']")[0]
            self.send_to_websocket({
                "code": 0,
                "msg": "获取成功",
                "payurl": str(form),
                "mark": str(mark),
                "money": float(money),
                "type": "alibank",
                "msgId": str(msgid),
                "batchNo": outBizNo,
                "bankCode": bank_code
            })
            self.driver.get("https://my.alipay.com/portal/i.htm")  # 操作完一边 回到用户主页
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")

    @pyqtSlot()
    def on_close_driver_signal(self):
        self.driver.quit()

    @pyqtSlot(str)
    def on_set_title_signal(self, title):

        self.driver.execute_script(f"document.title='{title}'")

    def closeEvent(self, QCloseEvent):
        self.driver.quit()
        self.websocket.close()
        QCloseEvent.accept()

    def send_to_websocket(self, data: dict):
        '''向CTP服务器发送数据'''
        logger.info("向服务器发送数据" + str(data))
        if isinstance(data, dict):
            d = json.dumps(data)
        else:
            d = str(data)
        logger.info(d)
        b_message = EngineIoPacket(MESSAGE,SocketIoPacket(EVENT,data=["message"]+[d]).encode()).encode()
        logger.info(b_message)
        self.websocket.sendBinaryMessage(b_message)


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
            self.start_work_signal.emit(msg)

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
        self.ping_timer.start()
    @pyqtSlot()
    def on_start_pushButton_clicked(self):
        '''开始'''
        if not self.websocket.isValid():
            key_name = self.key_name_lineEdit.text()
            token_value = self.token_value_lineEdit.text()
            if not key_name or not token_value:
                QMessageBox.warning(self, "错误", "请输入")
                return
            address = f"ws://{self.config['SOCKET']['IP']}:{self.config['SOCKET']['PORT']}/socket.io/?EIO=3&transport=websocket&token={token_value}"
            logger.info(f"尝试与{address}建立连接")
            self.websocket.open(QUrl(address))  # 建立连接
            self.title = key_name
            self.driver.get(profile.ALI_LOGIN_PATH)
            self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")

    @pyqtSlot()
    def on_set_title_pushButton_clicked(self):
        '''设置页面title'''
        self.driver.execute_script(f"document.title='{self.key_name_lineEdit.text()}'")
