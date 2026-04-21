# War Thunder 载具音乐助手

这是一个面向 War Thunder 的外部音乐播放助手，通过游戏 API 检测当前载具并自动播放对应音乐，完全不修改游戏文件，降低封号风险。

> **重要提醒**：War Thunder 有反作弊机制，本工具仅提供外部辅助功能，不保证完全无风险。使用前请仔细阅读游戏官方用户协议。本插件由b站我的卷卷去哪了制作

## 功能特性

- ✅ **外部检测**：通过 War Thunder 官方 localhost API 检测载具，无需修改游戏
- ✅ **智能播放**：优先播放特定载具音乐，无则播放国籍默认音乐
- ✅ **多格式支持**：支持多个 MP3 文件，随机播放
- ✅ **自动切换**：载具变化时自动停止/开始音乐
- ✅ **低风险**：完全外部工具，不注入游戏进程

## 快速开始

### 1. 安装依赖

```bash
# 自动安装（推荐）
python install_deps.py

# 或手动安装
pip install -r requirements.txt
```

### 2. 添加音乐文件

创建 `music/` 文件夹，按以下结构添加 MP3 文件：

```
music/
├── usa/
│   ├── usa_anthem.mp3
│   └── usa_march.mp3
├── germany/
│   ├── germany_march.mp3
│   └── germany_anthem.mp3
├── cn/
│   └── cn_default.mp3
└── ...                     # 其他国家文件夹
```

**支持的国家**：所有 War Thunder 中存在的国家，直接使用国籍代码作为文件夹名（如 usa, germany, cn, japan, ussr 等）

### 3. 运行程序

```bash
python main.py
```

启动 War Thunder 游戏，程序会自动检测载具并使用系统默认播放器播放对应国籍的音乐。

## 工作原理

1. **载具检测**：查询 `http://localhost:8111/indicators` API 获取当前载具名称
2. **国籍代码提取**：从载具名称中提取国籍代码（如 `cn_ztz_99a` → `cn`）
3. **音乐查找**：在 `music/{国籍代码}/` 文件夹中查找 MP3 文件
4. **播放控制**：使用系统默认播放器播放随机选择的 MP3 文件

## 文件结构

```
项目根目录/
├── main.py                 # 主程序
├── install_deps.py         # 依赖安装脚本
├── requirements.txt        # Python 依赖清单（requests, pygame-ce）
├── vehicle_mapping.json    # 配置信息
├── README.md              # 本说明文件
└── music/                 # 音乐文件夹（需要手动创建）
    └── {国籍代码}/        # 国籍文件夹（如 usa, germany, cn 等）
        ├── music1.mp3
        └── music2.mp3
```

## 配置说明

### 外部播放器

## 技术栈

- **Python 3.11+**
- **requests**：War Thunder API 调用
- **pygame-ce**：内置音频播放
- **pathlib**：文件操作

## 注意事项

- 确保 War Thunder 正在运行且 localhost:8111 API 可用
- MP3 文件需放在对应的国籍代码文件夹中（如 `music/cn/`）
- 程序检测到新载具时会自动切换音乐
- 建议使用高质量 MP3 文件以获得更好体验

## 故障排除

- **无法播放音乐**：确认 MP3 文件是否存在于对应国籍文件夹中
- **API 连接失败**：确认 War Thunder 已启动，localhost:8111 API 可用
- **音乐不断切换**：可能是载具检测不稳定，检查游戏状态是否正常

## 许可证

本项目仅供学习和个人使用，请遵守 War Thunder 用户协议。
   ```bash
   python install_deps.py
   ```

2. **手动安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**：
   ```bash
   python main.py
   ```

> 注意：确保 War Thunder 正在运行且 localhost:8111 端口可用。
