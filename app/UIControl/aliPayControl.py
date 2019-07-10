import json


from PyQt5 import QtWebSockets
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from configobj import ConfigObj

from app.UIControl import logger
from app.UIView.aliPayMainWindow import Ui_MainWindow
from profile import profile


class aliPayControl(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(aliPayControl, self).__init__()
        self.setupUi(self)
        self.show()

        self.config = ConfigObj(profile.CONFIG_INI_URL, encoding=profile.ENCODING)

        self.websocket = QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)  # 与直播服务器的连接
        # self.websocket = QTcpSocket(self)
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_textMessageReceived)
        # self.websocket.readyRead.connect(self.on_readyRead)
        self.websocket.error.connect(self.on_error)
        self.websocket.stateChanged.connect(self.on_stateChanged)


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
        recv_data = json.loads(message)
        logger.info("收到直播服务器数据" + str(recv_data))
        # try:
        #     getattr(self, purpose + "_signal").emit(recv_data)
        # except AttributeError as e:
        #     logger.error("收到服务器未知含义的包")

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
        key_name = self.key_name_lineEdit.text()
        token_value = self.token_value_lineEdit.text()
        if not key_name or  not token_value:
            QMessageBox.warning(self, "错误", "请输入")
            return
        address = f"http://{self.config['SOCKET']['IP']}:{self.config['SOCKET']['PORT']}/?token={token_value}"
        print(address)
        self.websocket.open(QUrl(address))
        #
        # self.websocket.connectToHost(address,
        #                            QTcpSocket.ReadWrite)
        # 建立连接