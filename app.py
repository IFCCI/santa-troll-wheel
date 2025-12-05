import random
import json
import os
import time
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
    """
    从文件中加载已有的抽签结果。
    """
    results = {}
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
    except Exception as e:
        # 如果文件出错，使用空字典防止程序崩溃
        results = {}
    
    # 确保所有人都存在于字典中，防止 Key Error
    full_map = {p: {"santa": None, "troll": None} for p in PARTICIPANTS}
    full_map.update(results)
    return full_map

def save_results(results):
    """
    只负责保存数据到文件，不负责刷新页面。
    """
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        st.session_state.RESULT_MAP = results
    except Exception as e:
        st.error(f"保存失败: {e}")

# 初始化 Session State
if 'RESULT_MAP' not in st.session_state:
    st.session_state.RESULT_MAP = load_results()

RESULT_MAP = st.session_state.RESULT_MAP

# --- 3. 核心算法函数 ---

def get_candidate_list(operator_name, draw_type):
    """
    根据抽签类型 (santa 或 troll) 动态生成候选名单。
    """
    current_data = st.session_state.RESULT_MAP
    
    # 1. 排除操作者本人
    candidates = set(PARTICIPANTS) - {operator_name}

    # 2. 排除已成为该类型(santa/troll)目标的人
    excluded_targets = set()
    for _, result in current_data.items():
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
        return None

    return random.choice(candidates)

# --- 4. Streamlit UI (界面逻辑) ---

# 设置页面配置
st.set_page_config(page_title="IFCCI Santa & Troll", layout="centered")

# 自定义 CSS 美化
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #D42426; /* 圣诞红 */
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 18px;
        color: #165B33; /* 圣诞绿 */
        text-align: center;
        margin-bottom: 30px;
    }
    .success-box {
        padding: 20px;
        background-color: #f0f9f0;
        border-radius: 10px;
        border: 2px solid #165B33;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">🎄 IFCCI Santa & Troll 抽签 😈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">请选择您的名字，抽取您的送礼对象和恶搞对象！</div>', unsafe_allow_html=True)

# --- 计算未完成抽签的人员名单 ---
# 只有当 'troll' 还没抽出来时，才算未完成
uncompleted_participants = [
    p for p in PARTICIPANTS 
    if RESULT_MAP.get(p, {}).get('troll') is None
]

# 显示进度条或文字
progress = len(PARTICIPANTS) - len(uncompleted_participants)
st.progress(progress / len(PARTICIPANTS))
st.caption(f"当前进度: {progress} / {len(PARTICIPANTS)} 人已完成")

st.markdown("---")

# --- 选择名字 ---
st.subheader("我是...")

# 下拉菜单选项：默认提示 + 未完成的人
options = ["-- 请选择您的名字 --"] + uncompleted_participants

selected_name = st.selectbox(
    "选择名字",
    options=options,
    label_visibility="collapsed"
)

# --- 抽签主逻辑 ---
if selected_name != "-- 请选择您的名字 --":
    st.markdown(f"### 👋 你好, {selected_name}")
    
    # 获取当前人的数据
    my_result = RESULT_MAP.get(selected_name, {})
    my_santa = my_result.get('santa')
    my_troll = my_result.get('troll')
    
    # 判断是否完全完成
    if my_santa and my_troll:
        st.markdown(f"""
        <div class="success-box">
            <h3>🎉 您已完成抽签！</h3>
            <p>🎅 您的 Santa 对象: <strong>{my_santa}</strong></p>
            <p>😈 您的 Troll 对象: <strong>{my_troll}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    
    else:
        # 还没完成，显示抽签按钮
        st.info("点击下方按钮，系统将为您同时抽取 Santa 和 Troll。")
        
        if st.button("🎁 开始 IFCCI 抽签 😈", type="primary", use_container_width=True):
            
            # 1. 抽 Santa
            if not my_santa:
                with st.spinner("🎅 正在寻找 Santa 对象..."):
                    time.sleep(1.5) # 增加一点紧张感
                    drawn_santa = spin_wheel(selected_name, 'santa')
                    if drawn_santa:
                        my_result['santa'] = drawn_santa
                        st.success(f"🎅 Santa 对象: {drawn_santa}")
                    else:
                        st.error("无法抽取 Santa (候选人不足)")
                        st.stop()
            else:
                st.info(f"🎅 Santa 对象已存在: {my_santa}")

            # 2. 抽 Troll
            if not my_result.get('troll'):
                with st.spinner("😈 正在寻找 Troll 对象..."):
                    time.sleep(1.5)
                    
                    # 尝试抽取，确保不重复
                    found_troll = None
                    for _ in range(10): # 尝试10次防止死循环
                        temp_troll = spin_wheel(selected_name, 'troll')
                        # 规则：Troll 不能和 Santa 是同一个人
                        if temp_troll != my_result['santa']:
                            found_troll = temp_troll
                            break
                    
                    if found_troll:
                        my_result['troll'] = found_troll
                        st.error(f"😈 Troll 对象: {found_troll}")
                    else:
                        st.error("无法抽取 Troll (候选人冲突或不足)")
                        # 如果 Troll 失败，不保存 Santa，允许重试（可选）
                        st.stop()

            # 3. 保存并刷新
            # 更新内存中的数据
            RESULT_MAP[selected_name] = my_result
            # 保存到文件
            save_results(RESULT_MAP)
            
            st.success("✅ 抽签完成！结果已保存。")
            time.sleep(1) # 让用户看一眼结果再刷新
            st.rerun()
