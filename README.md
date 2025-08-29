# AI产品经理学习助手
Streamlit在线链接：https://liucl-ai-pm-learning-assistant-20250827-5hcvkexnytrxapppphyyb.streamlit.app/

一个为AI产品经理设计的学习辅助工具，帮助用户提问、获取AI回答并保存学习卡片。

## 功能特性

- 💡 **AI问答**：输入问题获取AI的专业回答
- 📚 **分类学习**：将问题和答案按照不同类别进行管理
- ⭐ **重点标注**：标记重要的学习内容以便后续复习
- 💾 **本地保存**：保存学习卡片到本地文件系统

## 安全部署指南

为了保护您的API密钥安全，避免泄露风险，本项目采用环境变量方式管理API密钥。请按照以下步骤安全部署：

### 本地开发环境

1. 在您的开发环境中设置环境变量：
   
   ```bash
   # Windows命令行
   set ARK_API_KEY=您的API密钥
   
   # Windows PowerShell
   $env:ARK_API_KEY="您的API密钥"
   
   # Linux/Mac
   export ARK_API_KEY=您的API密钥
   ```

2. 安装依赖：
   
   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用：
   
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud部署

**重要：永远不要直接在代码中硬编码API密钥！**

1. 首先，将项目推送到GitHub仓库
2. 访问 [Streamlit Cloud](https://share.streamlit.io/)
3. 点击 "New app" 创建新应用
4. 选择您的GitHub仓库
5. 在 "Advanced settings" 中：
   - 点击 "Secrets"
   - 添加环境变量：`ARK_API_KEY=您的API密钥`
6. 点击 "Deploy" 完成部署

## 项目结构

- `app.py`：主应用文件，包含Streamlit UI和业务逻辑
- `ai_backend.py`：AI服务接口，处理与火山引擎SDK的交互
- `questions&answers.json`：存储用户问答数据的JSON文件
- `requirements.txt`：项目依赖声明文件

## 依赖说明

- `streamlit`：Web应用框架
- `volcenginesdkarkruntime`（可选）：火山引擎AI模型SDK，本地运行时需要安装

## 安全提示

- 永远不要将API密钥提交到代码仓库中
- 定期更新您的API密钥
- 在Streamlit Cloud中使用Secrets功能保护敏感信息
- 避免在日志或调试信息中打印API密钥

## 免责声明

本项目仅供学习和研究使用，使用时请遵守相关API服务提供商的使用条款和政策。
