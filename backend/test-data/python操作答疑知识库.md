# Python 学习操作答疑知识库

## Python 安装教程（Windows 系统）

### 步骤

1. 打开浏览器访问 https://www.python.org/downloads/
2. 点击黄色大按钮下载最新 3.x 版本（截至 2024 年推荐 3.12）
3. 运行下载的 `.exe` 安装包
4. **关键步骤**：在安装界面底部，务必勾选 **"Add Python to PATH"**（Add python.exe to PATH），否则命令行找不到 python
5. 点击 "Install Now"（快速安装）或 "Customize installation"（自定义，推荐）
6. 自定义安装：确认勾选 pip、py launcher、for all users
7. 安装完成后，打开命令提示符（Win+R → 输入 cmd → 回车）
8. 输入 `python --version`，看到版本号则安装成功

![](faq-images/python-install.png)

### 常见坑

- **忘记勾选 Add to PATH**：命令行输入 python 报"不是内部或外部命令"。解决：重新运行安装包 → Modify → 勾选 Add to PATH；或手动将 Python 安装目录添加到系统环境变量 Path
- **装了多个 Python 版本**：用 `py -3.12` 指定版本，用 `py -3.12 -m pip install 包名` 安装
- **安装路径有中文或空格**：部分工具报错，建议装到 `C:\Python312\`

## Python 安装教程（macOS 系统）

### 步骤

1. 推荐用 Homebrew 安装（最省心）：打开终端（Terminal），运行

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. 安装 Homebrew 后执行：

```
brew install python
```

3. 安装完成后验证：

```
python3 --version
pip3 --version
```

macOS 自带 python2，一定用 `python3` 和 `pip3`，不要用 `python`。

### 常见坑

- **brew 下载慢**：把 Homebrew 源换为清华源或中科大源
- **权限问题**：不要用 sudo pip3，用 `pip3 install --user 包名`
- **M1/M2 芯片**：brew 默认装 arm 版，绝大多数包都支持，遇到问题加 `arch -x86_64` 前缀

## pip 安装慢或超时——国内镜像源配置

### 场景

执行 `pip install` 时下载极慢，或出现 `timeout` 报错。

### 解决方法：换用国内镜像源

**临时使用（单次）：**

```
pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**永久配置（推荐）：**

```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

执行后再运行 `pip install` 会自动走清华源。

![](faq-images/pip-mirror.png)

### 常用国内镜像地址

| 镜像名 | 地址 |
|--------|------|
| 清华大学 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ |
| 华为云 | https://repo.huaweicloud.com/repository/pypi/simple/ |

### 验证是否生效

```
pip config list
```

看到 `global.index-url = https://pypi.tuna.tsinghua.edu.cn/simple` 即生效。

## pip 报错处理

### 报错 1："pip 不是内部或外部命令"

**原因**：Python 安装时未勾选 Add to PATH，或 Scripts 目录未加入环境变量。

**解决方法：**

1. 用 python 模块方式调用：`python -m pip install 包名`
2. 根本解决：把 Python 的 Scripts 目录加入 PATH

```
# 找到 Scripts 目录（一般在）
C:\Users\你的用户名\AppData\Local\Programs\Python\Python312\Scripts
# 将其添加到系统环境变量 Path
```

![](faq-images/pip-error.png)

### 报错 2：SSL 证书错误

报错信息包含 `SSLError` 或 `certificate verify failed`。

**解决方法：**

```
pip install 包名 --trusted-host pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或全局配置信任：

```
pip config set global.trusted-host "pypi.org files.pythonhosted.org"
```

### 报错 3：权限错误（Permission denied）

**解决方法：**

```
# 方法1：安装到用户目录（推荐，不需要管理员权限）
pip install 包名 --user

# 方法2：用虚拟环境（最推荐）
python -m venv myenv
myenv\Scripts\activate
pip install 包名
```

### 报错 4：找不到包（Could not find a version）

检查：
1. 包名拼写是否正确（严格区分大小写）
2. Python 版本是否兼容（到 PyPI 官网查看）
3. 尝试指定版本：`pip install 包名==版本号`

## PyCharm 创建新项目完整流程

### 步骤

1. 打开 PyCharm，点击 **File → New Project**（或欢迎界面的 New Project）
2. 在 **Location** 填写项目保存路径（建议全英文路径，无空格）
3. 展开 **Python Interpreter** 区域：
   - 选择 **New environment using Virtualenv**（推荐，自动创建隔离环境）
   - 或选择 **Existing interpreter** → 选择已安装的 Python.exe
4. 点击 **Create**，等待 PyCharm 创建项目和虚拟环境
5. 创建完成后在右下角可以看到解释器版本（如 Python 3.12）

![](faq-images/pycharm-new-project.png)

### 验证解释器是否正确

- 点击右下角 Python 版本按钮（或 File → Settings → Project → Python Interpreter）
- 看到正确的 Python 版本 + pip 包列表即成功
- 在 Terminal 标签页输入 `python --version` 再次确认

### 常见坑

- **Location 路径含中文**：部分插件报错，务必全英文
- **Base interpreter 选错**：选了 Python 2 或其他版本 → 在设置里重新选
- **创建时 PyCharm 卡住**：等待网络下载依赖，耐心等待；也可以先断网创建

## PyCharm 选错解释器导致 ModuleNotFoundError

### 场景

明明用 pip 安装了某个包，运行时却报 `ModuleNotFoundError: No module named 'xxx'`。

**最常见原因：pip 安装到了另一个 Python，而 PyCharm 用的是不同的解释器。**

### 解决步骤

1. **查看 PyCharm 当前使用的解释器**：
   - 右下角点击 Python 版本 → "Interpreter Settings"
   - 或 File → Settings → Project: 项目名 → Python Interpreter

2. **查看解释器路径**，记下它

3. **确认 pip 安装位置**：在 PyCharm Terminal 中运行

```
pip show 包名
# 查看 Location 字段，确认包安装在哪个 Python 下
```

4. **换为正确解释器**：Settings → Python Interpreter → 右上角齿轮 → Add

5. **在 PyCharm 内用 pip 安装**：Terminal → `pip install 包名`（此时 pip 自动指向当前 venv）

### 快速验证

在 PyCharm Terminal 中运行：

```python
import sys
print(sys.executable)   # 查看 Python 路径
print(sys.path)         # 查看包搜索路径
```

## venv 和 uv 虚拟环境基础

### 什么是虚拟环境

虚拟环境是独立的 Python 包安装目录，不同项目互不干扰，避免版本冲突。

### venv 基础操作

```
# 创建虚拟环境
python -m venv myenv

# 激活（Windows cmd）
myenv\Scripts\activate

# 激活（macOS / Linux）
source myenv/bin/activate

# 激活后安装包（只影响当前虚拟环境）
pip install requests numpy

# 退出虚拟环境
deactivate
```

激活后命令行开头会出现 `(myenv)` 标识。

### uv 基础操作（更快的现代工具）

uv 是用 Rust 写的包管理工具，速度比 pip 快 10-100 倍。

```
# 安装 uv
pip install uv

# 创建项目并初始化
uv init myproject
cd myproject

# 添加依赖
uv add requests

# 运行代码
uv run python main.py
```

### 常见坑

- **Windows PowerShell 激活报错**："无法加载文件…"：执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **激活后 pip install 还是全局**：检查命令行开头是否有 `(myenv)`；没有则重新激活

## 确认 Python 版本与包是否安装成功

### 确认 Python 安装

```
python --version          # Windows（加了 PATH）
python3 --version         # macOS / Linux
py --version              # Windows py launcher
```

看到 `Python 3.x.x` 即成功。

### 确认 pip 安装

```
pip --version
# 输出示例：pip 24.0 from C:\Python312\Lib\site-packages\pip (python 3.12)
```

### 查看已安装的包

```
pip list                  # 列出所有包
pip show 包名             # 查看某个包的版本和路径
pip freeze                # 导出依赖清单（可存为 requirements.txt）
```

### 在代码中验证

```python
import importlib
print(importlib.import_module("requests").__version__)

# 或者
try:
    import numpy
    print("numpy 可用，版本：", numpy.__version__)
except ImportError:
    print("numpy 未安装")
```

### 常见坑

- **python 和 python3 版本不同**：macOS 下 python 可能是 2.7，python3 才是 3.x
- **pip install 成功但 import 失败**：多个 Python 版本混用，用 `python -m pip install 包名` 确保装到当前 Python
- **包版本冲突**：用 `pip check` 检查依赖冲突
