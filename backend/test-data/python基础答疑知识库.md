# Python 基础答疑知识库

本文档面向 Python 初学者，涵盖入门阶段最常见的概念和报错，供答疑系统检索使用。

## Python 是什么

Python 是一种简单易学、适合初学者的高级编程语言，由 Guido van Rossum 于 1991 年发布。

它的语法接近自然语言，代码简洁易读，非常适合作为编程入门的第一门语言。Python 的应用范围非常广泛，包括：自动化脚本、数据分析、Web 后端开发、人工智能与机器学习等方向。

Python 采用解释型执行方式，每行代码由解释器逐行运行，出错时会立即给出提示，便于调试学习。

## Python 适合做什么

Python 可以用来完成非常多类型的任务：

- **自动化脚本**：批量重命名文件、定时发送邮件、自动填表等重复性工作。
- **数据处理与分析**：配合 pandas、numpy 处理 Excel、CSV 等数据文件。
- **网络爬虫**：使用 requests + BeautifulSoup 抓取网页内容。
- **Web 后端服务**：使用 Flask、FastAPI、Django 构建 HTTP 接口。
- **人工智能 / 机器学习**：使用 scikit-learn、PyTorch、TensorFlow 构建模型。
- **接口调用**：调用第三方 REST API，发送 HTTP 请求，处理 JSON 响应。

初学者建议从自动化脚本或数据处理入手，门槛最低、成就感最强。

## 变量和数据类型

变量是存储数据的容器，Python 中不需要声明类型，直接赋值即可。

常用数据类型：

- **字符串 str**：文本内容，用单引号或双引号括起来，例如 `name = "张三"`。
- **整数 int**：不含小数的数字，例如 `age = 18`。
- **浮点数 float**：含小数的数字，例如 `price = 9.9`。
- **布尔值 bool**：只有 True 或 False 两个值，用于条件判断。
- **列表 list**：有序的数据集合，可以包含不同类型，例如 `scores = [90, 85, 78]`。
- **字典 dict**：键值对集合，例如 `user = {"name": "张三", "age": 18}`。

```python
name = "张三"
age = 18
is_student = True
scores = [90, 85, 78]
user = {"name": "张三", "age": 18}
print(type(name))   # <class 'str'>
print(type(age))    # <class 'int'>
```

## if 判断

if 语句用于根据条件决定是否执行某段代码，是控制流程的基础工具。

语法结构：

```python
if 条件:
    # 条件为 True 时执行
elif 另一个条件:
    # 前面条件为 False、这个条件为 True 时执行
else:
    # 以上条件都不满足时执行
```

最小示例：

```python
score = 85
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

注意事项：条件后面必须有冒号，代码块必须缩进（通常 4 个空格）。

## for 循环

for 循环适合重复执行固定次数的任务，或遍历一个序列中的每个元素。

最常用的是配合 `range()` 函数使用：

```python
for i in range(5):
    print(i)
# 输出：0 1 2 3 4
```

也可以遍历列表：

```python
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(fruit)
```

`range(start, stop, step)` 三个参数分别表示起始值、终止值（不含）、步长。

```python
for i in range(1, 10, 2):
    print(i)
# 输出：1 3 5 7 9
```

## 函数

函数是把一段重复逻辑封装起来，给它起个名字，方便反复调用，避免代码重复。

定义函数用 `def` 关键字：

```python
def greet(name):
    return f"你好，{name}！"

print(greet("张三"))   # 你好，张三！
print(greet("李四"))   # 你好，李四！
```

函数可以有默认参数：

```python
def add(a, b=10):
    return a + b

print(add(5))     # 15（b 用默认值 10）
print(add(5, 3))  # 8
```

## 文件读写

Python 使用内置的 `open()` 函数来读写文件。

读取文本文件：

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(content)
```

写入文本文件：

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, Python!")
```

使用 `with` 语句可以确保文件操作完成后自动关闭，推荐始终使用这种写法。

追加内容使用 `"a"` 模式，逐行读取使用 `f.readlines()`。

## JSON 处理

Python 内置 `json` 模块，可以在 Python 对象（字典、列表）和 JSON 字符串之间互相转换。

```python
import json

# dict → JSON 字符串
data = {"name": "张三", "age": 18}
json_str = json.dumps(data, ensure_ascii=False)
print(json_str)  # {"name": "张三", "age": 18}

# JSON 字符串 → dict
text = '{"name": "李四", "score": 95}'
obj = json.loads(text)
print(obj["name"])  # 李四
```

读取 JSON 文件使用 `json.load(f)`，写入 JSON 文件使用 `json.dump(data, f)`。

## requests 请求

`requests` 是 Python 最流行的 HTTP 请求库，需要先安装：`pip install requests`。

发送 GET 请求：

```python
import requests

response = requests.get("https://api.example.com/data")
print(response.status_code)  # 200 表示成功
print(response.json())        # 解析 JSON 响应
```

发送 POST 请求，携带 JSON 数据：

```python
payload = {"username": "test", "password": "123456"}
response = requests.post("https://api.example.com/login", json=payload)
print(response.json())
```

常用属性：`response.status_code`（状态码）、`response.text`（文本内容）、`response.json()`（JSON 响应）。

## FastAPI 是什么

FastAPI 是一个现代化的 Python Web 框架，专门用来快速开发 HTTP 接口（API），性能接近 Node.js 和 Go。

最小示例：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}
```

启动命令：`uvicorn main:app --reload`

FastAPI 的主要特点：自动生成 API 文档（/docs）、基于 Pydantic 的数据校验、支持异步（async/await）、类型注解友好。

## 常见报错：ModuleNotFoundError

**报错示例：**

```
ModuleNotFoundError: No module named 'requests'
```

**原因分析：**

1. 没有安装对应的包（最常见）。
2. 安装了包但解释器选错，安装环境和运行环境不一致。
3. 虚拟环境没有激活。

**解决方法：**

```bash
pip install requests
# 如果使用虚拟环境
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install requests
```

验证安装：`python -c "import requests; print(requests.__version__)"`

## 常见报错：SyntaxError

**报错示例：**

```
SyntaxError: invalid syntax
```

**原因分析：**

语法写错了，常见情况：

- 括号没有闭合：`print("hello"`
- 冒号漏写：`if x > 0` 后面没有 `:`
- 引号不匹配：`name = "张三'`
- 中文符号混入：用了中文冒号 `：` 而不是英文冒号 `:`

**解决方法：**

仔细检查报错行及其上一行，重点看括号、引号、冒号是否完整正确。

## 常见报错：IndentationError

**报错示例：**

```
IndentationError: unexpected indent
IndentationError: expected an indented block
```

**原因分析：**

Python 对缩进非常严格，每一级缩进必须一致（通常使用 4 个空格）。

常见原因：

- 混用了空格和 Tab（肉眼看不出来，但 Python 能检测到）。
- 某行缩进多了或少了一个空格。
- 函数或 if 语句后面的代码块没有缩进。

**解决方法：**

统一使用空格（不要用 Tab），推荐在编辑器中开启"显示空白字符"选项。
