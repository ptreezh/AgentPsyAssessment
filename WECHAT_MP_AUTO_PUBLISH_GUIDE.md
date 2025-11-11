# 微信公众号自动发布配置指南

## 🔧 当前状态 vs 真实发布

### 当前配置（模拟版本）
- ✅ Markdown 转 HTML 格式转换
- ✅ 文章预览和模拟发布
- ✅ 生成发布链接（模拟）
- ❌ **无法真正发布到微信公众号**

### 真实发布需要的配置
- ❌ 微信公众号开发者权限
- ❌ AppID 和 AppSecret
- ❌ Access Token 管理
- ❌ 素材上传和图文消息接口

## 📋 微信公众号自动发布完整配置流程

### 1. 注册微信公众号开发者账号

#### 1.1 注册类型选择
```
个人号 ❌ 无法获取开发者权限
企业号 ✅ 可以获取完整 API 权限
政府号 ✅ 可以获取完整 API 权限
媒体号 ✅ 可以获取完整 API 权限
```

#### 1.2 注册步骤
1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 选择合适的账号类型注册
3. 完成企业认证（需要营业执照）
4. 支付认证费用（300元/年）

### 2. 获取开发者权限

#### 2.1 开发者设置
1. 登录微信公众平台
2. 进入 **设置与开发** → **基本配置**
3. 获取 **AppID** 和 **AppSecret**

#### 2.2 服务器配置
1. 配置服务器 URL（需要公网可访问的域名）
2. 设置 Token（自定义令牌）
3. 配置 EncodingAESKey（消息加解密密钥）
4. 选择消息加解密方式

### 3. API 权限申请

#### 3.1 必需权限
```
- 素材管理权限 ✅
- 图文消息管理权限 ✅
- 用户管理权限 ✅
```

#### 3.2 申请流程
1. 进入 **设置与开发** → **接口权限**
2. 申请相关 API 权限
3. 提交审核材料
4. 等待微信审核（通常 1-3 个工作日）

## 🔑 获取关键配置信息

### AppID 和 AppSecret
```json
{
  "appid": "wx1234567890abcdef",
  "appsecret": "your_32_character_app_secret_here"
}
```

### Access Token（通过 API 获取）
```python
import requests

def get_access_token(appid, appsecret):
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": appsecret
    }
    response = requests.get(url, params=params)
    return response.json()

# 示例响应
# {
#   "access_token": "ACCESS_TOKEN",
#   "expires_in": 7200
# }
```

## 🛠️ 真实微信公众号发布 MCP 实现

### 配置文件结构
```
wechat_config/
├── config.json          # 基础配置
├── tokens.json          # Access Token 缓存
├── materials/           # 上传的素材
└── logs/               # 发布日志
```

### 配置文件示例
```json
{
  "wechat": {
    "appid": "your_appid_here",
    "appsecret": "your_appsecret_here",
    "server_url": "https://your-domain.com/wechat",
    "token": "your_custom_token",
    "encoding_aes_key": "your_encoding_key"
  },
  "publish": {
    "auto_publish": true,
    "draft_mode": false,
    "cover_image": "path/to/default/cover.jpg"
  }
}
```

### 核心发布 API 调用
```python
import requests
import json
import time

class WeChatPublisher:
    def __init__(self, config):
        self.config = config
        self.access_token = None
        self.token_expires = 0

    def get_access_token(self):
        """获取或刷新 Access Token"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.config["appid"],
            "secret": self.config["appsecret"]
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "access_token" in data:
            self.access_token = data["access_token"]
            self.token_expires = time.time() + data["expires_in"] - 300  # 提前5分钟刷新
            return self.access_token
        else:
            raise Exception(f"获取 Access Token 失败: {data}")

    def upload_media(self, file_path, media_type="image"):
        """上传媒体文件到微信服务器"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

        with open(file_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)

        return response.json()

    def create_draft(self, title, content, author="", digest="", cover_media_id=""):
        """创建图文消息草稿"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        articles = [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": "",
            "thumb_media_id": cover_media_id,
            "show_cover_pic": 1 if cover_media_id else 0,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]

        data = {"articles": articles}
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})

        return response.json()

    def publish_article(self, media_id):
        """发布图文消息"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"

        data = {"media_id": media_id}
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})

        return response.json()
```

## ⚠️ 重要注意事项

### 1. API 限制
```
- Access Token 有效期: 2小时
- 每日发布数量限制: 根据账号类型不同
- 素材上传大小限制: 图片 2MB，视频 10MB
- API 调用频率限制: 根据公众号等级
```

### 2. 安全要求
```
- AppSecret 必须严格保密
- 服务器需要 HTTPS 协议
- 需要实现消息签名验证
- 建议使用 IP 白名单
```

### 3. 内容规范
```
- 内容必须符合微信公众平台规范
- 不能包含违规内容
- 图片需要审核
- 发布前建议先创建草稿
```

## 🚀 实现步骤建议

### 阶段一：获取开发者权限
1. 注册企业类型的微信公众号
2. 完成认证和开发者设置
3. 获取 AppID 和 AppSecret

### 阶段二：配置开发环境
1. 准备可公网访问的服务器
2. 配置域名和 SSL 证书
3. 实现微信服务器验证

### 阶段三：集成发布功能
1. 实现 Access Token 管理
2. 集成素材上传功能
3. 实现图文消息发布
4. 添加错误处理和重试机制

### 阶段四：测试和优化
1. 使用测试账号进行功能测试
2. 优化发布流程
3. 添加日志和监控
4. 完善错误处理

## 📞 联系信息

如果在配置过程中遇到问题，可以：
1. 查看微信官方文档：https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
2. 联系微信客服：400-616-1616
3. 加入微信开发者社区

---

**注意**：真实的微信公众号自动发布需要企业资质和严格的安全配置，建议在充分了解微信平台规则后再进行实现。