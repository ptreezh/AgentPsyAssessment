# 微信公众号自动发布完整配置指南

## 🎯 回答你的问题

> "我如何配置自己的微信公众号的ID 和账户呢，从而能够自动发到我的微信公众号的呢？"

## 📋 简要回答

### 当前配置状态
- ✅ **模拟版本**：已配置完成，支持 Markdown 转换和模拟发布
- ❌ **真实发布**：需要额外的微信公众号开发者权限配置

### 真实发布需要什么？
1. **企业类型的微信公众号**（个人号无法获取开发者权限）
2. **AppID 和 AppSecret**（从微信公众平台获取）
3. **开发者权限认证**（300元/年认证费）
4. **API 权限申请**（素材管理、图文消息管理权限）

## 🛠️ 完整配置步骤

### 步骤 1: 准备微信公众号账号

#### 1.1 检查账号类型
```
✅ 企业号 - 可以获取完整 API 权限
✅ 政府号 - 可以获取完整 API 权限
✅ 媒体号 - 可以获取完整 API 权限
❌ 个人号 - 无法获取开发者权限
```

#### 1.2 注册企业公众号（如果还没有）
1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 选择 **企业** 类型注册
3. 提交营业执照等企业资质
4. 支付认证费用 300元/年
5. 等待微信审核（通常 1-3 个工作日）

### 步骤 2: 获取开发者配置信息

#### 2.1 登录微信公众平台
1. 进入 **设置与开发** → **基本配置**
2. 复制 **AppID**（18位字符，如：wx1234567890abcdef）
3. 复制 **AppSecret**（32位字符，请妥善保管）

#### 2.2 配置服务器（可选）
如果你需要接收微信消息或回调：
1. **服务器 URL**：需要 HTTPS 协议的公网可访问域名
2. **Token**：自定义令牌，用于验证消息来源
3. **EncodingAESKey**：消息加解密密钥

### 步骤 3: 申请 API 权限

1. 进入 **设置与开发** → **接口权限**
2. 申请以下必需权限：
   - ✅ **素材管理权限**：上传图片、视频等媒体文件
   - ✅ **图文消息管理权限**：创建和发布图文消息
   - ✅ **用户管理权限**：获取用户信息（可选）

3. 提交申请材料，等待审核

### 步骤 4: 使用配置向导

运行我们提供的配置向导：

```bash
# 启动交互式配置向导
python wechat_config_wizard.py

# 检查当前配置状态
python wechat_config_wizard.py check
```

配置向导会引导你：
- ✅ 确认账号类型
- ✅ 输入 AppID 和 AppSecret
- ✅ 配置发布行为（草稿模式/自动发布）
- ✅ 设置默认作者和评论选项

### 步骤 5: 测试配置

```bash
# 测试真实发布功能
python test_real_wechat_publisher.py

# 检查配置状态
python wechat_config_wizard.py check
```

## 📁 配置文件结构

配置完成后，你的配置文件将位于：
```
wechat_config/
├── config.json          # 主配置文件
├── tokens.json          # Access Token 缓存（自动生成）
├── materials/           # 上传的媒体文件
└── logs/               # 发布日志
```

## 🔧 配置文件示例

### wechat_config/config.json
```json
{
  "wechat": {
    "appid": "wx1234567890abcdef",
    "appsecret": "your_32_character_app_secret_here",
    "enabled": true,
    "server_url": "https://your-domain.com/wechat",
    "token": "your_custom_token",
    "encoding_aes_key": "your_encoding_key_here"
  },
  "publish": {
    "auto_publish": false,
    "draft_mode": true,
    "cover_image": "",
    "default_author": "AI Assistant",
    "open_comment": false,
    "only_fans_comment": false
  },
  "api": {
    "timeout": 30,
    "retry_times": 3,
    "token_refresh_buffer": 300
  }
}
```

## 🚀 使用方法

### 1. 通过 MCP 技能调用

配置完成后，你可以使用以下 MCP 技能：

```python
# 检查配置状态
result = mcp__real-wechat-publisher__check_wechat_config()

# 预览文章
result = mcp__real-wechat-publisher__run_real_wechat_publisher(
    markdown_content="# 我的新文章\n\n这是文章内容...",
    title="文章标题",
    author="我的名字",
    preview=True
)

# 发布文章（需要配置自动发布）
result = mcp__real-wechat-publisher__run_real_wechat_publisher(
    markdown_content="# 我的新文章\n\n这是文章内容...",
    title="文章标题",
    author="我的名字",
    preview=False,
    auto_publish=True
)
```

### 2. 通过 CLI 工具调用

```bash
# 检查配置
python wechat_config_wizard.py check

# 测试发布功能
python test_real_wechat_publisher.py
```

## ⚠️ 重要注意事项

### 1. 费用和资质
- **企业认证费**：300元/年
- **服务器费用**：如果需要配置服务器 URL
- **SSL 证书**：需要有效的 HTTPS 证书

### 2. 安全要求
- **严格保密 AppSecret**：泄露后可能导致账号被盗用
- **HTTPS 协议**：服务器必须使用 HTTPS
- **IP 白名单**：建议限制 API 调用来源 IP

### 3. 使用限制
- **API 调用频率**：有每日调用次数限制
- **发布数量限制**：根据公众号等级不同
- **内容审核**：所有发布内容需符合微信平台规范

### 4. 推荐配置
- **草稿模式**：建议先开启草稿模式，手动审核后再发布
- **测试环境**：先使用测试账号进行功能测试
- **日志记录**：启用详细日志以便排查问题

## 🔄 从模拟到真实的切换

### 当前状态
- ✅ 模拟版本：`wechat_publisher_mcp.py` - 仅支持格式转换和模拟发布
- ✅ 真实版本：`wechat_real_publisher_mcp.py` - 支持真实 API 调用

### 切换步骤
1. 配置真实的微信公众号开发者权限
2. 运行 `python wechat_config_wizard.py` 配置 API 信息
3. 使用 `mcp__real-wechat-publisher__` 技能进行真实发布

## 📞 获取帮助

如果在配置过程中遇到问题：

1. **微信官方文档**：https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
2. **微信客服**：400-616-1616
3. **配置向导**：`python wechat_config_wizard.py`
4. **状态检查**：`python wechat_config_wizard.py check`

## 🎯 总结

要配置真实的微信公众号自动发布，你需要：

1. **准备条件**：企业类型微信公众号 + 300元/年认证费
2. **获取配置**：AppID + AppSecret + API 权限
3. **运行向导**：`python wechat_config_wizard.py`
4. **测试功能**：先草稿模式测试，再启用自动发布

目前配置的模拟版本已经可以正常使用，当你准备好真实微信公众号后，可以按照上述步骤升级到真实发布功能。