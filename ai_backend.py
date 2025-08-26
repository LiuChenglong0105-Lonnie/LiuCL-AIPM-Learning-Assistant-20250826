import json
import os
import datetime
import time
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError  # 导入openai常见异常

# 加载.env文件中的环境变量
load_dotenv()

# 定义AI产品经理面试回答指南作为基础prompt（保持不变）
AI_PRODUCT_MANAGER_PROMPT = """你是一名非常资深的AI产品经理。我是一个正在进行AI产品求职的人。我会向你请教一系列AI产品经理面试问题，希望你能结合 AI 产品的特性、行业实践和自身对岗位的理解，给出逻辑清晰、内容详实且有深度的回答。
回答时请遵循以下原则：
只需要进行问题的回答，无需寒暄客套。
字数限制在2000字以内;
针对性：紧密围绕问题核心，不偏离主题；
专业性：体现对 AI 技术（如大模型能力边界、数据安全、算法逻辑等）的扎实认知，不出现技术认知错误；
产品思维：必须有产品经理必备的思维（如用户需求分析、产品定位、迭代策略等）；
商业思维：如果涉及实际业务应用，需要考虑落地性、商业化等问题，体现出商业思维。
表达：语言简洁，用词专业，结构化，采用 "观点 + 分析 " 的模式，先用核心观点回应，再分点展开分析。
案例：如果只讨论理论不足以解释问题，必要时可结合过往经验或行业案例佐证（可合理虚构符合逻辑的经历）；
前瞻性：在回答中体现对 AI 产品发展趋势的思考，如AI产品体验与比较、技术与场景的结合、用户体验的优化方向、伦理合规等潜在问题的应对思路；
"""

# 2. 简化MockArk：仅保留模拟回答功能（删除原SDK兼容逻辑）
class MockArk:
    def chat(self):
        class ChatCompletions:
            def create(self, model, messages, max_tokens=3000, temperature=0.8):
                # 模拟回答（保持原提示文案）
                class MockResponse:
                    class Choices:
                        def __init__(self):
                            self.message = type('obj', (), {'content': "当前环境无法连接到AI服务。这是一个示例回答，展示了AI产品经理学习助手的基本功能。\n\n请配置环境变量ARK_API_KEY以获取完整的AI回答能力。"})
                        @property
                        def choices(self):
                            return [self]
                return MockResponse.Choices()
        return ChatCompletions()

class AIClient:
    def __init__(self, model_name='doubao-seed-1-6-250615'):
        """初始化OpenAI客户端（适配ARK服务），从环境变量获取API密钥"""
        self.api_key = os.environ.get('ARK_API_KEY')
        self.model_name = model_name
        self.client = None
        self.initialize_client()  # 初始化客户端（真实/模拟）
    
    def initialize_client(self):
        """3. 初始化客户端：改用openai.OpenAI，失败则用模拟客户端"""
        try:
            # 若有API密钥，初始化真实OpenAI客户端（指向ARK服务）
            if self.api_key:
                self.client = OpenAI(
                    base_url="https://ark.cn-beijing.volces.com/api/v3",  # ARK的OpenAI兼容接口地址
                    api_key=self.api_key
                )
                print("OpenAI客户端（适配ARK）初始化成功")
            else:
                # 无密钥，使用模拟客户端
                self.client = MockArk()
                print("使用模拟AI客户端（未配置ARK_API_KEY）")
        except Exception as e:
            print(f"初始化客户端失败: {str(e)}")
            self.client = MockArk()
    
    def generate_answer(self, question, category="AI产品经理面试", max_retries=3):
        """4. 生成回答：适配openai库的调用格式"""
        if not self.client:
            self.initialize_client()
            if not self.client:
                return False, "无法初始化AI客户端，请检查API密钥是否正确"
        
        retries = 0
        while retries < max_retries:
            try:
                print(f"处理问题: {question}")
                # 构建提示词（保持原逻辑，确保回答符合AI产品经理指南）
                prompt = f"{AI_PRODUCT_MANAGER_PROMPT}\n\n类别: {category}\n问题: {question}"
                
                print(f"准备调用ARK服务，模型: {self.model_name}")
                print(f"准备发送的prompt长度: {len(prompt)} 字符")
                
                # 调用ARK服务（修改为与test_direct_api_call.py相同的格式）
                response = self.client.chat.completions.create(
                    model=self.model_name,  # ARK的推理接入点ID（不变）
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=3000,  # 保持原配置
                    temperature=0.8   # 保持原配置（控制回答随机性）
                )
                
                print(f"API调用成功，响应类型: {type(response)}")
                print(f"响应属性: {dir(response)}")
                
                # 提取回答（适配openai的响应格式）
                # 注意：真实API响应中，回答在response.choices[0].message.content中
                if hasattr(response, 'choices'):
                    print(f"响应包含choices，数量: {len(response.choices) if hasattr(response.choices, '__len__') else '未知'}")
                    if response.choices and hasattr(response.choices[0], 'message'):
                        answer = response.choices[0].message.content
                        print(f"成功提取回答，长度: {len(answer)} 字符")
                        return True, answer
                    else:
                        print("无法提取回答: choices为空或没有message属性")
                        # 兼容可能的不同响应格式
                        return False, "无法提取AI回答，请检查响应格式"
                else:
                    print("响应不包含choices属性")
                    # 打印完整响应以便调试
                    print(f"完整响应: {response}")
                    return False, "无法提取AI回答，请检查响应格式"

                
            # 5. 异常处理：捕获openai库的常见异常（重试逻辑不变）
            except (APIError, APIConnectionError, RateLimitError) as e:
                retries += 1
                error_msg = f"调用ARK服务失败 (尝试 {retries}/{max_retries}): {str(e)}"
                print(error_msg)
                if retries >= max_retries:
                    return False, error_msg
                time.sleep(2 ** retries)  # 指数退避重试
            except Exception as e:
                retries += 1
                error_msg = f"未知错误 (尝试 {retries}/{max_retries}): {str(e)}"
                print(error_msg)
                if retries >= max_retries:
                    return False, error_msg
                time.sleep(2 ** retries)

# QA保存器（完全不变，保留原功能）
class QASaver:
    def __init__(self, data_file="questions&answers.json"):
        self.data_file = data_file
        self.initialize_data_file()
    
    def initialize_data_file(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        else:
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = []
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_qa(self, question, answer, category):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = []
            current_time = int(time.time())
            qa_id = f"q_{len(data)}_{current_time}"
            new_qa = {
                "id": qa_id,
                "category": category,
                "question": question,
                "status": "completed",
                "answer": answer
            }
            data.append(new_qa)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True, f"问答已保存到 '{category}' 分类"
        except Exception as e:
            return False, f"保存问答失败: {str(e)}"

# 单例模式（不变，供app.py调用）
aiclient = AIClient()
qasaver = QASaver()

# 测试代码（可选，本地运行验证）
if __name__ == "__main__":
    success, result = aiclient.generate_answer("什么是AI产品经理？", "技术原理与基础概念")
    if success:
        print(f"AI回答:\n{result}")
        save_success, save_msg = qasaver.save_qa("什么是AI产品经理？", result, "技术原理与基础概念")
        print(save_msg)
    else:
        print(f"生成回答失败: {result}")