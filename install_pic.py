import base64
import json
import os
import re
import time
import uuid
from urllib.parse import unquote, quote

import requests

# 原始 markdown 目录路径
markdown_dir = 'data/blog'
# 图片上传后的 GitHub 地址前缀

# 定义支持的图片格式
image_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
# 临时存储路径
tmp_dir = 'data/img'

# github 仓库信息
# 配置
github_token = os.getenv("code_api_github_token")  # 环境变量加入GitHub Token
repo_owner = "Bit-urd"  # 仓库拥有者
repo_name = "image-cloud"  # 仓库名称
target_path = "image-gp"  # 上传至仓库中的路径
branch = "master"  # 目标分支
github_base_url = f'https://raw.githubusercontent.com/Bit-urd/image-cloud/refs/heads/master/{target_path}/'


# 时间戳生成器
def generate_timestamp():
    return time.strftime('%Y%m%d%H%M%S')


# 下载非本地图片到临时目录
def download_image_to_tmp(url, tmp_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(tmp_path, 'wb') as f:
                f.write(response.content)
            print(f"已下载 {url} 到 {tmp_path}")
            return True
    except Exception as e:
        print(f"下载 {url} 时出错: {e}")
    return False


def uploadimg_to_github(new_filename, tmp_path):
    local_file_path = tmp_path  # 本地文件路径

    # 读取本地文件内容并进行 Base64 编码
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # 设置请求 URL 和请求头
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{target_path}/{new_filename}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 定义请求数据
    data = {
        "message": "Upload path.img to image-data",
        "content": content,
        "branch": branch
    }

    # 发送 PUT 请求上传文件
    response = requests.put(url, headers=headers, data=json.dumps(data))

    # 检查响应状态
    if response.status_code == 201:
        print("文件上传成功:", response.json().get("content").get("html_url"))
    else:
        print("文件上传失败:", response.json())

    # 处理 markdown 文件的图片链接


def process_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 匹配 Markdown 文件中的图片链接格式
    image_links = re.findall(r'!\[.*?\]\((.*?)\)', content)

    for link in image_links:
        is_encoded = False
        if link != unquote(link):
            link = unquote(link)
            is_encoded = True
        if link.startswith(github_base_url):
            print(f"跳过已上传的图片: {link}")
            continue
        # 检查是否为本地图片文件
        if any(link.endswith(ext) for ext in image_extensions):
            image_path = os.path.join(os.path.dirname(file_path), link)

            # 检查图片是否为本地文件
            tmp_image_path = ''
            if not os.path.exists(image_path):
                # 若不是本地文件，则下载至临时目录
                new_filename = generate_timestamp() + os.path.splitext(link)[1]
                tmp_image_path = os.path.join(tmp_dir, new_filename)

                # 下载图片
                if download_image_to_tmp(link, tmp_image_path):
                    image_path = tmp_image_path
                else:
                    print(f"跳过无法下载的链接: {link}")
                    continue
                    # 生成新的 GitHub 文件名和链接
            new_filename = f'{generate_timestamp()}_{uuid.uuid4()}{os.path.splitext(link)[1]}'
            github_image_url = github_base_url + new_filename

            # 模拟上传至 GitHub 本地目录

            uploadimg_to_github(new_filename, image_path)

            # 替换 Markdown 中的链接
            if is_encoded:
                content = content.replace(quote(link), github_image_url)
            else:
                content = content.replace(link, github_image_url)
            print(f"替换 {link} 为 {github_image_url}")

            # 若为临时文件，删除下载的临时图片
            if image_path == tmp_image_path:
                os.remove(tmp_image_path)
                print(f"删除临时文件 {tmp_image_path}")

    # 保存修改后的内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# uploadimg_to_github("test.png","data/img/20241101142848.png")

# 遍历目录，处理所有 Markdown 文件
for root, dirs, files in os.walk(markdown_dir):
    for filename in files:
        if filename.endswith('.md'):
            process_markdown(os.path.join(root, filename))

print("所有 Markdown 文件处理完成！")
