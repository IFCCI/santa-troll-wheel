import random
import json
import os
import streamlit as st

# --- 1. 核心数据 ---

# 参加者名单（14 人）
PARTICIPANTS = [
    "Dato’ Kingston", "Datin Paris", "Wena", "Zi Qing", "Zhen Hao", 
    "Jeffrey", "Klain", "Daniel Ang", "Kingston Neo", "Kimberly", 
    "Hanshon", "Cassey", "Bryan", "Melissa"
]

# 存储文件路径
STORAGE_FILE = 'draw_results.json'

# --- 2. 文件和状态管理 ---

def load_results():
    """从文件中加载已有的抽签结果，如果文件不存在则返回初始化字典。"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            results = {} # 文件不存在，从空字典开始
    except json.JSONDecodeError:
        st.error("⚠️ 警告: 结果文件损坏，已重置结果。")
        results = {}
    
    # 确保所有人都存在于 ResultMap 中
    initial_map = {p: {"santa": None, "troll": None} for p in PARTICIPANTS}
    initial_map.update(results)
    return initial_map

def save_results(results):
    """将抽签结果保存到文件，并更新 Session State。"""
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    st.session_state.RESULT_MAP = results
    st.experimental_rerun() # 重新运行脚本以更新界面状态

# 使用 Streamlit Session State 来保持状态
if 'RESULT_MAP' not in st.session_state:
    st.session_state.RESULT_MAP = load_results()

# --- 3. 核心算法函数 ---

def get_candidate_list(operator_name, draw_type):
    """
    根据抽签类型 (santa 或 troll) 动态生成候选名单。
    """
    results = st.session_state.RESULT_MAP
    
    # 1. 排除操作者本人
    candidates = set(PARTICIPANTS) - {operator_name}

    # 2. 排除已成为目标的人
    excluded_targets = set()
    for _, result in results.items():
        target = result.get(draw_type)
        if target is not None:
            excluded_targets.add(target)

    # 最终候选名单
    final_candidates = list(candidates - excluded_targets)
    random.shuffle(final_candidates) 

    return final_candidates

def spin_wheel(operator_name, draw_type):
    """执行一次抽签并返回结果。"""
    candidates = get_candidate_list(operator_name, draw_type)

    if not candidates:
        st.error(f"❌ {draw_type.upper()} 候选名单为空！无法抽签。")
        return None

    drawn_name = random.choice(candidates)
    return drawn_name

# --- 4. Streamlit UI/主程序 ---

# --- UI 美化部分 ---
st.set_page_config(page_title="🎄 IFCCI Santa & Troll 抽签轮盘", layout="centered", initial_sidebar_state="collapsed")

# 增加一些 CSS 来自定义样式
st.markdown("""
    <style>
    .big-title {
        font-size: 36px !important;
        font-weight: bold;
        color: #ff4b4b; /* 圣诞红 */
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 24px !important;
        font-weight: bold;
        color: #008000; /* 圣诞绿 */
        text-align: center;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .stSelectbox label {
        font-size: 18px;
        font-weight: bold;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🎄 IFCCI Santa & Troll 抽签轮盘 😈</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">请选择您的名字，点击按钮进行抽签！</p>', unsafe_allow_html=True)
st.markdown("---")

RESULT_MAP = st.session_state.RESULT_MAP

# 筛选出尚未完成抽签的人员列表 (Santa 或 Troll 任一为 None)
uncompleted_participants = [
    p for p in PARTICIPANTS 
    if RESULT_MAP.get(p, {}).get('santa') is None or RESULT_MAP.get(p, {}).get('troll') is None
]
completed_participants = len(PARTICIPANTS) - len(uncompleted_participants)

# 状态显示
st.info(f"✅ 已完成抽签人数: **{completed_participants} / {len(PARTICIPANTS)}**")
st.markdown("---")

# --- 步骤 1: 选择操作者 ---
st.subheader("请选择您的名字：")

# 选项只包含未完成抽签的人员
operator_options = ["--请选择您的名字--"] + uncompleted_participants

operator = st.selectbox(
    "选择您的名字",
    options=operator_options,
    index=0,
    label_visibility="collapsed"
)

if operator != "--请选择您的名字--":
    st.markdown(f"### 您选择了: **{operator}**")
    st.markdown("---")
    
    current_result = RESULT_MAP.get(operator, {})
    is_completed = current_result.get('troll') is not None # 只要 Troll 抽完，就视为完成

    if is_completed:
        # 如果用户选择了一个虽然没有在下拉列表，但数据中已完成的人（比如有人手动输入或 URL 传入），则显示结果
        st.success(f"🎉 **{operator}，您已完成抽签！**")
        st.metric("您的 Santa 对象是", current_result['santa'])
        st.metric("您的 Troll 对象是", current_result['troll'])
        st.balloons()
        st.warning("请记住您的对象，祝您圣诞快乐！")
    else:
        # --- 步骤 2 & 3: 抽签按钮 ---
        st.markdown("点击下面的按钮开始抽签，您将抽到一位 Santa 对象和一位 Troll 对象。")
        if st.button("🎁 开始我的抽签 😈", type="primary", use_container_width=True):
            
            # --- Santa 抽签逻辑 ---
            drawn_santa = current_result.get('santa')
            
            if drawn_santa is None:
                st.subheader("🎅 抽 Santa Wheel...")
                with st.spinner("正在为您抽取 Santa 对象..."):
                    import time
                    time.sleep(2) # 模拟抽签过程
                    drawn_santa = spin_wheel(operator, 'santa')

                if drawn_santa:
                    st.success(f"🎉 Santa 对象抽中: **{drawn_santa}** (您将送礼物给 Ta!)")
                    current_result['santa'] = drawn_santa
                else:
                    st.error("未能抽取 Santa 对象。")
            else:
                st.info(f"您的 Santa 对象已是: **{drawn_santa}**")
                
            # 如果 Santa 抽中，继续抽 Troll
            drawn_troll = current_result.get('troll')
            if drawn_santa and drawn_troll is None:
                st.markdown("---")
                st.subheader("😈 抽 Troll Wheel...")
                with st.spinner("正在为您抽取 Troll 对象..."):
                    import time
                    time.sleep(2) # 模拟抽签过程
                    
                    drawn_troll = None
                    attempts = 0 
                    
                    while attempts < 10:
                        drawn_troll = spin_wheel(operator, 'troll')
                        
                        if drawn_troll is None:
                            st.error("无法找到 Troll 候选人。")
                            break

                        if drawn_troll == drawn_santa:
                            st.warning(f"❗❗ 警告：抽中的 Troll ({drawn_troll}) 与 Santa ({drawn_santa}) 重复了。自动重抽...")
                            attempts += 1
                            continue 
                        
                        # 抽签成功
                        st.error(f"😈 Troll 对象抽中: **{drawn_troll}** (您将恶搞 Ta!)")
                        current_result['troll'] = drawn_troll
                        break
                
                if drawn_troll:
                    st.success("恭喜您完成抽签！")
                    st.balloons()
                    st.warning("请记住您的对象，祝您圣诞快乐！")
                else:
                    st.error("未能抽取 Troll 对象。")

            # 无论 Santa 还是 Troll 完成，都保存结果并刷新页面
            save_results(RESULT_MAP)
