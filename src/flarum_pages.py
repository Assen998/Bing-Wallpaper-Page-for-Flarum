import requests
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Page:
    """页面数据类"""
    id: int
    title: str
    slug: str
    content: str
    is_hidden: bool
    is_html: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class FlarumPages:
    """Flarum Pages插件API客户端"""
    def __init__(self, base_url: str, api_token: str):
        """
        初始化Pages API客户端
        
        :param base_url: Flarum论坛的基础URL
        :param api_token: API访问令牌
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }

    def create_page(self, title: str, content: str, slug: str = None,
                   is_hidden: bool = False, is_html: bool = False) -> Optional[Page]:
        """
        创建新页面
        
        :param title: 页面标题
        :param content: 页面内容
        :param slug: URL别名(可选)
        :param is_hidden: 是否隐藏
        :param is_html: 是否作为HTML渲染
        :return: 创建的页面对象
        """
        url = f"{self.base_url}/api/pages"
        data = {
            "data": {
                "type": "pages",
                "attributes": {
                    "title": title,
                    "content": content,
                    "isHidden": is_hidden,  # 修改键名以匹配API要求
                    "isHtml": is_html,      # 修改键名以匹配API要求
                }
            }
        }
        
        # 如果提供了slug，则添加到属性中
        if slug:
            data["data"]["attributes"]["slug"] = slug

        try:
            print(f"正在创建页面: {title}")
            print(f"请求URL: {url}")
            print(f"发送数据: {data}")
            
            response = requests.post(url, headers=self.headers, json=data)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 201:
                page = self._parse_page(response.json()["data"])
                if page:
                    print(f"✅ 页面创建成功: {page.title} (ID: {page.id})")
                    return page
                else:
                    print("❌ 页面创建成功但解析响应失败")
                    return None
            else:
                print(f"❌ 创建页面失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ 发送请求时出错: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ 创建页面时发生未知错误: {str(e)}")
            return None

    def get_page(self, id: int) -> Optional[Page]:
        """获取指定ID的页面"""
        url = f"{self.base_url}/api/pages/{id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return self._parse_page(response.json()["data"])
        return None

    def get_page_by_slug(self, slug: str) -> Optional[Page]:
        """通过slug获取页面"""
        url = f"{self.base_url}/api/pages"
        params = {"filter[slug]": slug}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            if data:
                return self._parse_page(data[0])
        return None

    def update_page(self, id: int, **kwargs) -> Optional[Page]:
        """
        更新页面
        
        :param id: 页面ID
        :param kwargs: 要更新的字段，可包含：title, content, is_hidden, is_html, slug
        :return: 更新后的页面对象
        """
        url = f"{self.base_url}/api/pages/{id}"
        data = {
            "data": {
                "type": "pages",
                "id": str(id),
                "attributes": kwargs
            }
        }
        response = requests.patch(url, headers=self.headers, json=data)
        if response.status_code == 200:
            return self._parse_page(response.json()["data"])
        return None

    def delete_page(self, id: int) -> bool:
        """删除页面"""
        url = f"{self.base_url}/api/pages/{id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204

    def list_pages(self, include_hidden: bool = False) -> List[Page]:
        """获取页面列表"""
        url = f"{self.base_url}/api/pages"
        params = {}
        if not include_hidden:
            params["filter[isHidden]"] = "0"
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"API响应数据: {json_data}")  # 调试信息
                return [self._parse_page(item) for item in json_data.get("data", [])]
            except Exception as e:
                print(f"处理API响应时出错: {e}")
                print(f"响应内容: {response.text}")
                return []
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return []

    def _parse_page(self, data: Dict) -> Page:
        """解析API返回的页面数据"""
        attrs = data["attributes"]
        try:
            return Page(
                id=int(data["id"]),
                title=attrs.get("title", ""),
                slug=attrs.get("slug", ""),
                content=attrs.get("content", ""),
                is_hidden=attrs.get("isHidden", False),
                is_html=attrs.get("isHtml", False),
                created_at=datetime.fromisoformat(attrs.get("time", "").replace("Z", "+00:00")) if attrs.get("time") else datetime.now(),
                updated_at=datetime.fromisoformat(attrs.get("editTime", "").replace("Z", "+00:00")) if attrs.get("editTime") else None
            )
        except Exception as e:
            print(f"解析页面数据时出错: {e}")
            print(f"原始数据: {data}")
            return None

