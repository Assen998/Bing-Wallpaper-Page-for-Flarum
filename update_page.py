import yaml
import os
import sys
from src.get_github_file import get_github_file
from src.flarum_pages import FlarumPages
from datetime import datetime

def load_config(config_file: str) -> dict:
    """加载YAML配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件 {config_file} 失败: {str(e)}")
        sys.exit(1)

def update_github_to_page(github_config: dict, flarum_config: dict) -> bool:
    """
    更新总览页面（使用指定的main_page_id）并替换链接
    
    :param github_config: GitHub相关配置
    :param flarum_config: Flarum相关配置
    :return: 是否更新成功
    """
    if 'main_page_id' not in flarum_config:
        print("❌ 配置中缺少 main_page_id")
        return False

    # 初始化Flarum客户端
    client = FlarumPages(
        base_url=flarum_config['base_url'],
        api_token=flarum_config['api_token']
    )
    
    # 获取指定ID的页面
    page = client.get_page(flarum_config['main_page_id'])
    if not page:
        print(f"❌ 未找到ID为 {flarum_config['main_page_id']} 的页面")
        return False

    # 从GitHub获取内容
    content = get_github_file(
        owner=github_config['owner'],
        repo=github_config['repo'],
        path=github_config['path'],
        branch=github_config.get('branch', 'main')
    )
    
    if not content:
        print("❌ 从GitHub获取内容失败")
        return False

    # 处理内容：替换链接
    try:
        # 查找历史归档部分
        archive_start = content.find("### 历史归档：")
        if archive_start != -1:
            # 分割内容
            before_archive = content[:archive_start].strip()
            archive_content = content[archive_start:]
            
            # 替换所有GitHub链接为Flarum链接
            import re
            pattern = r'\[(\d{4}-\d{2})\]\(/zh-cn/picture/\d{4}-\d{2}/\)'
            
            def replace_link(match):
                year_month = match.group(1)
                return f'[{year_month}]({flarum_config["base_url"]}/p/bing-wallpaper-{year_month.lower()})'
            
            new_archive_content = re.sub(pattern, replace_link, archive_content)
            
            # 组合新内容
            content = f"{before_archive}\n\n{new_archive_content}"
            print("✅ 已替换历史归档链接")
    except Exception as e:
        print(f"❌ 处理内容时出错: {str(e)}")
        return False

    # 更新页面
    try:
        updated_page = client.update_page(
            page.id,
            content=content
        )
        
        if updated_page:
            print(f"✅ 总览页面更新成功 (ID: {updated_page.id})")
            return True
        else:
            print("❌ 总览页面更新失败")
            return False
            
    except Exception as e:
        print(f"❌ 更新页面时出错: {str(e)}")
        return False

def update_current_month_page(github_config: dict, flarum_config: dict) -> bool:
    """
    更新或创建当前月份的归档页面，并在创建新页面时更新配置文件
    """
    if 'archive_page_id' not in flarum_config or 'current_year_month' not in flarum_config:
        print("❌ 配置中缺少必要字段")
        return False

    # 获取当前年月
    current_date = datetime.now()
    current_year_month = current_date.strftime("%Y-%m")
    
    print(f"📅 当前年月: {current_year_month}")
    print(f"📅 配置文件记录的年月: {flarum_config['current_year_month']}")
    
    # 初始化Flarum客户端
    client = FlarumPages(
        base_url=flarum_config['base_url'],
        api_token=flarum_config['api_token']
    )
    
    # 检查是否需要创建新页面
    if current_year_month != flarum_config['current_year_month']:
        print("📝 检测到新的月份，准备创建新页面...")
        target_title = f"Bing Wallpaper ({current_year_month})"
        target_slug = f"bing-wallpaper-{current_year_month}"
        
        # 构建新月份的GitHub文件路径
        github_path = f"{github_config['base_path']}/{current_year_month}/README.md"
        content = get_github_file(
            owner=github_config['owner'],
            repo=github_config['repo'],
            path=github_path,
            branch=github_config.get('branch', 'main')
        )
        
        if not content:
            print("❌ 从GitHub获取内容失败")
            return False
            
        # 创建新页面
        new_page = client.create_page(
            title=target_title,
            content=content,
            slug=target_slug,
            is_hidden=False,
            is_html=False
        )
        
        if new_page:
            print(f"✅ 新页面创建成功: {new_page.title} (ID: {new_page.id})")
            # 更新配置文件
            config_file = os.path.join(os.path.dirname(__file__), 'config', 'flarum_config.yaml')
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            config['archive_page_id'] = new_page.id
            config['current_year_month'] = current_year_month
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, allow_unicode=True)
                
            print(f"✅ 配置文件已更新:")
            print(f"   - archive_page_id: {new_page.id}")
            print(f"   - current_year_month: {current_year_month}")
            return True
        else:
            print("❌ 新页面创建失败")
            return False
    else:
        # 更新现有页面
        print(f"📝 更新现有归档页面 (ID: {flarum_config['archive_page_id']})")
        page = client.get_page(flarum_config['archive_page_id'])
        if not page:
            print("❌ 无法获取现有页面")
            return False
            
        # 获取当前月份的GitHub内容
        github_path = f"{github_config['base_path']}/{current_year_month}/README.md"
        content = get_github_file(
            owner=github_config['owner'],
            repo=github_config['repo'],
            path=github_path,
            branch=github_config.get('branch', 'main')
        )
        
        if not content:
            print("❌ 从GitHub获取内容失败")
            return False
            
        # 更新页面
        updated_page = client.update_page(
            page.id,
            content=content,
            title=f"Bing Wallpaper ({current_year_month})"
        )
        
        if updated_page:
            print(f"✅ 页面更新成功: {updated_page.title} (ID: {updated_page.id})")
            return True
        else:
            print("❌ 页面更新失败")
            return False

def main():
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    github_config_file = os.path.join(config_dir, 'github_config.yaml')
    flarum_config_file = os.path.join(config_dir, 'flarum_config.yaml')

    try:
        github_config = load_config(github_config_file)
        flarum_config = load_config(flarum_config_file)
        
        # 先更新总览页面
        print("\n🔄 更新总览页面...")
        success1 = update_github_to_page(github_config, flarum_config)
        
        # 再更新当前月份页面
        print("\n🔄 更新当前月份页面...")
        success2 = update_current_month_page(github_config, flarum_config)
        
        # 两个操作都成功才返回成功
        sys.exit(0 if (success1 and success2) else 1)
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()