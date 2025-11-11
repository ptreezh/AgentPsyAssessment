# 微信公众号 API 故障排除指南

## 🔍 当前问题分析

### 错误信息
```
{'error': "获取 Access Token 失败: {'errcode': 40164, 'errmsg': 'invalid ip 101.71.206.109 ipv6 ::ffff:101.71.206.109, not in whitelist rid: 690ddc11-194abf89-5ccd9538'}"}
```

### 问题说明
错误代码 **40164** 表示 IP 地址不在白名单中。微信要求所有 API 调用都必须来自预先配置的 IP 地址。

## 🔧 解决方案

### 方案 1: 配置 IP 白名单（推荐）

#### 1.1 登录微信公众平台
1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 使用你的管理员账号登录

#### 1.2 进入 IP 白名单配置
1. 进入 **设置与开发** → **基本配置**
2. 找到 **IP 白名单** 设置
3. 添加你的公网 IP 地址

#### 1.3 获取当前公网 IP
```bash
# 方法1: 使用 curl
curl ipinfo.io/ip

# 方法2: 使用 ipify
curl https://api.ipify.org

# 方法3: 访问网站查看
# 访问 https://www.ip.cn/ 或 https://ipinfo.io/
```

#### 1.4 添加 IP 到白名单
在 IP 白名单中添加：
- `101.71.206.109` (IPv4)
- 如果支持 IPv6，添加 `::ffff:101.71.206.109`

### 方案 2: 使用代理服务器

如果无法直接添加 IP 到白名单，可以使用代理服务器：

#### 2.1 配置代理
```bash
# 使用 HTTP 代理
export HTTP_PROXY=http://your-proxy-server:port
export HTTPS_PROXY=http://your-proxy-server:port

# 使用 SOCKS 代理
export ALL_PROXY=socks5://your-proxy-server:port
```

#### 2.2 修改配置文件
在 `wechat_config/config.json` 中添加代理设置：
```json
{
  "wechat": {
    "appid": "wx62a545a826e36a1b",
    "appsecret": "bc8d96a750f659448bd223727c3cff8a",
    "enabled": true,
    "proxy": {
      "http": "http://proxy-server:port",
      "https": "http://proxy-server:port"
    }
  }
}
```

### 方案 3: 使用云服务器

#### 3.1 租用云服务器
- 腾讯云、阿里云、华为云等
- 确保服务器 IP 可以添加到微信白名单
- 在云服务器上部署你的应用

#### 3.2 配置云服务器
```bash
# 在云服务器上部署
git clone <your-repo>
cd <your-repo>
pip install -r requirements.txt
python wechat_config_wizard.py check
```

## 📋 完整配置检查清单

### ✅ 微信公众平台配置
- [ ] 已完成企业认证（300元/年）
- [ ] AppID 和 AppSecret 已获取
- [ ] IP 白名单已配置
- [ ] API 权限已申请：
  - [ ] 素材管理权限
  - [ ] 图文消息管理权限
  - [ ] 用户管理权限（可选）

### ✅ 本地配置
- [ ] 配置文件已更新
- [ ] AppID: `wx62a545a826e36a1b` ✅
- [ ] AppSecret: `bc8d96a750f659448bd223727c3cff8a` ✅
- [ ] 启用状态: `true` ✅

## 🔄 配置完成后测试

### 步骤 1: 重新测试配置
```bash
python wechat_config_wizard.py check
```

### 步骤 2: 测试 Access Token
```bash
python test_real_wechat_publisher.py token
```

### 步骤 3: 测试文章创建
```bash
python test_real_wechat_publisher.py article
```

### 步骤 4: 完整测试
```bash
python test_real_wechat_publisher.py
```

## 🚨 常见错误和解决方案

### 错误 40164: IP 不在白名单
**原因**: 当前 IP 未在微信白名单中
**解决**: 在微信公众平台添加当前 IP 到白名单

### 错误 40125: AppSecret 无效
**原因**: AppSecret 错误或已被重置
**解决**: 检查 AppSecret，重新获取

### 错误 41001: 缺少 access_token 参数
**原因**: Access Token 获取失败或过期
**解决**: 重新获取 Access Token

### 错误 45009: 多媒体文件大小超出限制
**原因**: 文件太大（图片 > 2MB，视频 > 10MB）
**解决**: 压缩文件或使用更小的文件

### 错误 40001: 不合法的凭证类型
**原因**: AppID 格式错误
**解决**: 检查 AppID 格式，应该以 "wx" 开头

## 📞 获取帮助

### 微信官方支持
- **官方文档**: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
- **客服电话**: 400-616-1616
- **开发者社区**: https://developers.weixin.qq.com/

### 技术支持
- **配置向导**: `python wechat_config_wizard.py`
- **状态检查**: `python wechat_config_wizard.py check`
- **日志查看**: 检查 `wechat_config/logs/` 目录

## 💡 最佳实践建议

### 安全性
- 🔒 不要在代码中硬编码 AppSecret
- 🔒 定期轮换 AppSecret
- 🔒 使用 HTTPS 协议
- 🔒 配置 IP 白名单限制访问

### 稳定性
- ⏰ 实现 Access Token 自动刷新
- 🔄 添加重试机制
- 📊 记录详细的操作日志
- 🚨 实现异常监控和告警

### 开发流程
- 🧪 先在测试环境验证
- ✅ 使用草稿模式避免误发布
- 📝 保存详细的操作记录
- 🔄 定期备份配置和日志

---

**当前状态**: 配置已完成，需要解决 IP 白名单问题才能正常使用真实发布功能。

**下一步**: 登录微信公众平台添加当前 IP `101.71.206.109` 到白名单。