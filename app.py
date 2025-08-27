import os

# 重要：必须在导入streamlit之前设置这个环境变量，以禁用文件监控
os.environ['STREAMLIT_DISABLE_FILE_WATCHING'] = 'true'

import streamlit as st
import json
from datetime import datetime
import uuid
import sys
import time

# 注意：在Streamlit Cloud环境中，API密钥通过secrets提供，而不是.env文件
# 以下代码已优化以适应Streamlit Cloud环境

# 尝试导入ai_backend模块，如果失败提供替代方案
class MockAIClient:
    def generate_answer(self, question, category="AI产品经理面试", max_retries=3):
        return True, "当前环境无法连接到AI服务。这是一个示例回答，展示了AI产品经理学习助手的基本功能。\n\n请配置环境变量ARK_API_KEY以获取完整的AI回答能力。"

class MockQASaver:
    def save_qa(self, question, answer, category):
        return True, "本地保存功能已启用" # 修改为更友好的提示

# 检查环境变量中是否设置了API密钥
has_api_key = 'ARK_API_KEY' in os.environ and os.environ['ARK_API_KEY']

# 无论是否有API密钥，都尝试导入ai_backend模块
try:
    from ai_backend import aiclient, qasaver
    # 如果没有API密钥，使用模拟对象
    if not has_api_key:
        aiclient = MockAIClient()
        qasaver = MockQASaver()
    st.session_state["ai_backend_available"] = True  # 只要能导入ai_backend，就认为可用
    st.session_state["has_api_key"] = has_api_key
    st.session_state["aiclient_type"] = type(aiclient).__name__  # 记录aiclient的类型以便调试
    
except ImportError as e:
    st.warning(f"无法导入ai_backend模块: {str(e)}，将使用基础功能模式")
    # 使用模拟对象
    aiclient = MockAIClient()
    qasaver = MockQASaver()
    st.session_state["ai_backend_available"] = False
    st.session_state["has_api_key"] = has_api_key
    st.session_state["aiclient_type"] = "MockAIClient"

st.set_page_config(
    page_title="AI产品经理学习助手",
    page_icon="📚",
    layout="wide"
)

st.sidebar.title("📚 AI产品经理学习助手")
page = st.sidebar.radio(
    "选择功能:",
    ["AI解答", "技术原理与基础概念", "产品设计与用户体验",
     "产品落地与工程实践", "特定场景与行业应用",
     "团队协作与职业发展", "重点标注学习"]
)

DATA_FILE = "questions&answers.json"

# 使用缓存来减少文件读取频率
_data_cache = None
_last_cache_time = 0
CACHE_DURATION = 5  # 缓存持续时间（秒）


def read_data():
    global _data_cache, _last_cache_time
    current_time = time.time()
    
    # 检查缓存是否有效
    if _data_cache and (current_time - _last_cache_time) < CACHE_DURATION:
        return _data_cache
    
    try:
        if not os.path.exists(DATA_FILE):
            result = {
                "AI解答": [],
                "技术原理与基础概念": [],
                "产品设计与用户体验": [],
                "产品落地与工程实践": [],
                "特定场景与行业应用": [],
                "团队协作与职业发展": [],
                "重点标注学习": []
            }
            # 缓存结果
            _data_cache = result
            _last_cache_time = current_time
            return result
        
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        categorized_data = {
            "AI解答": [],
            "技术原理与基础概念": [],
            "产品设计与用户体验": [],
            "产品落地与工程实践": [],
            "特定场景与行业应用": [],
            "团队协作与职业发展": [],
            "重点标注学习": []
        }
        
        for item in data:
            if isinstance(item, dict):
                category = item.get("category", "AI解答")
                qa_item = {
                    "id": item.get("id", str(uuid.uuid4())),
                    "question": item.get("question", ""),
                    "answer": item.get("answer", ""),
                    "category": category,
                    "timestamp": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "starred": item.get("starred", False)
                }
                if category in categorized_data:
                    categorized_data[category].append(qa_item)
        
        starred_items = []
        for cat in ["技术原理与基础概念", "产品设计与用户体验", "产品落地与工程实践", "特定场景与行业应用", "团队协作与职业发展"]:
            for item in categorized_data[cat]:
                if item.get("starred"):
                    starred_items.append(item)
        categorized_data["重点标注学习"] = starred_items
        
        # 缓存结果
        _data_cache = categorized_data
        _last_cache_time = current_time
        return categorized_data
    except Exception as e:
        st.error(f"读取数据时出错: {str(e)}")
        result = {
            "AI解答": [],
            "技术原理与基础概念": [],
            "产品设计与用户体验": [],
            "产品落地与工程实践": [],
            "特定场景与行业应用": [],
            "团队协作与职业发展": [],
            "重点标注学习": []
        }
        return result


def save_data(data):
    global _data_cache, _last_cache_time
    all_items = []
    
    try:
        for category, items in data.items():
            if category != "重点标注学习":
                for item in items:
                    qa_item = {
                        "id": item["id"],
                        "category": item["category"],
                        "question": item["question"],
                        "answer": item["answer"],
                        "timestamp": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "starred": item.get("starred", False)
                    }
                    all_items.append(qa_item)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(DATA_FILE) if os.path.dirname(DATA_FILE) else '.', exist_ok=True)
        
        # 写入文件
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)
        
        # 清除缓存，下次读取时更新
        _data_cache = None
        _last_cache_time = 0
        
    except Exception as e:
        st.error(f"保存数据时出错: {str(e)}")

for key in ["current_question", "current_answer", "current_category", "ai_answered"]:
    if key not in st.session_state:
        st.session_state[key] = ""

if "ai_answered" not in st.session_state:
    st.session_state["ai_answered"] = False

if page == "AI解答":
    st.title("💡 AI解答")
    st.write("输入你的问题，获取AI的回答，并可以保存为学习卡片")

    question = st.text_area("请输入你的问题:", key="input_question", height=150, value=st.session_state.get("current_question", ""))

    category = st.selectbox(
        "选择问题类别:",
        ["技术原理与基础概念", "产品设计与用户体验",
         "产品落地与工程实践", "特定场景与行业应用",
         "团队协作与职业发展"],
        key="input_category",
        index=["技术原理与基础概念", "产品设计与用户体验",
               "产品落地与工程实践", "特定场景与行业应用",
               "团队协作与职业发展"].index(
                   st.session_state.get("current_category", "技术原理与基础概念") 
                   if st.session_state.get("current_category") in ["技术原理与基础概念", "产品设计与用户体验", "产品落地与工程实践", "特定场景与行业应用", "团队协作与职业发展"] 
                   else "技术原理与基础概念"
               )
    )

    if st.button("向AI提问", key="ask_ai", use_container_width=True):
        if question.strip():
            with st.spinner("AI正在思考中..."):
                try:
                    success, result = aiclient.generate_answer(question, category)
                    if success:
                        st.session_state["current_question"] = question
                        st.session_state["current_answer"] = result
                        st.session_state["current_category"] = category
                        st.session_state["ai_answered"] = True
                    else:
                        st.error(f"获取AI回答失败: {result}")
                        st.session_state["ai_answered"] = False
                except Exception as e:
                    st.error(f"调用AI后端时发生错误: {str(e)}")
                    st.session_state["ai_answered"] = False
        else:
            st.warning("请输入问题后再提问")
            st.session_state["ai_answered"] = False

    if st.session_state.get("ai_answered", False) and st.session_state.get("current_answer", ""):
        st.subheader("AI回答:")
        st.write(st.session_state["current_answer"])

        if st.button("保存卡片", key="save_card", use_container_width=True):
            try:
                data = read_data()
                new_item = {
                    "id": str(uuid.uuid4()),
                    "question": st.session_state["current_question"],
                    "answer": st.session_state["current_answer"],
                    "category": st.session_state["current_category"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "starred": False
                }
                data[st.session_state["current_category"]].append(new_item)
                save_data(data)
                try:
                    save_success, save_msg = qasaver.save_qa(
                        st.session_state["current_question"],
                        st.session_state["current_answer"],
                        st.session_state["current_category"]
                    )
                    if save_success:
                        st.success(f"{save_msg}（知识卡片保存成功！）")
                    else:
                        st.warning("本地保存成功，但后端保存失败: " + str(save_msg))
                except Exception as e:
                    st.warning("本地保存成功，但后端接口异常: " + str(e))
                # 保存后不清空内容
            except Exception as e:
                st.error(f"保存卡片时发生错误: {str(e)}")

else:
    st.title(f"📖 {page}")
    data = read_data()
    category_items = data.get(page, [])
    category_items.sort(key=lambda x: x["timestamp"], reverse=True)
    st.write(f"共 {len(category_items)} 个学习卡片")
    search_query = st.text_input("搜索问题:")
    if search_query:
        filtered_items = [
            item for item in category_items
            if search_query.lower() in item["question"].lower() or
               search_query.lower() in item["answer"].lower()
        ]
    else:
        filtered_items = category_items
    if search_query:
        st.write(f"找到 {len(filtered_items)} 个相关卡片")
    if filtered_items:
        for item in filtered_items:
            # 将问题标题作为expander的标题，让用户不需要展开就能看到
            with st.expander(f"⭐  {item['question']}"):
                
                # 将按钮移到正文上方，并调整收藏按钮在删除按钮之前
                col1, col2 = st.columns(2)
                with col1:
                    if page != "重点标注学习":
                        if item.get("starred", False):
                            if st.button("取消收藏", key=f"unstar_{item['id']}", use_container_width=True):
                                for i in data[page]:
                                    if i["id"] == item["id"]:
                                        i["starred"] = False
                                data["重点标注学习"] = [i for i in data["重点标注学习"] if i["id"] != item["id"]]
                                save_data(data)
                                st.success("已取消收藏！")
                                st.rerun()
                        else:
                            if st.button("收藏", key=f"star_{item['id']}", use_container_width=True):
                                for i in data[page]:
                                    if i["id"] == item["id"]:
                                        i["starred"] = True
                                data["重点标注学习"].append(item)
                                save_data(data)
                                st.success("已收藏到重点标注学习！")
                                st.rerun()
                    else:
                        if st.button("取消收藏", key=f"unstar_{item['id']}", use_container_width=True):
                            data["重点标注学习"] = [i for i in data["重点标注学习"] if i["id"] != item["id"]]
                            for category in ["技术原理与基础概念", "产品设计与用户体验",
                                             "产品落地与工程实践", "特定场景与行业应用",
                                             "团队协作与职业发展"]:
                                for i in data[category]:
                                    if i["id"] == item["id"]:
                                        i["starred"] = False
                            save_data(data)
                            st.success("已取消收藏！")
                            st.rerun()
                with col2:
                    if st.button("删除", key=f"delete_{item['id']}", use_container_width=True):
                        data[page] = [i for i in data[page] if i["id"] != item["id"]]
                        if item.get("starred", False) and page != "重点标注学习":
                            data["重点标注学习"] = [i for i in data["重点标注学习"] if i["id"] != item["id"]]
                        save_data(data)
                        st.success("卡片已删除！")
                        st.rerun()
                # 正文内容移到按钮下方，使用更大的字体显示回答
                st.markdown(f"<span style='font-size: 1.1rem;'>{item['answer']}</span>", unsafe_allow_html=True)
                st.caption(f"创建时间: {item['timestamp']}")
    else:
        st.info("该分类下暂无学习卡片")

st.sidebar.markdown("---")
st.sidebar.info("AI产品经理学习助手 - 让知识触手可及")
