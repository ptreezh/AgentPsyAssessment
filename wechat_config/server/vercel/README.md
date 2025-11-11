# Vercel 部署微信公众号服务器

## 🚀 快速部署

### 方案1: 通过GitHub部署（推荐）

1. **将代码推送到GitHub**
   ```bash
   # 创建新的GitHub仓库
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/wechat-server.git
   git push -u origin main
   ```

2. **连接Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 使用GitHub账号登录
   - 点击 "New Project"
   - 选择你的GitHub仓库
   - 点击 "Import"

3. **配置环境变量**
   在Vercel项目设置中添加环境变量：
   - `WECHAT_TOKEN`: 你的微信Token

4. **部署完成！**
   - Vercel会自动部署
   - 你会获得一个 `.vercel.app` 域名
   - 服务器URL: `https://your-project.vercel.app/wechat`

### 方案2: 通过Vercel CLI部署

1. **安装Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录Vercel**
   ```bash
   vercel login
   ```

3. **部署项目**
   ```bash
   cd vercel
   vercel
   ```

4. **设置环境变量**
   ```bash
   vercel env add WECHAT_TOKEN
   ```

## ⚙️ 配置说明

### 1. 微信公众平台配置

登录 [微信公众平台](https://mp.weixin.qq.com/)：

1. 进入 **设置与开发** → **基本配置**
2. 配置服务器信息：
   - **URL**: `https://your-project.vercel.app/wechat`
   - **Token**: 与你在Vercel中设置的Token一致
   - **EncodingAESKey**: 随机生成（可选）
   - **消息加解密方式**: 明文模式（推荐）

3. 点击 **提交** 进行验证

### 2. 环境变量配置

在Vercel项目设置中配置：

```env
WECHAT_TOKEN=your_custom_token_here
```

## 🧪 测试部署

### 1. 健康检查
```bash
curl https://your-project.vercel.app/api/health
```

预期响应：
```json
{
  "status": "ok",
  "service": "wechat-server",
  "version": "1.0.0",
  "platform": "vercel"
}
```

### 2. 微信验证测试
- 在微信公众平台点击"提交"按钮
- 查看Vercel函数日志确认验证成功

### 3. 消息测试
- 关注微信公众号
- 发送测试消息如"帮助"或"评估"
- 确认收到自动回复

## 📊 监控和日志

### 查看日志
1. 访问Vercel项目控制台
2. 点击 "Functions" 标签
3. 选择 `api/wechat.py` 函数
4. 查看实时日志

### 监控指标
- 函数执行时间
- 调用次数
- 错误率
- 响应时间

## 🔧 自定义配置

### 修改自动回复内容

编辑 `api/wechat.py` 中的 `get_auto_reply` 方法：

```python
def get_auto_reply(self, user_message):
    user_message = user_message.lower().strip()

    if '关键词1' in user_message:
        return "自定义回复1"
    elif '关键词2' in user_message:
        return "自定义回复2"
    else:
        return "默认回复"
```

### 添加新的消息类型处理

在 `do_POST` 方法中添加新的消息类型：

```python
if msg_type == 'text':
    response = self.handle_text_message(xml_data)
elif msg_type == 'image':
    response = self.handle_image_message(xml_data)  # 新增
elif msg_type == 'event':
    response = self.handle_event_message(xml_data)
```

## 🚨 故障排除

### 常见问题

1. **验证失败**
   - 检查Token是否与微信公众平台一致
   - 确认URL格式正确：`https://your-domain.vercel.app/wechat`
   - 查看Vercel函数日志

2. **超时错误**
   - Vercel函数最大执行时间为10秒
   - 检查函数是否有无限循环
   - 优化代码执行时间

3. **消息接收失败**
   - 查看Vercel函数日志
   - 确认XML解析正确
   - 检查响应格式

### 调试技巧

1. **添加调试日志**
   ```python
   print(f"Debug: 收到消息 - {xml_data}")
   ```

2. **本地测试**
   ```bash
   # 使用Vercel CLI本地测试
   vercel dev
   ```

3. **查看详细错误**
   在Vercel控制台查看函数执行详情

## 🔄 更新和维护

### 更新代码
```bash
# 修改代码后
git add .
git commit -m "Update wechat server"
git push

# Vercel会自动重新部署
```

### 回滚部署
1. 访问Vercel项目控制台
2. 点击 "Deployments"
3. 找到之前的部署版本
4. 点击 "..." 菜单选择 "Promote to Production"

## 💰 成本

### Vercel免费套餐
- **函数执行**: 100GB-小时/月
- **带宽**: 100GB/月
- **请求数**: 无限制
- **冷启动**: 免费套餐可能有一点延迟

对于微信公众号使用，免费套餐完全足够！

## 🌐 自定义域名

### 配置自定义域名
1. 在Vercel项目设置中点击 "Domains"
2. 添加你的域名：`agentpsy.com`
3. 配置DNS记录：
   ```
   CNAME  agentpsy.com  cname.vercel-dns.com
   ```

### 微信公众平台URL
使用自定义域名后，更新微信公众平台URL为：
```
https://agentpsy.com/wechat
```

## 📝 功能特性

✅ **Serverless架构**: 无需管理服务器
✅ **自动HTTPS**: Vercel提供免费SSL证书
✅ **全球CDN**: 快速响应
✅ **自动扩展**: 根据请求量自动扩展
✅ **免费套餐**: 个人使用完全免费
✅ **Git集成**: 与GitHub/GitLab完美集成
✅ **实时日志**: 方便调试和监控
✅ **自定义域名**: 支持品牌域名

## 🎉 部署完成

完成以上步骤后，你就拥有了一个完全功能、免费、可靠的微信公众号服务器！

现在你可以：
- 接收和回复微信消息
- 处理用户关注事件
- 设置关键词自动回复
- 监控服务器状态

部署成功后，你的微信公众号就能正常接收和回复消息了！