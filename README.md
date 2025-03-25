# Bing Wallpaper Page for Flarum

一个用于管理必应每日壁纸页面的Python工具，支持从GitHub仓库同步内容到Flarum论坛页面。

## 功能特点

- 自动同步GitHub仓库内容到Flarum页面
- 支持创建和更新月度归档页面
- 自动处理历史归档链接
- 支持批量创建历史归档页面

## 目录结构

```
page-bingpaper/
├── config/                # 配置文件目录
│   ├── flarum_config.yaml   # Flarum配置
│   └── github_config.yaml   # GitHub配置
├── src/                   # 源代码目录
│   ├── flarum_pages.py     # Flarum API封装
│   └── get_github_file.py  # GitHub API封装
├── create_archive_pages.py  # 创建归档页面
├── update_page.py          # 更新页面内容
└── README.md              # 项目说明文档
```

## 安装

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/page-bingpaper.git
cd page-bingpaper
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 创建并编辑 `config/flarum_config.yaml`：
```yaml
base_url: "https://your-forum.com"
api_token: "your-api-token"    
current_year_month: 2025-03   //这是记录最近更新页面的年月，一般修改为当前的年月
archive_page_id: 32   //这是最新日期归档页面的id，批量创建归档页面后，找到这个id
main_page_id: 1       //这是壁纸总览主页的id，需手动随便创建一个页面，找到这个id
```

2. 创建并编辑 `config/github_config.yaml`：
```yaml
# GitHub配置 默认为原始仓库
owner: niumoo  # GitHub用户名
repo: bing-wallpaper  # 仓库名称
path: /zh-cn/README.md  # 文件路径
branch: main  # 分支名称
base_path: "zh-cn/picture"  # 图片路径
```

## 使用方法
flarum必须安装插件 Pages by FriendsOfFlarum
Installation

Use Bazaar or install manually with composer:
```
composer require fof/pages
```
### 第一次批量创建归档页面
需克隆niumoo/bing-wallpaper仓库到本地
```bash
git clone https://github.com/niumoo/bing-wallpaper.git
```
然后复制bing-wallpaper/zh-cn/picture目录，到本项目page-bingpaper目录下
```bash

python create_archive_pages.py
```

### 更新页面内容
建议定时运行
```bash
python update_page.py
```


## 注意事项

1. 确保已正确配置 Flarum API 令牌
2. 图片目录结构需符合规范（YYYY-MM格式）
3. 每个月份目录下必须包含 README.md 文件
4. 建议先在测试环境验证功能

## 开发说明

- Python 版本要求：3.6+
- 主要依赖：
  - requests
  - pyyaml
  - datetime

## 许可证

MIT License

## 作者

[Assen998]

## 更新日志

### v1.0.0 (2025-03-25)
- 初始版本发布
- 实现基本功能