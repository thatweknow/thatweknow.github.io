---
title: clickhouse运维篇（三）：生产环境一键生成配置并快速部署ck集群.
date: 2024-09-29 13:15:00
top: true
cover: true
toc: true
mathjax: false
categories: 运维
tags:
  - 后端
  - 运维
---   


![请添加图片描述](https://raw.githubusercontent.com/Bit-urd/image-cloud/refs/heads/master/image-gp/20241101184811_fcf9cfcc-6fa3-468f-9355-8d671d6e165d.png)

> 前提条件：先了解集群搭建流程是什么样，需要改哪些配置，有哪些环境，这个文章目的是简化部署。 

[clickhouse运维篇（一）：docker-compose 快速部署clickhouse集群](https://blog.csdn.net/qq_42873554/article/details/142646374)
[clickhouse运维篇（二）：多机器手动部署ck集群](https://blog.csdn.net/qq_42873554/article/details/143368665?sharetype=blogdetail&sharerId=143368665&sharerefer=PC&sharesource=qq_42873554&spm=1011.2480.3001.8118)

!https://raw.githubusercontent.com/Bit-urd/image-cloud/refs/heads/master/image-gp/20241101184811_fcf9cfcc-6fa3-468f-9355-8d671d6e165d.png

# 项目目录解析：

```bash
 $ tree .
.
├── cluster.conf   #集群配置，  集群包含哪些机器、端口分别为多少
├── config  
│   ├── config_node1.xml  # 生成的ck节点配置文件
│   ├── config_node2.xml
│   ├── config_template.xml  # config模版
│   ├── users_node1.xml     # 生成的ck节点用户配置文件
│   ├── users_node2.xml
│   └── users_template.xml   # users模版
├── dep   #下面包含需要的远程依赖， zookeeper、clickhouse、jdk，根据自己的需求更改
├── gen_cluster_config.sh  
├── gen_login_cmd.sh
├── install.conf  # 远程登录的主机conf，需要在跳板机或者中间机器上去ssh、scp使用
└── main.sh   #启动入口
```

# 1、main.sh

```bash
CUR_FOLDER=$(cd "/Users/admin/scripts/my_app/ckcluster";pwd)

. ${CUR_FOLDER}/cluster.conf
. ${CUR_FOLDER}/gen_cluster_config.sh
. ${CUR_FOLDER}/gen_login_cmd.sh

CONFIG_FOLDER="${CUR_FOLDER}/config"
DEP_FOLDER="${CUR_FOLDER}/dep"
TEMPLATE_FILE="${CONFIG_FOLDER}/config_template.xml"

if [ ! -d "$CONFIG_FOLDER" ]; then
    mkdir -p "$CONFIG_FOLDER"
fi

if [ ! -d "$DEP_FOLDER" ]; then
    mkdir -p "$DEP_FOLDER"
fi

zk_index=1
# 首先读取所有节点信息并根据 shard 进行分组
while true; do
    host_var="zk_node_${zk_index}_host"

    # 检查所有变量是否为空，若有一个为空则跳出循环
    if [ -z "${!host_var}" ]; then
        break
    fi
    # 远程安装jdk、zookeeper

    install_path=$(get_install_path ${!host_var})
    echo $(get_scp_command ${!host_var} . "${DEP_FOLDER}/jdk-8u202-nonroot.tar.gz ${DEP_FOLDER}/apache-zookeeper-3.7.2-bin.tar.gz")
    `get_scp_command ${!host_var} . "${DEP_FOLDER}/jdk-8u202-nonroot.tar.gz ${DEP_FOLDER}/apache-zookeeper-3.7.2-bin.tar.gz"`

    echo $(get_ssh_command ${!host_var} "cd ${install_path};tar -xzvf ${install_path}/jdk-8u202-nonroot.tar.gz")
    echo $(get_ssh_command ${!host_var} "cd ${install_path};tar -xzvf ${install_path}/apache-zookeeper-3.7.2-bin.tar.gz")
    `get_ssh_command ${!host_var} "cd ${install_path};tar -xzvf ${install_path}/jdk-8u202-nonroot.tar.gz"`
    `get_ssh_command ${!host_var} "cd ${install_path};tar -xzvf ${install_path}/apache-zookeeper-3.7.2-bin.tar.gz"`
    
    zk_index=$((zk_index + 1))
done

# 生成ck集群配置文件
gen_config

# 远程安装clickhouse
ck_index=1
# 首先读取所有节点信息并根据 shard 进行分组
while true; do
    host_var="ck_node_${ck_index}_host"

    # 检查所有变量是否为空，若有一个为空则跳出循环
    if [ -z "${!host_var}" ]; then
        break
    fi
#     <users_config>/opt/appaduudit/my_app-2.4/clickhouse-23.4.2.9/ck_node_1/config/users_node.xml</users_config>    
    install_path=$(get_install_path ${!host_var})    
    `get_scp_command ${!host_var} . "${DEP_FOLDER}/clickhouse-23.4.2.9.tar.gz"`
    echo $(get_ssh_command ${!host_var} "cd ${install_path};tar -xzvf ${install_path}/clickhouse-23.4.2.9.tar.gz")

    NODE_CK_PATH="${BASE_CK_PATH}/ck_node_${ck_index}"
    echo $(get_scp_command ${!host_var} ${NODE_CK_PATH}/config  "${CONFIG_FOLDER}/user_node${ck_index}.xml")
    `get_scp_command ${!host_var} ${NODE_CK_PATH}/config "${CONFIG_FOLDER}/config_node${ck_index}.xml"`
    `get_scp_command ${!host_var} ${NODE_CK_PATH}/config  "${CONFIG_FOLDER}/users_node${ck_index}.xml"`

    echo $(get_ssh_command ${!host_var} "${install_path}/clickhouse-23.4.2.9.tar.gz/bin/clickhouse server --config-file  ${install_path}/config_node${ck_index}.xml")
    `get_ssh_command ${!host_var} "${install_path}/clickhouse-23.4.2.9.tar.gz/bin/clickhouse server --config-file  ${install_path}/config_node${ck_index}.xml"`    
    
    ck_index=$((ck_index + 1))
done
```

# 2、cluster.conf

```bash
# 定义变量
target_install_path="/opt/app/ck_cluster"
BASE_CK_PATH="/opt/app/my_app-2.4/clickhouse-23.4.2.9"
CK_CLUSTER_NAME="my_ck_cluster_test"

#port为zk的clientPort
zk_node_1_host=172.168.1.206
zk_node_1_port=8551

zk_node_2_host=172.168.1.207
zk_node_2_port=8551

zk_node_3_host=172.168.1.208
zk_node_3_port=8551

ck_node_1_host=172.168.1.206
ck_node_1_tcp_port=8601
ck_node_1_http_port=8602
ck_node_1_interserver_http_port=8603
ck_node_1_user=default
ck_node_1_password=password
ck_node_1_shard=01
ck_node_1_replica=replica_63

ck_node_2_host=172.168.1.207
ck_node_2_tcp_port=8611
ck_node_2_http_port=8612
ck_node_2_interserver_http_port=8613
ck_node_2_user=default
ck_node_2_password=password
ck_node_2_shard=02
ck_node_2_replica=replica_63

#ck_node_3_host=ck_host_3
#ck_node_3_tcp_port=ck_tcp_port_3
#ck_node_3_http_port=ck_http_port_3
#ck_node_3_interserver_http_port=ck_interserver_http_port_3
#ck_node_3_user=user3
#ck_node_3_password=password3
#ck_node_3_shard=02
#ck_node_3_replica=replica_209
```

# 3、install.conf

```bash
ssh.172.168.1.206=root:app:/opt/app/ck_cluste
ssh.172.168.1.207=admin:adminpass:/opt/app/ck_cluste
ssh.172.168.1.208=admin:adminpass:/opt/app/ck_cluste
```

# 4、gen_login_cmd.sh

```bash
#!/bin/bash
cd /Users/admin/scripts/my_app/ckcluster
# 读取配置文件并解析
CONFIG_FILE="install.conf"
declare -A HOSTS

while IFS='=' read -r key user_password || [[ -n "$key" ]]; do
    key=$(echo "$key" | xargs)
    user_password=$(echo "$user_password" | xargs)
    if [[ $key == ssh.* ]]; then
        host=${key#ssh.}
        HOSTS["$host"]="$user_password"
    fi
done < "$CONFIG_FILE"

# 获取 SSH 命令
get_ssh_command() {
    local host=$1
    local cmd=$2
    local user_password=${HOSTS["$host"]}
    IFS=':' read -r user password install_path<<< "$user_password"
    # echo "sshpass -p '$password' ssh $user@$host $cmd"
    echo "sshpass -p '$password' ssh $user@$host \"$cmd\""

}

# 获取 SCP 命令
get_scp_command() {
    local host=$1
    local extra_dir=$2
    local files=$3    
    local user_password=${HOSTS[$host]}
    
    # root:idss:/opt/idss/ck_cluste
    IFS=':' read -r user password install_path<<< "$user_password"

    if [ "$extra_dir" != "." ]; then
        install_path=$extra_dir
    fi
    mkdir_cmd=$(get_ssh_command $host "mkdir -p $install_path")
    eval "$mkdir_cmd"
    echo "sshpass -p '$password' scp -r $files $user@$host:$install_path"
}

get_install_path() {
    local host=$1
    local user_password=${HOSTS[$host]}
    
    # root:idss:/opt/idss/ck_cluste
    IFS=':' read -r user password install_path<<< "$user_password"
    echo $install_path
}
# ssh_command=$(get_scp_command "10.87.102.206" "/Users/admin/scripts/my_app/ckcluster/dep/jdk-8u202-nonroot.tar.gz /Users/admin/scripts/my_app/ckcluster/dep/apache-zookeeper-3.7.2-bin.tar.gz")
# echo $ssh_command
# scp_command=$(get_ssh_command "10.87.102.206" "ls /opt/idss/ck_cluste")
# echo $scp_command
# `$scp_command`
```

# 5、gen_cluster_config.sh

```bash
#!/bin/bash
# 定义基础路径和模板文件名

function gen_config() {

# 生成 zookeeper 配置
ZOOKEEPER_CONFIG="<zookeeper>\n"
# 循环遍历 zk_node_*_host 和 zk_node_*_port 变量
zk_index=1
while true; do
    host_var="zk_node_${zk_index}_host"
    port_var="zk_node_${zk_index}_port"
    # 检查变量是否已定义，如果未定义则跳出循环
    if [ -z "${!host_var}" ] || [ -z "${!port_var}" ]; then
        break
    fi
    
    ZOOKEEPER_CONFIG+="    <node index=\"${zk_index}\">\n"
    ZOOKEEPER_CONFIG+="        <host>${!host_var}</host>\n"
    ZOOKEEPER_CONFIG+="        <port>${!port_var}</port>\n"
    ZOOKEEPER_CONFIG+="    </node>\n"
    
    zk_index=$((zk_index + 1))
done
ZOOKEEPER_CONFIG+="</zookeeper>"

# 生成 remote_servers 配置
declare -A shard_nodes config_content

ck_index=1
# 首先读取所有节点信息并根据 shard 进行分组
while true; do
    host_var="ck_node_${ck_index}_host"
    tcp_port_var="ck_node_${ck_index}_tcp_port"
    http_port_var="ck_node_${ck_index}_http_port"
    interserver_port_var="ck_node_${ck_index}_interserver_http_port"
    user_var="ck_node_${ck_index}_user"
    password_var="ck_node_${ck_index}_password"
    shard_var="ck_node_${ck_index}_shard"
    replica_var="ck_node_${ck_index}_replica"

    # 检查所有变量是否为空，若有一个为空则跳出循环
    if [ -z "${!host_var}" ] || \
       [ -z "${!tcp_port_var}" ] || \
       [ -z "${!http_port_var}" ] || \
       [ -z "${!interserver_port_var}" ] || \
       [ -z "${!user_var}" ] || \
       [ -z "${!password_var}" ] || \
       [ -z "${!shard_var}" ] || \
       [ -z "${!replica_var}" ]; then
        break
    fi

    # 将当前节点信息存入以 shard 为 key 的数组
    shard_nodes["${!shard_var}"]+=$(cat <<-NODE
            <replica>
                <host>${!host_var}</host>
                <port>${!tcp_port_var}</port>
                <user>${!user_var}</user>
                <password>${!password_var}</password>
            </replica>\n
NODE
    )
    NODE_CK_PATH="${BASE_CK_PATH}/ck_node_${ck_index}"

    config_template=$(cat ${CONFIG_FOLDER}/config_template.xml)
    config_template=$(echo "$config_template" | sed "s|\${BASE_CK_PATH}|${NODE_CK_PATH}|g")
    config_template=$(echo "$config_template" | sed "s|\${HTTP_PORT}|${!http_port_var}|g")
    config_template=$(echo "$config_template" | sed "s|\${TCP_PORT}|${!tcp_port_var}|g")
    config_template=$(echo "$config_template" | sed "s|\${INTERSERVER_HTTP_PORT}|${!interserver_port_var}|g")
    config_template=$(echo "$config_template" | sed "s|\${MACROS_SHARD}|${!shard_var}|g")
    config_template=$(echo "$config_template" | sed "s|\${MACROS_REPLICA}|${!replica_var}|g")
    config_template=$(echo "$config_template" | sed "s|\${CK_PASSWORD}|${!password_var}|g")    
    config_template=$(echo "$config_template" | sed "s|\${ck_index}|${!ck_index}|g")        
    # 将生成的配置内容存入字典
    config_content["config_node${ck_index}"]="$config_template"

    # users文件生成
    users_template=$(cat ${CONFIG_FOLDER}/users_template.xml)
    users_template=$(echo "$users_template" | sed "s|\${CK_PASSWORD}|${!password_var}|g")    
    echo -e "$users_template" > "${CONFIG_FOLDER}/users_node${ck_index}.xml"
    ck_index=$((ck_index + 1))
done

# 构建最终的 XML 配置
REMOTE_SERVERS_CONFIG="<remote_servers>\n"
REMOTE_SERVERS_CONFIG+="    <${CK_CLUSTER_NAME}>\n"
for shard in "${!shard_nodes[@]}"; do
    REMOTE_SERVERS_CONFIG+="        <shard>\n"
    REMOTE_SERVERS_CONFIG+="            <internal_replication>true</internal_replication>  \n"
    REMOTE_SERVERS_CONFIG+="${shard_nodes[$shard]}"
    REMOTE_SERVERS_CONFIG+="        </shard>\n"
done
REMOTE_SERVERS_CONFIG+="    </${CK_CLUSTER_NAME}>\n"
REMOTE_SERVERS_CONFIG+="</remote_servers>"

# 动态修改配置文件（插入 Zookeeper\CK集群 配置）
for node_config in "${!config_content[@]}"; do
    echo "处理 $node_config ..."

    # 创建临时文件
    temp_file="${node_config}_tmp.xml"
    echo -e "${config_content[$node_config]}" > "$temp_file"

    sed -i '' '/<\/yandex>/d' "$temp_file"
    # linux下为
    # sed -i '/<\/yandex>/d' "$temp_file"    

    # 拼接 Zookeeper 和 Remote Servers 配置
    combined_insert="${ZOOKEEPER_CONFIG}
${REMOTE_SERVERS_CONFIG}"

    echo -e "$combined_insert" >> "$temp_file"
    echo "</yandex>" >> "$temp_file"
    
    mv "$temp_file" "$CONFIG_FOLDER/${node_config}.xml"

    echo "生成 $node_config 完成: ${node_config}.xml"
done

}
```

# 6、config_template.xml

```bash
<?xml version="1.0"?>
<yandex>
    <logger>
        <level>notice</level>
        <log>${BASE_CK_PATH}/log/clickhouse-server.log</log>
        <errorlog>${BASE_CK_PATH}/log/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>
    <path>${BASE_CK_PATH}/data/</path>
    <tmp_path>${BASE_CK_PATH}/tmp/</tmp_path>
    <user_files_path>${BASE_CK_PATH}/data/user_files/</user_files_path>
    <users_config>${BASE_CK_PATH}/config/users_node${ck_index}.xml</users_config>    
    <users>
        <default>
            <password>${CK_PASSWORD}</password> <!-- 空密码 -->
            <networks>
                <ip>::/0</ip> <!-- 允许所有IP访问 -->
            </networks>
            <profile>default</profile>
            <quota>default</quota>
            <access_management>1</access_management>
        </default>
    </users>    
    <default_profile>default</default_profile>
    <default_database>default</default_database>
    <http>
        <port>${HTTP_PORT}</port>
        <max_connections>1024</max_connections>
        <async_insert>1</async_insert>
    </http>
    <listen_host>0.0.0.0</listen_host>
    <listen_host>::</listen_host>
    <http_port>${HTTP_PORT}</http_port>
    <tcp_port>${TCP_PORT}</tcp_port>
    <interserver_http_port>${INTERSERVER_HTTP_PORT}</interserver_http_port>
    <distributed_ddl>
        <!-- Path in ZooKeeper to queue with DDL queries -->
        <path>/clickhouse/task_queue/ddl</path>
    </distributed_ddl>

    <macros>
        <shard>${MACROS_SHARD}</shard>
        <replica>${MACROS_REPLICA}</replica>
    </macros>
</yandex>
```

# 7、users_template.xml

```bash
<?xml version="1.0"?>
<yandex>
    <!-- Profiles of settings. -->
    <profiles>
        <!-- Default settings. -->
        <default>
            <!-- Maximum memory usage for processing single query, in bytes. -->
            <max_memory_usage>10000000000</max_memory_usage>

            <load_balancing>random</load_balancing>
        </default>

        <!-- Profile that allows only read queries. -->
        <readonly>
            <readonly>1</readonly>
        </readonly>
    </profiles>

    <users>
        <default>
            <password>${CK_PASSWORD}</password> 
            <networks>
                <ip>::/0</ip> <!-- 允许所有IP访问 -->
            </networks>
            <profile>default</profile>
            <quota>default</quota>
            <access_management>1</access_management>
        </default>
    </users>    
    
    <!-- Quotas. -->
    <quotas>
        <!-- Name of quota. -->
        <default>
            <!-- Limits for time interval. You could specify many intervals with different limits. -->
            <interval>
                <!-- Length of interval. -->
                <duration>3600</duration>
                <distributed_product_mode>allow</distributed_product_mode>
                <!-- No limits. Just calculate resource usage for time interval. -->
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
</yandex>

```
