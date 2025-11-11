# 🚀 Edge浏览器Vercel微信服务器部署指南

## 📋 重要信息（请复制保存）

**你的微信配置信息：**
- Token: `your_custom_token`
- AppID: `wx62a545a826e36a1b`
- 服务器地址: `https://agentpsy.com/wechat`

---

## 🎯 第一步：登录Vercel

1. **浏览器应该已经打开 Vercel 网站**
2. **点击右上角 "Login" 按钮**
3. **选择 "Continue with GitHub"**
4. **完成GitHub登录授权**

---

## 🎯 第二步：创建GitHub仓库

### 2.1 创建新仓库
1. **新标签页访问**: https://github.com
2. **登录GitHub**
3. **点击右上角 "+" → "New repository"**
4. **填写信息**:
   - Repository name: `wechat-server-vercel`
   - Description: `WeChat Official Account Server for Vercel`
   - 选择: **Public** (免费用户必须选择公开)
5. **点击 "Create repository"**

### 2.2 上传代码文件
1. **在创建的仓库页面，点击 "uploading an existing file"**
2. **打开文件资源管理器，导航到**: `D:\AIDevelop\portable_psyagent\server\vercel\`
3. **将以下4个文件拖拽到浏览器上传区域**:
   - `api/wechat.py`
   - `api/health.py`
   - `vercel.json`
   - `README.md`
4. **上传完成后，点击 "Commit changes"**

---

## 🎯 第三步：在Vercel中导入项目

1. **回到Vercel标签页**
2. **应该自动跳转到项目创建页面**
3. **如果没有自动跳转，访问**: https://vercel.com/new
4. **点击 "Import Git Repository"**
5. **点击 "Continue with GitHub"**
6. **选择刚创建的 `wechat-server-vercel` 仓库**
7. **点击 "Import"**

---

## 🎯 第四步：配置Vercel项目

### 4.1 项目设置
1. **Project Name**: `wechat-server` (可以自定义)
2. **Framework Preset**: 选择 "Other"
3. **Root Directory**: 保持默认 (.)
4. **Build Command**: 留空
5. **Output Directory**: 留空

### 4.2 环境变量设置
1. **滚动到 "Environment Variables" 部分**
2. **添加环境变量**:
   - **Name**: `WECHAT_TOKEN`
   - **Value**: `your_custom_token`
   - **Environment**: 全选 (Production, Preview, Development)
3. **点击 "Add"**

### 4.3 部署项目
1. **点击 "Deploy" 按钮**
2. **等待部署完成 (1-3分钟)**

---

## 🎯 第五步：测试部署

### 5.1 健康检查
1. **部署成功后，复制Vercel提供的URL** (类似: `https://wechat-server-xxx.vercel.app`)
2. **在浏览器中访问**: `https://your-url.vercel.app/api/health`
3. **应该看到**: `{"status":"ok","service":"wechat-server","version":"1.0.0","platform":"vercel"}`

### 5.2 微信验证
1. **登录微信公众平台**: https://mp.weixin.qq.com/
2. **进入**: 设置与开发 → 基本配置
3. **修改服务器配置**:
   - **URL**: `https://your-url.vercel.app/wechat`
   - **Token**: `your_custom_token`
   - **EncodingAESKey**: 随机生成
   - **消息加解密方式**: 明文模式
4. **点击 "提交" 进行验证**

---

## 🔧 重要注意事项

### ✅ 检查清单
- [ ] GitHub仓库已创建并上传代码
- [ ] Vercel项目已导入
- [ ] 环境变量 `WECHAT_TOKEN` 已设置
- [ ] 部署成功
- [ ] 健康检查通过
- [ ] 微信验证通过

### ❌ 常见问题解决

**问题1: 部署失败**
- 检查文件结构是否正确
- 确保 `api/` 目录下的文件存在

**问题2: 环境变量未生效**
- 重新部署项目
- 检查变量名称是否正确

**问题3: 微信验证失败**
- 确保Token在Vercel和微信公众平台完全一致
- 检查URL是否正确 (包含 `/wechat` 路径)

**问题4: 健康检查失败**
- 等待部署完全完成
- 查看Vercel项目日志

---

## 🎉 成功标志

当你完成以下所有步骤，说明部署成功：

1. ✅ **Vercel部署成功** - 项目状态为 "Ready"
2. ✅ **健康检查通过** - 访问 `/api/health` 返回正确JSON
3. ✅ **微信验证成功** - 微信公众平台显示验证通过
4. ✅ **消息测试成功** - 关注公众号并发送测试消息

---

## 📞 需要帮助？

如果遇到任何问题：
1. **检查Vercel项目日志** - 在Vercel控制台查看详细错误信息
2. **确认文件结构** - 确保 `api/wechat.py` 文件存在
3. **验证环境变量** - 确保Token完全一致
4. **重新部署** - 有时重新部署可以解决问题

---

## 🎯 快速复制内容

**GitHub仓库创建**: https://github.com/new
**Vercel项目创建**: https://vercel.com/new
**微信公众平台**: https://mp.weixin.qq.com/

**环境变量配置**:
- Name: `WECHAT_TOKEN`
- Value: `your_custom_token`

---

**按照这个步骤操作，你就能成功部署微信服务器到Vercel！** 🚀