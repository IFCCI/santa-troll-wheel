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
# 在 Streamlit Cloud 中，应用实例会重启，文件系统写入是临时的
# 对于这种游戏，我们依赖文件写入，但如果应用长时间不活跃或 Streamlit 容器重启，数据会重置。
# 对于一次性活动或短期游戏，这是可接受的。
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
    # 用加载的结果覆盖初始 map
    initial_map.update(results)
    return initial_map

def save_results(results):
    """将抽签结果保存到文件，并更新 Session State。"""
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    st.session_state.RESULT_MAP = results # 更新 session state 中的 RESULT_MAP
    st.experimental_rerun() # 重新运行脚本以更新界面状态

# 使用 Streamlit Session State 来保持状态，这是在 Web 应用中管理数据流的关键
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

st.set_page_config(page_title="🎄 Santa & Troll 抽签轮盘", layout="centered", initial_sidebar_state="collapsed")
st.title("🎄 Santa & Troll 抽签轮盘")
st.markdown("---")

# 显示当前已完成抽签人数
RESULT_MAP = st.session_state.RESULT_MAP
completed_participants = [p for p in PARTICIPANTS if RESULT_MAP.get(p, {}).get('troll') is not None]
st.info(f"✅ 已完成抽签人数: **{len(completed_participants)} / {len(PARTICIPANTS)}**")
st.markdown("---")

# --- 步骤 1: 选择操作者 ---
st.subheader("请选择您的名字开始抽签：")
operator = st.selectbox(
    "选择您的名字",
    options=["--请选择--"] + PARTICIPANTS,
    index=0,
    label_visibility="collapsed"
)

if operator != "--请选择--":
    st.markdown(f"### 您选择了: **{operator}**")
    st.markdown("---")
    
    current_result = RESULT_MAP.get(operator, {})
    is_completed = current_result.get('troll') is not None

    if is_completed:
        st.success(f"🎉 **{operator}，您已完成抽签！**")
        st.metric("您的 Santa 对象是", current_result['santa'])
        st.metric("您的 Troll 对象是", current_result['troll'])
        st.balloons() # 庆祝气球动画
        st.warning("请记住您的对象，祝您圣诞快乐！")
    else:
        # --- 步骤 2 & 3: 抽签按钮 ---
        st.markdown("点击下面的按钮开始抽签，您将抽到一位 Santa 对象和一位 Troll 对象。")
        if st.button("🎁 开始我的抽签 😈", type="primary", use_container_width=True):
            
            # --- Santa 抽签逻辑 ---
            drawn_santa = current_result.get('santa')
            if drawn_santa is None:
                with st.spinner("🎅 正在为您抽取 Santa 对象..."):
                    import time
                    time.sleep(2) # 模拟抽签过程
                    drawn_santa = spin_wheel(operator, 'santa')

                if drawn_santa:
                    st.success(f"🎉 您的 Santa 对象抽中: **{drawn_santa}** (您将送礼物给 Ta!)")
                    current_result['santa'] = drawn_santa
                else:
                    st.error("由于未知错误，未能抽取 Santa 对象。请稍后再试。")
            else:
                st.info(f"您的 Santa 对象已是: **{drawn_santa}**")
                
            # 如果 Santa 抽中，继续抽 Troll
            if drawn_santa and current_result.get('troll') is None:
                st.markdown("---")
                with st.spinner("😈 正在为您抽取 Troll 对象..."):
                    import time
                    time.sleep(2) # 模拟抽签过程
                    
                    drawn_troll = None
                    attempts = 0 
                    
                    while attempts < 10: # 最多重试10次
                        drawn_troll = spin_wheel(operator, 'troll')
                        
                        if drawn_troll is None:
                            st.error("无法找到 Troll 候选人。")
                            break

                        if drawn_troll == drawn_santa:
                            st.warning(f"❗❗ 警告：抽中的 Troll ({drawn_troll}) 与 Santa ({drawn_santa}) 重复了。自动重抽...")
                            attempts += 1
                            continue 
                        
                        # 抽签成功
                        st.error(f"😈 您的 Troll 对象抽中: **{drawn_troll}** (您将恶搞 Ta!)")
                        current_result['troll'] = drawn_troll
                        break
                
                if drawn_troll:
                    st.success("恭喜您完成抽签！")
                    st.balloons()
                    st.warning("请记住您的对象，祝您圣诞快乐！")
                else:
                    st.error("由于未知错误，未能抽取 Troll 对象。请稍后再试。")

            # 无论 Santa 还是 Troll 完成，都保存结果并刷新页面
            save_results(RESULT_MAP)