import os
import re
import yaml
from datetime import datetime
from src.get_github_file import get_github_file
from src.flarum_pages import FlarumPages
#本程序是首次为每个月份的README.md创建对应的页面
# 克隆到本地后，复制出zh-cn/picture文件夹，然后运行本程序即可
def create_archive_pages(base_url: str, api_token: str, picture_dir: str):
    """
    为每个月份的README.md创建对应的页面
    
    :param base_url: Flarum网站URL
    :param api_token: API访问令牌
    :param picture_dir: 图片目录路径
    """
    # 初始化Flarum客户端
    client = FlarumPages(base_url, api_token)
    
    # 记录成功创建的页面数量
    success_count = 0
    
    # 遍历picture目录
    for dirname in sorted(os.listdir(picture_dir)):
        # 检查目录名格式是否为YYYY-MM
        if not re.match(r'^\d{4}-\d{2}$', dirname):
            print(f"⚠️ 跳过不符合格式的目录: {dirname}")
            continue
            
        readme_path = os.path.join(picture_dir, dirname, 'README.md')
        if not os.path.exists(readme_path):
            print(f"⚠️ {dirname} 目录下没有找到README.md")
            continue
            
        try:
            # 读取README.md内容
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建页面标题和slug
            title = f"Bing Wallpaper ({dirname})"
            slug = f"bing-wallpaper-{dirname.lower()}"
            
            # 直接创建新页面
            print(f"✨ 创建新页面: {title} (slug: {slug})")
            result = client.create_page(
                title=title,
                content=content,
                slug=slug,
                is_hidden=False,
                is_html=False
            )
            
            if result:
                print(f"✅ 创建成功: {title}")
                success_count += 1
            else:
                print(f"❌ 创建失败: {title}")
            
        except Exception as e:
            print(f"❌ 处理 {dirname} 时出错: {str(e)}")
            continue
            
    print(f"\n总结: 成功创建 {success_count} 个页面")
    return success_count > 0

def load_config(config_file: str) -> dict:
    """加载YAML配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {str(e)}")
        raise

def main():
    # 加载YAML配置文件
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'flarum_config.yaml')
    try:
        config = load_config(config_file)
        
        create_archive_pages(
            base_url=config['base_url'],
            api_token=config['api_token'],
            picture_dir=config.get('picture_dir', os.path.join(os.path.dirname(__file__), 'picture'))
        )
        return 0
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())