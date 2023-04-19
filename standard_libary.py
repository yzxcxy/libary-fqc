from configparser import ConfigParser
import datetime
import time
import requests
import os
from pathlib import Path

path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "conf.ini")  # 默认读取当前文件夹下的con.ini文件

config = ConfigParser()

# 读取配置文件
config.read(config_path, encoding="utf-8")

# 填充信息到全局变量
username = config["user"]["id"]
password = config["user"]["password"]
login_cookie = config["user"]["login_cookie"]
cookie = config["user"]["cookie"]
start_time = config["time"]["start"]
end_time = config["time"]["end"]
devs_temp = config["seats"]["devs"]
devs = devs_temp.split(",")
start_go = config["time"]["start_go"]  # 开始抢座时间
url = config["user"]["url"]


# TODO 添加对数据的校验功能


# 获得13位时间戳
def get_time():
    millis = str(int(round(time.time() * 1000)))
    return millis


# 转换时分秒到秒
def t2s(t):  # t format is hh:mm:ss
    if t != '0':
        h, m, s = t.strip().split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        return 0


# 生成url
def generate_get_url(dev_id, current_time):
    # 设备id
    global end_time
    dev = dev_id
    # 当前时间(填充到url中
    c_time = str(current_time)
    # 获取后一日的日期
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    split = last_date.split("-")
    year = split[0]
    month = split[1]
    day = split[2]
    weekday = datetime.date(int(year), int(month), int(day)).weekday()

    # 判断是否为星期五
    if weekday == 4:
        if t2s(end_time + ":00") > t2s("20:00:00"):
            end_time = "20:00"
    else:
        if t2s(end_time + ":00") > t2s("22:00:00"):
            end_time = "22:00"

    # 转化时间个格式、
    start_time_f1 = start_time.split(":")[0] + "%3A" + start_time.split(":")[1]
    start_time_f2 = start_time.split(":")[0] + start_time.split(":")[1]
    end_time_f1 = end_time.split(":")[0] + "%3A" + end_time.split(":")[1]
    end_time_f2 = end_time.split(":")[0] + end_time.split(":")[1]
    # 返回生成的请求url
    return url.format(dev, last_date, start_time_f1, last_date, end_time_f1, start_time_f2, end_time_f2, c_time)


# 登录所耗费的时间大概是两秒，建议先进行登录
def login():
    print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), "login...")
    login_url = "https://libic.njfu.edu.cn/ClientWeb/pro/ajax/login.aspx"
    # 请求头
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Length": "38",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Cookie": login_cookie,
        "Host": "libic.njfu.edu.cn",
        "Origin": "https://libic.njfu.edu.cn",
        "Referer": "https://libic.njfu.edu.cn/clientweb/xcus/ic2/Default.aspx?version=3.00.20181109",
        "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like ecko) "
                      "Chrome/107.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    # post请求体，id为学号,pwd为密码,act为行为
    data = "_=" + get_time() + "&id={}&pwd={}&act=login".format(username, password)
    response = requests.post(url=login_url, headers=headers, data=data)
    if response.status_code == 200:
        print("返回体信息:" + response.text)
        print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), " 登录成功")
        return 1
    else:
        print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), " 登录失败")
        return 0


def greb_the_seat():
    print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), " starting...")
    # 需要遍历的所有座位号,按照需求进行填入
    dev_id = devs

    headers = {
        "Accept": "application/json, text/javascript, * / *; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "libic.njfu.edu.cn",
        "Origin": "https://libic.njfu.edu.cn",
        "Referer": "https://libic.njfu.edu.cn/clientweb/xcus/ic2/Default.aspx?version=3.00.20181109",
        "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like ecko) "
                      "Chrome/107.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    # 定时
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    stamp = time.mktime(time.strptime(now + " " + start_go, '%Y-%m-%d %H:%M:%S'))
    while True:
        # 当前时间的十位时间戳
        # TODO 添加多线程优化
        current_stamp = int(time.time())
        if current_stamp >= stamp:
            break
    for dev in dev_id:
        get_url = generate_get_url(dev, get_time())
        response = requests.get(url=get_url, headers=headers)
        print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), end="")
        print(response.text)
        response_json = response.json()
        msg_json = response_json["msg"]
        if msg_json != "操作成功！":
            print("获取" + dev + "失败")
        else:
            print("抢座成功")
            break


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    flag = False
    count = 0
    while not flag and count < 4:
        # 直到登录成功才进行抢座
        if login() == 1:
            flag = True
            greb_the_seat()
        count += 1
    print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), end="")
    print("本次运行结束，goodbye")
