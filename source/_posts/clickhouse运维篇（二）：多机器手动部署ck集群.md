
> 熟悉流程并且有真正部署需求可以看一下我的另一篇简化部署的文章，因为多节点配置还是比较麻烦的先要jdk、zookeeper，再ck，还有各种配置文件登录不同机器上手动改配置文件还挺容易出错的。  
> [clickhouse运维篇（三）：生产环境一键生成配置并快速部署ck集群](https://blog.csdn.net/qq_42873554/article/details/143367712?spm=1001.2014.3001.5501)

@[TOC](多机器手动部署ck集群)
# 1、 安装jdk

上传jdk安装包到各节点

1、解压安装包 （这里举例解压到/opt/jdk8u333）

2、 执行 sh setup.sh install

3、 修改环境变量

```
vi /etc/profile
```

vi /etc/profile

在文件末尾加

```
#java
export JAVA_HOME=/opt/jdk8u333
export CLASSPATH=.:${JAVA_HOME}/jre/lib/rt.jar:${JAVA_HOME}
export PATH=$PATH:${JAVA_HOME}/bin
```

4、 执行指令生效

```
source /etc/profile
```

# 2、 zookeeper集群搭建（选举机制，奇数节点部署）

举例三个节点：

172.168.1.206

172.168.1.207

172.168.1.208

上传安装包到各节点

解压安装包（这里举例解压到/opt/app/zookeeper-3.7.2）

1、创建目录

```
mkdir /opt/app/zookeeper-3.7.2/zkData

```

2、 复制zoo_sample.cfg文件命名为 zoo.cfg

```
cp zoo_sample.cfg zoo.cfg

```

3、 在各个节点创建一个id（距离下边在206、207、208三个节点的zkData目录下分别创建）

```
echo 1 >/opt/app/zookeeper-3.7.2/zkData/myid
echo 2 >/opt/app/zookeeper-3.7.2/zkData/myid
echo 3 >/opt/app/zookeeper-3.7.2/zkData/myid

```

4、修改zoo.cfg文件

```
vi zoo.cfg

```

clientPort为16871

dataDir为上边创建的zkData

server.后边的1、2、3为机器节点id；

**server.1=172.168.1.206:2888:3888**

**server.2=172.168.1.207:2888:3888**

**server.3=172.168.1.208:2888:3888**

```
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/opt/app/zookeeper-3.7.2/zkData
clientPort=16871
server.1=172.168.1.206:2888:3888
server.2=172.168.1.207:2888:3888
server.3=172.168.1.208:2888:3888

```

5、 在其余节点重复以上操作，在bin目录下执行启动脚本

```
sh zkServer.sh start

```

6、 查看集群状态

```bash
./zkServer.sh status
```

说明集群搭建完成，172.168.1.208是主节点

# 3、 clickhouse集群规划
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/03947ce021b24d4ca6c7d415aaac9a4a.png)


1. 根据集群部署分配的服务器进行预先考虑

a. 需要多少个分片  【多少台机器多少个分片，最好一个机器不要多分片，会导致查询的负载不平衡，导致短筒效应 (保证分片数<=机器数最佳)】

b. 每个分片多少个副本 【默认同一个分片的副本不要在同一个机器上，不能起到容灾作用，一般情况一个分片内两个实例即可，一主一副】

2. 同一个实例不能既是主分片又是副本分片，想要部署m分片每个分片内n个实例的集群就需要部署 m*n 个clickhouse实例。


3. 例如，所以如果只有三台机器，想部署3分片每个分片2实例的集群就需要3*2=6个 实例【遵循上面1.a中 分片数<=机器数】。 如果机器1上有了shard1的分片，副本实例就最好启动在机器2或者机器3上【遵循上面1.b中 同一分片副本不在相同机器】
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f686dfacc8cc44919f24180c12dd64f6.png)

# 4、 clickhouse集群搭建

举例三个节点：

172.168.1.206

172.168.1.207

172.168.1.208

上传安装包到各节点

1、解压安装包 （这里举例解压到/opt/app/clickhouse-23.4.2.9)

2、 修改配置文件，打开config目录

```
cd config
vi config.xml

```

3、 修改config.xml文件

设置clickhouse端口16860

打开所有地址监听

tcp端口默认9000（可以按需修改）

```
<http_port>16860</http_port>
<listen_host>::</listen_host>
<tcp_port>9000</tcp_port>
```

添加集群节点信息 【三机器两分片、每个分片两个实例的配置文件】

```
// clickhose xml需要修改的内容
    <remote_servers>
        <!-- 可自定义clickhouse集群名 -->
        <ck_cluster>
            <!-- 数据分片1  -->
            <shard>
                <internal_replication>true</internal_replication>
                <!-- 副本1 -->
                <replica>
                    <host>172.168.1.206</host>
                    <port>9000</port>
                    <user>default</user>
                    <password>my_password</password>
                </replica>
                <!-- 副本2 -->
                <replica>
                    <host>172.168.1.207</host>
                    <port>9000</port>
                    <user>default</user>
                    <password>my_password</password>
                </replica>
            </shard>
            <!-- 数据分片2  -->
            <shard>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>172.168.1.207</host>
                    <port>9001</port>
                    <user>default</user>
                    <password>my_password</password>
                </replica>
                <replica>
                    <host>172.168.1.208</host>
                    <port>9000</port>
                    <user>default</user>
                    <password>my_password</password>
                </replica>
            </shard>

        </ck_cluster>
    </remote_servers>

    <macros>
        <shard>02</shard>
        <replica>replica_208</replica>
    </macros>

    <zookeeper>
        <!-- index内容为server.id -->
        <node index="1">
            <host>172.168.1.206</host>
            <port>16871</port>
        </node>
        <node index="2">
            <host>172.168.1.207</host>
            <port>16871</port>
        </node>
        <node index="3">
            <host>172.168.1.208</host>
            <port>16871</port>
        </node>
    </zookeeper>

		<!-- 如果一个机器上部署多个实例这几个端口不要冲突 -->
    <http_port>16860</http_port>
    <tcp_port>9000</tcp_port>
    <interserver_http_host>172.168.1.208</interserver_http_host>
		<interserver_http_port>9009</interserver_http_port>
    <http>
        <max_connections>1024</max_connections>
        <async_insert>1</async_insert> <!-- 启用异步插入 -->
    </http>

		<!-- vim下输入 /clickhouse-23.4  查找path相关tag是否配置正确		-->										<path>/opt/app/my_app-2.4/clickhouse-23.4.2.9/data/</path>
		  <format_schema_path>/opt/app/my_app-2.4/clickhouse-23.4.2.9/data/format_schemas/</format_schema_path>
		    <log>/opt/app/my_app-2.4/clickhouse-23.4.2.9/log/clickhouse-server/clickhouse-server.log</log>
		    <errorlog>/opt/app/my_app-2.4/clickhouse-23.4.2.9/log/clickhouse-server/clickhouse-server.err.log</errorlog>
		    <tmp_path>/opt/app/my_app-2.4/clickhouse-23.4.2.9/tmp/</tmp_path>
		    <user_files_path>/opt/app/my_app-2.4/clickhouse-23.4.2.9/data/user_files/</user_files_path>

```

4、修改users.xml文件

设置default账号的密码

```
<password>my_password</password>
```

5、其余节点重复以上步骤，然后启动服务（注意修改config.xml中的<macros>值）

```
/opt/app/my_app-2.4/clickhouse-23.4.2.9/bin/clickhouse server --config-file /opt/app/my_app-2.4/clickhouse-23.4.2.9/config/config.xml --pid-file /opt/app/my_app-2.4/clickhouse-23.4.2.9/clickhouse.pid --daemon
```

# 5、 配置nginx代理

编辑nginx配置文件底部加入clickhouse反向代理供web服务调用

```bash
$ vim  /opt/app/my_app-2.4/nginx/conf/my_app.conf

upstream clickhouse_cluster {
    server 172.168.1.206:16860;
    server 172.168.1.207:16860;
    server 172.168.1.207:16861;    
    server 172.168.1.208:16860;
}

# 新增的 ClickHouse 反向代理并配置相应的黑白名单策略， 入的流量应该是访问ck集群的流量，
# 所以应该是访问源的网段也就是my_app对应的网段或者ip
server {
    listen 1442;
    allow localhost;
	 allow 192.168.13.0/24;
	 allow 10.1.5.0/16;    
    deny all;

    location / {
        proxy_pass http://clickhouse_cluster;
    }
}
```

● nginx反向代理验证

```
[root@localhost ~]# curl localhost:1442
Ok.
```

# 6、 集群验证

这里使用dbever工具验证

1、执行sql，查看ck集群节点状态

```
SELECT * from system.clusters;
```
2、执行sql，查看zookeeper中/clickhouse的节点是否存在
```
SELECT * FROM system.zookeeper WHERE path = '/clickhouse';
```

如果截图如上则表示分布式集群部署成功
 查看各个节点状态，关注最后一列可以看出各个节点的与集群的连接状况【比如第三行数字22就是实例与cluster连接有问题】


# 7、 分布式，本地表测试

- 语句加`on cluster ck_cluster` 就是在所有实例上执行

创建一个表
```
-- 删除本地表
DROP TABLE IF EXISTS test_table_local on cluster ck_cluster SYNC;

-- 创建本地表
CREATE TABLE test_table_local ON CLUSTER ck_cluster
(
    `tenantId`        UInt64 CODEC (Delta(8), ZSTD(1)),
    `alarmId`         String,
    `grade`           Int32,
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{uuid}/{shard}/audit_log_local', '{replica}');


-- 删除分布式表
DROP TABLE IF EXISTS test_table_all on cluster ck_cluster SYNC;
-- 创建分布式表
CREATE TABLE test_table_all ON CLUSTER ck_cluster as test_table_local ENGINE = Distributed('ck_cluster', 'default', 'test_table_local', rand());
```

分布式表测试
```
SELECT count(*) FROM test_table_all;
```
本地表测试

```
INSERT INTO test_table_local (id, name, grade) VALUES (1,'jack',60);
```
