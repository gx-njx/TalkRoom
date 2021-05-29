
import sys
import re
import threading
import subprocess

class DetecIP:

    def __init__(self, startip = "192.168.1.0"):
        super().__init__()
        self.setip(startip)
        self.pthread_list = []
        self.ip_list = []
        self.setip(startip)

    def setip(self, startip):
        endip = ""
        pattern = r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))$)"
        m = re.match(pattern, startip)      # 检查IP地址是否合法
        if m:
            temip = startip.split('.')
            temip[3] = '255'
            endip = '.'.join(temip)
            self.startip = startip.split('.')
            self.startip[3] = str(0)
            self.endip = endip.split('.')
        else:
            print("ip不合法")

    def get_ping_result(self, tip):
        '''
        检查对应的IP是否被占用
        '''
        cmd_str = "ping {0} -n 1 -w 600".format(tip)
        DETACHED_PROCESS = 0x00000008   # 不创建cmd窗口
        try:
            subprocess.check_call(cmd_str, creationflags=DETACHED_PROCESS)  # 仅用于windows系统
        except subprocess.CalledProcessError as err:
            return
        else:
            self.ip_list.append(tip)

    def getip(self):
        get_ping_result = self.get_ping_result
        pthread_list = self.pthread_list
        startip = self.startip
        endip = self.endip
        tmp_ip = self.startip
        for i in range(int(startip[3]), int(endip[3]) + 1):
            tmp_ip[3] = str(i)
            ip = '.'.join(tmp_ip)
            pthread_list.append(threading.Thread(target=self.get_ping_result, args=[ip]))
        for pthread in pthread_list:
            pthread.start()
        for pthread in pthread_list:
            pthread.join()
        return self.ip_list
        


if __name__ == "__main__":
    aa = DetecIP('192.168.31.161')

    ip_list = aa.getip()
    print("占用的IP：")
    for item in ip_list:
        print(item)
