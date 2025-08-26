import json
import os
import datetime
import time
import uuid

# 尝试导入火山引擎SDK，如果失败则使用模拟实现
ARK_AVAILABLE = False
try:
    from volcenginesdkarkruntime import Ark
    ARK_AVAILABLE = True
    print("成功导入火山引擎SDK")
except ImportError:
    print("无法导入火山引擎SDK，将使用模拟实现")

# 定义AI产品经理面试回答指南作为基础prompt
AI_PRODUCT_MANAGER_PROMPT = """你是一名非常资深的AI产品经理。我是一个正在进行AI产品求职的人。我会向你请教一系列AI产品经理面试问题，希望你能结合 AI 产品的特性、行业实践和自身对岗位的理解，给出逻辑清晰、内容详实且有深度的回答。

回答时请遵循以下原则：
只需要进行问题的回答，无需寒暄客套。
字数限制在2000字以内;
针对性：紧密围绕问题核心，不偏离主题；
专业性：体现对 AI 技术（如大模型能力边界、数据安全、算法逻辑等）的扎实认知，不出现技术认知错误；
产品思维：必须有产品经理必备的思维（如用户需求分析、产品定位、迭代策略等）；
商业思维：如果涉及实际业务应用，需要考虑落地性、商业化等问题，体现出商业思维。
表达：语言简洁，用词专业，结构化，采用 "观点 + 分析 " 的模式，先用核心观点回应，再分点展开分析。
案例：如果只讨论理论不足以解释问题，必要时课结合过往经验或行业案例佐证（可合理虚构符合逻辑的经历）；
前瞻性：在回答中体现对 AI 产品发展趋势的思考，如AI产品体验与比较、技术与场景的结合、用户体验的优化方向、伦理合规等潜在问题的应对思路；
"""

# 模拟的Ark类，用于在无法导入真实SDK时提供基本功能
class MockArk:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        
    class Chat:  # 类名从ChatCompletions改为Chat
        def create(self, model, messages, max_tokens=3000, temperature=0.8):
            # 保持原有实现不变
            class MockResponse:
                class Choices:
                    class Message:
                        def __init__(self):
                            self.content = "当前环境无法连接到AI服务。这是一个示例回答，展示了AI产品经理学习助手的基本功能。\n\n请配置环境变量ARK_API_KEY以获取完整的AI回答能力。"
                
                def __init__(self):
                    # 直接引用内部定义的Message类
                    self.message = MockResponse.Choices.Message()
                
                @property
                def choices(self):
                    return [self]
                
            # 创建并返回MockResponse实例
            response = MockResponse()
            return response
    
    @property
    def chat(self):
        return self.Chat()  # 返回Chat类实例而非ChatCompletions

class AIClient:
    def __init__(self, model_name='doubao-seed-1-6-250615'):
        """初始化AI客户端，只从环境变量获取API密钥，确保密钥安全"""
        # 仅从环境变量获取API密钥，彻底避免硬编码风险
        self.api_key = os.environ.get('ARK_API_KEY')
        self.model_name = model_name
        self.client = None
        self.initialize_client()
        
    def initialize_client(self):
        """初始化客户端（真实或模拟）"""
        try:
            if ARK_AVAILABLE and self.api_key:
                self.client = Ark(
                    base_url="https://ark.cn-beijing.volces.com/api/v3",
                    api_key=self.api_key
                )
                print("AI客户端初始化成功")
            else:
                # 使用模拟客户端
                self.client = MockArk()
                print("使用模拟AI客户端")
        except Exception as e:
            print(f"初始化AI客户端失败: {str(e)}")
            self.client = MockArk()
    
    def generate_answer(self, question, category="AI产品经理面试", max_retries=3):
        """
        生成AI回答
        参数:
            question: 用户的问题
            category: 问题类别
            max_retries: 最大重试次数
        返回:
            tuple: (成功标志, 回答内容/错误信息)
        """
        if not self.client:
            self.initialize_client()
            if not self.client:
                return False, "无法初始化AI客户端，请检查API密钥是否正确"
        
        retries = 0
        
        while retries < max_retries:
            try:
                print(f"处理问题: {question}")
                
                # 构建提示词
                prompt = f"{AI_PRODUCT_MANAGER_PROMPT}\n\n类别: {category}\n问题: {question}"
                
                response = self.client.chat.create(  # 移除了中间的completions层级
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ],
                    max_tokens=3000,
                    temperature=0.8
                )
                
                # 提取答案
                answer = response.choices[0].message.content
                
                return True, answer
                
            except Exception as e:
                retries += 1
                error_msg = f"调用API失败 (尝试 {retries}/{max_retries}): {str(e)}"
                print(error_msg)
                
                if retries >= max_retries:
                    return False, error_msg
                # 指数退避重试
                time.sleep(2 ** retries)

class QASaver:
    def __init__(self, data_file="questions&answers.json"):
        """初始化QA保存器"""
        self.data_file = data_file
        self.initialize_data_file()
    
    def initialize_data_file(self):
        """初始化数据文件"""
        if not os.path.exists(self.data_file):
            initial_data = []
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
        else:
            # 尝试读取现有文件，如果格式错误则重新初始化
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 确保数据是列表格式
                if not isinstance(data, list):
                    data = []
                # 保存更新后的数据
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 文件格式错误，重新初始化
                initial_data = []
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
        
    def save_qa(self, question, answer, category):
        """保存问题和答案"""
        try:
            # 读取现有数据
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 确保data是列表格式
            if not isinstance(data, list):
                data = []
            
            # 生成唯一ID
            current_time = int(time.time())
            qa_id = f"q_{len(data)}_{current_time}"
            
            # 创建新的问答项，遵循现有格式
            new_qa = {
                "id": qa_id,
                "category": category,
                "question": question,
                "status": "completed",
                "answer": answer
            }
            
            # 添加到数据列表
            data.append(new_qa)
            
            # 保存数据
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"问答已保存到 '{category}' 分类"
            
        except Exception as e:
            return False, f"保存问答失败: {str(e)}"

# 单例模式，方便app.py调用
aiclient = AIClient()  # 不再传入api_key参数，构造函数会自动从环境变量获取
qasaver = QASaver()

if __name__ == "__main__":
    # 测试代码
    success, result = aiclient.generate_answer("什么是AI产品经理？", "技术原理与基础概念")
    if success:
        print(f"AI回答:\n{result}")
        # 测试保存功能
        save_success, save_msg = qasaver.save_qa("什么是AI产品经理？", result, "技术原理与基础概念")
        print(save_msg)
    else:
        print(f"生成回答失败: {result}")
