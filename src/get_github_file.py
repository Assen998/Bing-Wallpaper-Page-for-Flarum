import requests
import base64
from typing import List, Dict, Optional

def get_github_file(owner, repo, path, branch="main"):
    """
    从GitHub仓库获取指定文件的内容

    :param owner: GitHub仓库的所有者用户名
    :param repo: 仓库名称
    :param path: 文件在仓库中的路径
    :param branch: 分支名称，默认为 "main"
    :return: 文件内容，如果请求失败则返回 None
    """
    # 构建GitHub API的URL
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"

    # 发送GET请求
    response = requests.get(url)

    # 检查响应状态码
    if response.status_code == 200:
        # 获取文件内容（Base64编码）
        data = response.json()
        content_base64 = data["content"]

        # 解码Base64内容
        content = base64.b64decode(content_base64).decode("utf-8")
        print(f"成功获取文件内容: {content}")
        return content
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"请求的 URL: {url}")
        print(f"响应内容: {response.text}")
        return None

def get_github_directory(owner: str, repo: str, path: str = "", branch: str = "main") -> Optional[List[Dict]]:
    """
    获取GitHub仓库中指定目录下的文件列表

    :param owner: GitHub仓库的所有者用户名
    :param repo: 仓库名称
    :param path: 目录路径，默认为根目录
    :param branch: 分支名称，默认为 "main"
    :return: 文件列表，每个文件包含type、name、path等信息，如果请求失败则返回 None
    """
    # 构建GitHub API的URL
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"

    try:
        # 发送GET请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析响应数据
            contents = response.json()
            
            # 如果返回的不是列表，说明这不是一个目录
            if not isinstance(contents, list):
                print(f"指定路径 '{path}' 不是一个目录")
                return None
                
            # 提取需要的信息
            files = []
            for item in contents:
                files.append({
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],  # 'file' 或 'dir'
                    'size': item.get('size', 0),
                    'download_url': item.get('download_url', '')
                })
            
            return files
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"请求的 URL: {url}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"获取目录内容时出错: {str(e)}")
        return None

