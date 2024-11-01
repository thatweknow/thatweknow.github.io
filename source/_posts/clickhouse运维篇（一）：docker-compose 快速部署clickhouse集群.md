---
title: clickhouse运维篇（一）：docker-compose 快速部署clickhouse集群.
date: 2024-09-27 19:25:00
toc: true
mathjax: false
categories: 运维
tags:
  - 后端
  - 运维
---   


## 前提条件
**注意事项：**
1. **镜像版本号注意保持一致   [zookeeper:3.7,   clickhouse/clickhouse-server:22.5.4]**
2. config里面的参数有些是必须的，日志报错缺少参数去官方文档里找 [config.xm参数官网](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings) 


在开始之前，请确保您的系统已经安装了以下工具：
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 目录结构

首先，我们需要为 ClickHouse 集群创建目录结构来存放数据和配置文件。执行以下命令来创建目录：

```bash
mkdir -p clickhouse_cluster/{zk/data1,zk/data2,zk/data3,zk/datalog1,zk/datalog2,zk/datalog3,ck/data/clickhouse01,ck/data/clickhouse02,ck/data/clickhouse03,ck/config/clickhouse01,ck/config/clickhouse02,ck/config/clickhouse03}
```

## 第一步：编写 `docker-compose.yml` 文件

在 `clickhouse_cluster` 目录下创建 `docker-compose.yml` 文件，这个文件定义了 ZooKeeper 和三个 ClickHouse 节点。为了安全性，我们会替换敏感数据如密码。

```yaml
version: '3.8'
# localhost:2181,localhost:2182,localhost:2183
services:
  nginx:
    image: nginx:latest
    container_name: nginx_server
    restart: no
    ports:
      - "80:80"        # 映射80端口，用于HTTP服务
      - "443:443"      # 映射443端口，用于HTTPS服务
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf   # 挂载自定义的 Nginx 配置文件
      - ./nginx/logs:/var/log/nginx                # 挂载日志目录
      - ./nginx/certs:/etc/nginx/certs             # 挂载证书目录（用于HTTPS）

  zookeeper1:
    image: zookeeper:3.7
    hostname: zookeeper1
    container_name: zookeeper1
    restart: no
    ports:
      - "2181:2181"
      - "2888:2888"  # 集群通信端口
      - "3888:3888"  # 选举端口
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2181 server.3=zookeeper3:2888:3888;2181
    volumes:
      - ./zk/data1:/data
      - ./zk/datalog1:/datalog

  zookeeper2:
    image: zookeeper:3.7
    hostname: zookeeper2    
    container_name: zookeeper2
    restart: no
    ports:
      - "2182:2181"
      - "2889:2888"  # 集群通信端口
      - "3889:3888"  # 选举端口
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2181 server.3=zookeeper3:2888:3888;2181
    volumes:
      - ./zk/data2:/data
      - ./zk/datalog2:/datalog
        

  zookeeper3:
    image: zookeeper:3.7
    hostname: zookeeper3    
    container_name: zookeeper3
    restart: no
    ports:
      - "2183:2181"
      - "2890:2888"  # 集群通信端口
      - "3890:3888"  # 选举端口
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zookeeper1:2888:3888;2181 server.2=zookeeper2:2888:3888;2181 server.3=zookeeper3:2888:3888;2181
    volumes:
      - ./zk/data3:/data
      - ./zk/datalog3:/datalog

  clickhouse01:
    image: clickhouse/clickhouse-server:23.4.2
    container_name: clickhouse01
    hostname: clickhouse01
    restart: no
    ports:
      - "8123:8123"   # HTTP接口
      - "9000:9000"   # TCP接口
      - "9009:9009"   # Internode通信接口
    volumes:
      - ./ck/data/clickhouse01:/var/lib/clickhouse
      - ./ck/config/clickhouse01:/etc/clickhouse-server
      # - ./config/clickhouse01/users.xml:/etc/clickhouse-server/users.d/default-user.xml
    environment:
      CLICKHOUSE_DB: default
      # CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: "your_secure_password"
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3

  clickhouse02:
    image: clickhouse/clickhouse-server:23.4.2
    container_name: clickhouse02
    hostname: clickhouse02    
    restart: no
    ports:
      - "8124:8123"   # HTTP接口
      - "9001:9000"   # TCP接口
      - "9010:9009"   # Internode通信接口
    volumes:
      - ./ck/data/clickhouse02:/var/lib/clickhouse
      - ./ck/config/clickhouse02:/etc/clickhouse-server
    environment:
      CLICKHOUSE_DB: default
      # CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: "your_secure_password"
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3

  clickhouse03:
    image: clickhouse/clickhouse-server:23.4.2
    container_name: clickhouse03
    hostname: clickhouse03        
    restart: no
    ports:
      - "8125:8123"   # HTTP接口
      - "9002:9000"   # TCP接口
      - "9011:9009"   # Internode通信接口
    volumes:
      - ./ck/data/clickhouse03:/var/lib/clickhouse
      - ./ck/config/clickhouse03:/etc/clickhouse-server
    environment:
      CLICKHOUSE_DB: default
      # CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: "your_secure_password"
    depends_on:
      - zookeeper1
      - zookeeper2
      - zookeeper3
```

### 关键点说明：

- **Zookeeper**：Zookeeper 用于协调 ClickHouse 集群中的分布式事务。
- **ClickHouse 节点**：我们设置了三个 ClickHouse 节点（`clickhouse01`、`clickhouse02` 和 `clickhouse03`），它们通过不同的端口进行通信。
- **密码**：为了安全性，密码使用占位符 `"your_secure_password"`，请确保使用强密码替换。

## 第二步：编写 ClickHouse 配置文件

接下来，创建每个 ClickHouse 节点的配置文件。以 `config/clickhouse01/config.xml` 为例，其他节点的配置类似。我们将替换原始文件中的敏感信息。

在 `clickhouse_cluster/config/clickhouse01` 目录下创建 `config.xml` 文件：

```xml
<yandex>
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <readonly>0</readonly>
        </default>
    </profiles>

    <path>/var/lib/clickhouse/</path>
    <tmp_path>/var/lib/clickhouse/tmp/</tmp_path>
    <user_files_path>/var/lib/clickhouse/user_files/</user_files_path> 
    <http_port>8123</http_port> 

    <logger>
        <log>/var/log/clickhouse-server/clickhouse.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse_error.log</errorlog>
    </logger>

    <format_schema_path>/var/lib/clickhouse/format_schemas/</format_schema_path>
    <default_profile>default</default_profile>
    <users_config>users.xml</users_config>
    <mark_cache_size>5368709120</mark_cache_size>

    <zookeeper>
	    <!-- index内容为server.id -->
	    <node index="1">
	        <host>zookeeper1</host>
	        <port>2181</port>
	    </node>
	    <node index="2">
	        <host>zookeeper2</host>
	        <port>2181</port>
	    </node>
	    <node index="3">
	        <host>zookeeper3</host>
	        <port>2181</port>
	    </node>        
    </zookeeper>

    <remote_servers>
        <my_clickhouse_cluster>
            <shard>
                <replica>
                    <host>clickhouse01</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse02</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>clickhouse03</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>clickhouse04</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>clickhouse05</host>
                    <port>9000</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>clickhouse06</host>
                    <port>9000</port>
                </replica>
            </shard>            
        </my_clickhouse_cluster>
    </remote_servers>

    <listen_host>::</listen_host>
    <listen_host>0.0.0.0</listen_host>
</yandex>
```

### 关键配置说明：

- **ZooKeeper**：配置了 ClickHouse 连接 Zookeeper，使用 `zookeeper1:2181\zookeeper1:2181\zookeeper1:2181` 地址。
- **集群配置**：`remote_servers` 配置了集群中的三个节点，分别对应 `clickhouse01`、`clickhouse02` 和 `clickhouse03`。

## 第三步：编写 `users.xml` 文件

在 `config/clickhouse01/` 目录下创建 `users.xml` 文件，用于定义用户及其权限。为了安全起见，密码将以占位符形式存在。

```xml
<?xml version="1.0"?>
<yandex>
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <use_uncompressed_cache>0</use_uncompressed_cache>
            <load_balancing>random</load_balancing>
        </default>
    </profiles>

    <users>
        <default>
            <password>your_secure_password</password>
            <!-- Password could be specified in plaintext or in SHA256 (in hex format).

                 If you want to specify password in plaintext (not recommended), place it in 'password' element.
                 Example: <password>qwerty</password>.
                 Password could be empty.

                 If you want to specify SHA256, place it in 'password_sha256_hex' element.
                 Example: <password_sha256_hex>65e84be33532fb784c48129675f9eff3a682b27168c0ea744b2cf58ee02337c5</password_sha256_hex>

                 How to generate decent password:
                 Execute: PASSWORD=$(base64 < /dev/urandom | head -c8); echo "$PASSWORD"; echo -n "$PASSWORD" | sha256sum | tr -d '-'
                 In first line will be password and in second - corresponding SHA256.
                 也可以使用加密的密码，用上面的shell命令就可以生成
            -->
            <!-- <password_double_sha1_hex></password_double_sha1_hex> -->
			
            <networks incl="networks" replace="replace">
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>

        <readonly_user>
            <password>your_readonly_password</password>
            <networks incl="networks" replace="replace">
                <ip>::/0</ip>
            </networks>
            <profile>readonly</profile>
            <quota>default</quota>
        </readonly_user>
    </users>
</yandex>
```

### 用户权限说明：

- `default` 用户具有默认的读写权限。
- `readonly_user` 用户具有只读权限，并且可以从任意 IP 访问。

## 第四步：启动 ClickHouse 集群

在 `clickhouse_cluster` 目录下，运行以下命令来启动整个集群：

```bash
docker-compose up -d
```

`docker-compose up -d` 将启动所有服务，包括 ZooKeeper 和六个 ClickHouse 节点。

## 第五步：验证集群部署

 1. 1.运行以下命令查看容器状态：
    ```bash
    docker-compose ps
    ```

    确保所有容器都处于 "Up" 状态。

2. 2.通过 HTTP 接口访问任意 ClickHouse 节点，查看是否可以成功连接：

    ```bash
    curl http://localhost:8123
    ```

    返回类似于 `Ok.` 的响应即表示成功。
3. 3.从单节点查询集群状态
	```bash
	docker exec -it clickhouse01 bash 
	clickhouse-client
	
	select * from system.clusters;
	select * from system.zookeeper where path='/clickhouse';
	```
![在这里插入图片描述](https://raw.githubusercontent.com/Bit-urd/image-cloud/refs/heads/master/image-gp/20241101184800_dfc947f0-4201-4972-9762-541afea7ab01.png)
## 六：配置nginx反向代理实现ck集群负载均衡的读写
```
worker_processes auto;
events {
    worker_connections 1024;  # 设置工作进程的最大连接数
}
http {
    upstream clickhouse_cluster {
        server localhost:8123 max_fails=3 fail_timeout=30s;
        server localhost:8124 max_fails=3 fail_timeout=30s;
        server localhost:8125 max_fails=3 fail_timeout=30s;
    }
    server {
        listen 8080;
        location / {
            proxy_pass http://clickhouse_cluster;
        }
    }
}
```
## 七：文件夹结构

![在这里插入图片描述](https://raw.githubusercontent.com/Bit-urd/image-cloud/refs/heads/master/image-gp/20241101184806_0c793390-74e1-4cdd-9646-c233f6f27402.png)






参考链接：
https://www.cnblogs.com/yoyo1216/p/13731225.html
https://www.cnblogs.com/syw20170419/p/16250500.html
https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings
