import socket
import time
from threading import Thread
from multiprocessing import Process
import os

hostname_value = {}

host = '114.212.81.221'
port = 8080

ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ser.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ser.bind((host, port))

ser.listen(5)

# 设置下 中间文件夹的存储
BASE_DIR = 'D:\mid_file'
print('Server is running...')       # 打印运行提示

#用来实现注册的数据结构 字典（key,value） key:主机名 就是wifi热点的名字
# #value: list=[bool,{ip,port},conn，dest_host] conn为连接成功的返回值
login_hostname_value = {}
def login(hostname,addr,conn,dest_host):
    global login_hostname_value
    print('login 调用')

    List = []
    List.append(1)
    List.append(addr)  # ip
    #List.append(addr)  # port
    List.append((conn))
    List.append(dest_host)
    print('List 生成完毕')
    login_hostname_value[hostname] = List
    print(hostname + '注册成功')

#测试 打印下 是否注册成功
def print_login():
    for key in login_hostname_value.keys():
        print(key)
        print(login_hostname_value[key][0])
        print(login_hostname_value[key][1]) #'    {ip,port}    '+
        #print('       ' + login_hostname_value[key][2])
        print( login_hostname_value[key][2]) #'    conn   ' +
        print(login_hostname_value[key][3])  #   dest_host

#根据用户名进行注销
def cancellation(hostname):
    del dict[hostname]

def tran_data(addr,conn,hostname_A):
    #获取 传输的文件名以及文件大小  格式是字符串的格式 文件名 文件大小 是以,隔开
    print("传输的文件名")
    conn.send('传输的文件名，文件的大小:'.encode('utf-8'))
    file_name_size = conn.recv(1024).decode('utf-8')
    file_name,file_size = file_name_size.split(',')

    # 生成文件路径
    file_path = os.path.join(BASE_DIR, file_name)
    print("接受文件的路径", file_path)
    print("接受文件的大小", file_size)

    # 1.先接收文件
    f = open(file_path, 'ab')  # 以二进制格式打开一个文件用于追加。如果该文件不存在，创建新文件进行写入。
    has_receive = 0  # 统计接收到的字节数
    while has_receive != file_size:
        data1 = conn.recv(1024)  # 一次从服务端接收1024字节的数据
        f.write(data1)  # 写入
        has_receive += len(data1)  # 更新接收到的字节数
    f.close()  # 关闭文件

    # 获取目标主机  的conn
    dest_host = login_hostname_value[hostname_A][3]
    dest_conn = login_hostname_value[dest_host][2]

    #开始转发

    dest_conn.send(file_name_size.decode('utf-8'))  # 发送目标文件名
    has_sent = 0  # 记录下已经发送的字节数
    fp = open(file_path, 'rb')
    while has_sent != file_size:  # 发送的字节数 不等于 图像的大小，则接着发送
        file = fp.read(1024)  # 一次读1024个字节
        dest_conn.send(file)
        has_sent += len(file)  # 更新已发送的字节数
    fp.close()  # 关闭文件



def tcplink(addr,conn ):
    print(f'客服端{addr}连接成功')
    #发送 一条消息 请发送 主机名
    succ = conn.send('请发送主机名:'.encode('utf-8'))
    if succ != 0:  #发送成功
        hostname_A = conn.recv(1024).decode('utf-8')
        succ1 = conn.send('请发送目标主机名:'.encode('utf-8'))
        if  succ1 != 0:
            destname_host_B = conn.recv(1024).decode('utf-8')
        while True:
            # 请发送想要的操作
            conn.send('请发送想要的操作:'.encode('utf-8'))
            data = int(conn.recv(1024).decode('utf-8'))
            print(data)
            if data == 1111:
                login(hostname_A, conn, addr,destname_host_B)
                print_login()
            elif data == 2222:
                conn.send('进行wifi检测目的地址:'.encode('utf-8'))
                login_hostname_value[hostname_A][0] = 0 # 把状态位 置为 0 说明正在 采用direct
                print_login()
                conn.send('3333:'.encode('utf-8'))  #因为是双方通信的 所以只有连续收到2次 3333 才可以
                destname_host_B = login_hostname_value[hostname_A][3]
                dest_conn_B = login_hostname_value[destname_host_B][2]
                dest_conn_B.send('3333:'.encode('utf-8')) #3333 第二次发送 ，收到之后双方 开始计时
            elif data == 4444:
                if login_hostname_value[hostname_A] == 0:  #由于DHCP的存在 分配的ip 地址可能发生变化 我要更新下
                    login_hostname_value[hostname_A][0] = 1
                    login_hostname_value[hostname_A][1] = addr
                    login_hostname_value[hostname_A][2] = conn
                tran_data(addr,conn,hostname_A)
            elif data == 5555: #用户注销
                cancellation(hostname_A)
                break
# Press the green button in the gutter to run the script.
while True:
    sock, addr = ser.accept()
    pthread = Thread(target=tcplink, args=(addr, sock))  # 多线程处理socket连接
    pthread.start()