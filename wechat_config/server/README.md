# 微信公众号服务器部署指南

## 📋 概述

这个目录包含了微信公众号 `https://agentpsy.com/wechat` 的服务器端代码。

## 🚀 部署步骤

### 1. 服务器要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **Python**: 3.8+
- **HTTPS证书**: 必须支持 HTTPS 协议
- **公网IP**: 服务器需要有公网IP地址

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 配置Token

编辑 `wechat_server.py` 文件，修改以下配置：

```python
# 将 "your_custom_token" 替换为你在微信公众平台设置的Token
WECHAT_TOKEN = "your_actual_token_here"  # 必须与微信公众平台一致
```

### 4. 启动服务

#### 方式1: 直接运行（测试用）
```bash
python wechat_server.py
```

#### 方式2: 使用 Gunicorn（生产推荐）
```bash
gunicorn -w 4 -b 0.0.0.0:8080 wechat_server:app
```

#### 方式3: 使用 Systemd（长期运行）
创建服务文件 `/etc/systemd/system/wechat.service`:

```ini
[Unit]
Description=WeChat Server
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/your/server
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:8080 wechat_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable wechat
sudo systemctl start wechat
```

### 5. 配置Nginx（推荐）

创建 Nginx 配置 `/etc/nginx/sites-available/wechat`:

```nginx
server {
    listen 80;
    server_name agentpsy.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name agentpsy.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location /wechat {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/wechat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 微信公众平台配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入 **设置与开发** → **基本配置**
3. 配置服务器信息：
   - **URL**: `https://agentpsy.com/wechat`
   - **Token**: 与代码中设置的Token一致
   - **EncodingAESKey**: 随机生成（可选）
   - **消息加解密方式**: 明文模式（推荐）

4. 点击 **提交** 进行验证

## 🔧 配置说明

### Token设置
- 必须与微信公众平台设置的Token完全一致
- 建议使用16-32位的随机字符串
- 可以包含字母、数字、下划线

### 安全配置
```python
# 在 wechat_server.py 中可以添加IP白名单
ALLOWED_IPS = [
    "127.0.0.1",  # 本地
    "微信服务器IP1",  # 查询微信官方文档获取
    "微信服务器IP2"
]
```

## 📊 监控和日志

### 查看运行状态
```bash
# 如果使用Systemd
sudo systemctl status wechat

# 查看日志
sudo journalctl -u wechat -f
```

### 健康检查
```bash
curl https://agentpsy.com/health
```

## 🛠️ 故障排除

### 常见问题

1. **验证失败**
   - 检查Token是否与微信公众平台一致
   - 确认服务器公网可访问
   - 检查HTTPS证书是否有效

2. **超时错误**
   - 检查服务器响应时间
   - 确认防火墙设置
   - 检查Nginx配置

3. **消息接收失败**
   - 查看服务器日志
   - 确认消息格式正确
   - 检查编码设置

### 调试模式
```python
# 在 wechat_server.py 中启用调试
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 更新和维护

### 更新代码
```bash
# 备份当前版本
cp wechat_server.py wechat_server.py.backup

# 部署新版本
git pull  # 或上传新文件
sudo systemctl restart wechat
```

### 定期维护
- 监控服务器磁盘空间
- 定期查看日志文件
- 更新Python依赖包
- 检查HTTPS证书有效期

## 📞 支持和联系

如果遇到问题：
1. 检查本故障排除指南
2. 查看微信公众平台开发者文档
3. 联系技术支持

## 📝 功能特性

✅ **服务器验证**: 支持微信服务器验证
✅ **消息接收**: 处理文本和事件消息
✅ **自动回复**: 关键词自动回复功能
✅ **健康检查**: 服务状态监控
✅ **日志记录**: 详细的操作日志
✅ **HTTPS支持**: 安全的HTTPS连接
✅ **多进程**: 支持并发处理

## 🚀 部署完成后的测试

1. **健康检查测试**:
   ```bash
   curl https://agentpsy.com/health
   ```

2. **微信验证测试**:
   - 在微信公众平台点击"提交"按钮
   - 查看服务器日志确认验证成功

3. **消息测试**:
   - 关注微信公众号
   - 发送测试消息
   - 确认收到自动回复

部署完成后，你的微信公众号就能正常接收和回复消息了！