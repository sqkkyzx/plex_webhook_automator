# 使用 Python 官方镜像作为基础镜像
FROM python:3.12.0-alpine

# 设置工作目录
WORKDIR /usr/src/myapp

# 安装依赖
RUN pip install --upgrade pip
RUN pip install -U requests uvicorn[standard] fastapi pypinyin urllib3 --no-cache-dir

COPY myapp /usr/src/myapp

# 启动应用程序
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "warning"]