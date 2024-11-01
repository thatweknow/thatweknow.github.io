#!/bin/bash

if [ "$(ls -A /Users/admin/my-project/biturd-gp/data/blog)" ]; then
    if ! myhexo d; then
        # 如果执行出错，发送自定义通知（例如：调用 API，发送到聊天工具等）
        echo "myhexo -d 执行失败" | mail -s "Crontab 错误通知" your_email@example.com
    fi
fi