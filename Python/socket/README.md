# Socket 简单编程

### Socket 类型

套接字格式：socket(family, type[,protocal]) 使用给定的套接族，套接字类型，协议编号（默认为 0）来创建套接字

| socket 类型        | 描述                             |
| :----------------- | :------------------------------- |
| socket.AF_INET     | 用于服务器与服务器之间的网络通信 |
| socket.SOCK_STREAM | 基于 TCP 的流式 socket 通信      |
| socket.SOCK_DGRAM  | 基于 UDP 的数据报式 socket 通信  |

### Socket 个别选项

* 获取方法 socketed.getsockopt(protocal_level, socket.opt) protocal_level 为协议层，opt 为选项
* 设置方法 socketed.setsockopt(protocal_level, socket.opt, val)

  | 协议层             | 选项         | 可读取 | 可设置 |
  | :----------------- | :----------- | :----- | :----- |
  | socket.SOL_SOCKET  | SO_SNDBUF    | √      | √      |
  | socket.SOL_SOCKET  | SO_RCVBUF    | √      | √      |
  | socket.SOL_SOCKET  | SO_REUSEADDR | √      | √      |
  | socket.IPPROTO_IP  | IP_TTL       | √      | √      |
  | socket.IPPROTO_TCP | TCP_NODELAY  | √      | √      |
  | socket.SOL_SOCKET  | TCP_MAXSEG   | √      | √      |

创建 TCP Socket：

```Python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

创建 UDP Socket：

```Python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

### Socket 简单流程

**TCP 服务器**
1、创建套接字，绑定套接字到本地 IP 与端口

```Python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind()
```

2、开始监听链接

```Python
s.listen()
```

3、进入循环，不断接受客户端的链接请求

```Python
While True:
    s.accept()
```

4、接收客户端传来的数据，并且发送给对方发送数据

```Python
s.recv(max_buffsize)  # max_buffsize为缓冲大小
s.sendall()
```

5、传输完毕后，关闭套接字

```Python
s.close()
```

**TCP 客户端**
1、创建套接字并链接至远端地址

```Python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect()
```

2、链接后发送数据和接收数据

```Python
s.sendall()
s.recv(max_buffsize)
```

3、传输完毕后，关闭套接字

```Python
s.close()
```

### TCP Socket 简单实例

```Python
# TCP 服务端
import socket

HOST = ''                 # 如果地址为空，则监听所有网络接口数据
PORT = 50007              # 监听的端口
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)



# TCP 客户端
import socket

HOST = 'server ip'          # 服务端ip
PORT = 50007                # 服务端端口
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)
print('Received', repr(data))
```

### UDP Socket 简单实例

```Python
## 服务端
import socket  

address = ('127.0.0.1', 31500)  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
s.bind(address)  

while True:  
    data, addr = s.recvfrom(2048)  
    if not data:
        break  
    print("from {} received data: {} ".format(addr, data))

s.close()  


## 客户端
import socket  

address = ('127.0.0.1', 31500)  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  

while True:  
    msg = raw_input()  
    if not msg:  
        break  
    s.sendto(msg, address)  

s.close()

# 已连接的客户端
# 优势：传输速度快
import socket

HOST='192.168.1.60'  
PORT=9999  

s = socket(AF_INET,SOCK_DGRAM)  
s.connect((HOST,PORT))  
while True:  
    message = raw_input('send message:>>')  
    s.sendall(message)  
    data = s.recv(1024)  
    print(data)

s.close()
```

### 使用扩展

* TCP 连接后如果意外断开会产生 TIME-WAIT，而这个 TIME-WAIT 时间会比较长，对于服务器来说影响较大，可以设置`s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`则可以将 TIME-WAIT 状态的套接字重新分配
* Nagle 算法，传输过程是先发送`N`得到回应后再发送`agle`, 再传输大文件/装满输出缓冲时，可以禁用 Nagle 算法，从而提高传输速度，例如网络视频；一般情况下，这个算法可以提高速度，但如果无条件放弃使用 Nagle 算法，就会增加过多的网络流量，影响传输；因此，未能准确判断数据特性时，不应该禁用 Nagle。`s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # 禁用Nagle算法`
* buff size 个人理解：套接字是唯一的，当装满缓冲时，socket 会取出，刷新缓冲
  * 可以创建`collections`中 `defaultdict`字典来存储未接收完的数据`dict_data[conn].append(recv_data)`
  * 当数据接收完后，则可以将对应的键值 del
  * 也可以使用`struct`来处理
* UDP 传输，如果服务端时固定的 IP 和端口。建议使用已连接的 UDP
