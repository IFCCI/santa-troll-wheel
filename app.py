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
    """从文件中加载已有的抽签结果。"""
    results = {}
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
    except Exception:
        results = {}
    
    # 确保所有人都存在于字典中
    full_map = {p: {"santa": None, "troll": None} for p in PARTICIPANTS}
    full_map.update(results)
    return full_map

def save_results(results):
    """保存数据到文件"""
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

# --- 3. 核心算法 ---

def get_candidate_list(operator_name, draw_type):
    current_data = st.session_state.RESULT_MAP
    candidates = set(PARTICIPANTS) - {operator_name}
    excluded_targets = set()
    for _, result in current_data.items():
        target = result.get(draw_type)
        if target is not None:
            excluded_targets.add(target)
    final_candidates = list(candidates - excluded_targets)
    random.shuffle(final_candidates) 
    return final_candidates

def spin_wheel(operator_name, draw_type):
    candidates = get_candidate_list(operator_name, draw_type)
    if not candidates: return None
    return random.choice(candidates)

# --- 4. Streamlit UI ---

st.set_page_config(page_title="IFCCI Santa & Troll", layout="centered")

# CSS 美化
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #D42426; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #165B33; text-align: center; margin-bottom: 20px; }
    .result-card {
        padding: 20px;
        border-radius: 15px;
        background-color: #f8fff8;
        border: 2px solid #165B33;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .emoji-large { font-size: 40px; }
    .name-large { font-size: 28px; font-weight: bold; color: #333; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎄 IFCCI Santa & Troll 抽签 😈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">2024 Christmas Edition</div>', unsafe_allow_html=True)

# 计算未完成名单
uncompleted_participants = [p for p in PARTICIPANTS if RESULT_MAP.get(p, {}).get('troll') is None]

# 进度条
progress = len(PARTICIPANTS) - len(uncompleted_participants)
st.progress(progress / len(PARTICIPANTS))
st.caption(f"进度: {progress} / {len(PARTICIPANTS)} 已完成")

st.markdown("---")

# 名字选择
st.subheader("我是...")
options = ["-- 请选择您的名字 --"] + uncompleted_participants
selected_name = st.selectbox("选择名字", options=options, label_visibility="collapsed")

# 主逻辑
if selected_name != "-- 请选择您的名字 --":
    st.markdown(f"### 👋 你好, {selected_name}")
    
    my_result = RESULT_MAP.get(selected_name, {})
    my_santa = my_result.get('santa')
    my_troll = my_result.get('troll')

    # 情况 A: 已经完全抽完了 (可能是手动输入了已完成的名字，或者刚抽完没刷新)
    if my_santa and my_troll:
        st.markdown(f"""
        <div class="result-card">
            <div class="emoji-large">🎅</div>
            <div>你的 Santa 对象是</div>
            <div class="name-large">{my_santa}</div>
            <div style="color:gray; font-size:12px;">(你要送礼物给 TA)</div>
            <hr>
            <div class="emoji-large">😈</div>
            <div>你的 Troll 对象是</div>
            <div class="name-large">{my_troll}</div>
            <div style="color:gray; font-size:12px;">(你要恶搞 TA)</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        
        # 添加手动刷新按钮
        if st.button("✅ 我记住了，下一位", type="primary", use_container_width=True):
            st.rerun()
            
    # 情况 B: 还没抽
    else:
        st.info("点击下方按钮，抽取你的对象！")
        
        if st.button("🎁 开始抽签 😈", type="primary", use_container_width=True):
            
            # 1. 抽 Santa
            if not my_santa:
                with st.spinner("🎅 正在寻找 Santa..."):
                    time.sleep(1)
                    drawn_santa = spin_wheel(selected_name, 'santa')
                    if drawn_santa:
                        my_result['santa'] = drawn_santa
                    else:
                        st.error("无法抽取 Santa (候选人不足)")
                        st.stop()
            
            # 2. 抽 Troll
            if not my_result.get('troll'):
                with st.spinner("😈 正在寻找 Troll..."):
                    time.sleep(1)
                    found_troll = None
                    for _ in range(10): 
                        temp_troll = spin_wheel(selected_name, 'troll')
                        if temp_troll != my_result['santa']:
                            found_troll = temp_troll
                            break
                    
                    if found_troll:
                        my_result['troll'] = found_troll
                    else:
                        st.error("无法抽取 Troll (候选人冲突)")
                        st.stop()

            # 3. 保存
            RESULT_MAP[selected_name] = my_result
            save_results(RESULT_MAP)
            
            # 4. 这里的关键修改：不自动刷新，而是强制手动刷新页面以显示结果卡片
            st.rerun()
