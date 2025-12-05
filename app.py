import random
import json
import os
import time
import streamlit as st

# --- 1. 核心配置与数据 ---

st.set_page_config(page_title="IFCCI Santa & Troll", layout="centered")

PARTICIPANTS = [
    "Dato’ Kingston", "Datin Paris", "Wena", "Zi Qing", "Zhen Hao", 
    "Jeffrey", "Klain", "Daniel Ang", "Kingston Neo", "Kimberly", 
    "Hanshon", "Cassey", "Bryan", "Melissa"
]

STORAGE_FILE = 'draw_results.json'

# --- 2. 状态管理函数 ---

def load_results():
    """加载数据，确保安全"""
    results = {}
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
    except Exception:
        results = {}
    
    # 补全所有人
    full_map = {p: {"santa": None, "troll": None} for p in PARTICIPANTS}
    full_map.update(results)
    return full_map

def save_results(results):
    """保存数据"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"保存失败: {e}")

# 初始化 Session State
if 'RESULT_MAP' not in st.session_state:
    st.session_state.RESULT_MAP = load_results()

# 初始化“当前展示结果的人”，防止刷新后消失
if 'show_result_for' not in st.session_state:
    st.session_state.show_result_for = None

RESULT_MAP = st.session_state.RESULT_MAP

# --- 3. 抽签算法与特效 ---

def get_candidate_list(operator_name, draw_type):
    """获取合法的候选人名单"""
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

def run_wheel_effect(placeholder, candidates, duration=1.5):
    """
    运行滚动抽奖特效
    placeholder: Streamlit 的占位符，用于更新文字
    candidates: 候选人列表，用于随机跳动
    duration: 动画持续时间（秒）
    """
    if not candidates:
        return
        
    end_time = time.time() + duration
    # 模拟转盘速度：开始快，后面也不变（为了简单流畅），如果想变慢可以加 sleep 递增
    delay = 0.08 
    
    while time.time() < end_time:
        # 随机显示一个名字
        temp_name = random.choice(candidates)
        # 使用 HTML 渲染大号字体，模拟跳动效果
        placeholder.markdown(
            f"<div style='font-size:30px; font-weight:bold; color:#FF9900; text-align:center;'>🎰 {temp_name}</div>", 
            unsafe_allow_html=True
        )
        time.sleep(delay)
    
    placeholder.empty() # 动画结束后清空

# --- 4. CSS 美化 ---
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #D42426; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #165B33; text-align: center; margin-bottom: 20px; }
    .result-card {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, #ffffff 0%, #f0fff4 100%);
        border: 3px solid #165B33;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        margin-bottom: 20px;
        animation: fadeIn 1s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .role-title { font-size: 20px; color: #555; margin-bottom: 5px; font-weight: bold;}
    .name-display { font-size: 36px; font-weight: 900; color: #D42426; margin-bottom: 15px; text-shadow: 1px 1px 0px rgba(0,0,0,0.1); }
    .divider { margin: 20px 0; border-top: 1px dashed #ccc; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎄 IFCCI Santa & Troll 😈</div>', unsafe_allow_html=True)

# ==========================================
#  逻辑分支：展示结果页 vs 抽签选择页
# ==========================================

# 🟢 分支 A: 如果有正在展示的结果，锁定画面显示结果卡片
if st.session_state.show_result_for:
    winner = st.session_state.show_result_for
    data = RESULT_MAP.get(winner, {})
    
    st.markdown(f"<h3 style='text-align:center'>👋 {winner}，你的抽签结果</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="result-card">
    <div style="font-size:50px;">🎅</div>
    <div class="role-title">恭喜你，成为 TA 的 Santa</div>
    <div class="name-display">{data.get('santa', '???')}</div>
    <div style="color:#666; font-size:14px;">(要送 TA 想要的礼物哦!)</div>
    <div class="divider"></div>
    <div style="font-size:50px;">😈</div>
    <div class="role-title">恭喜你，成为 TA 的 Troll</div>
    <div class="name-display">{data.get('troll', '???')}</div>
    <div style="color:#666; font-size:14px;">(准备好恶搞 TA 吧!)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    # 这个按钮点击后，才会清除状态，回到主页
    if st.button("✅ 我记住了，下一位", type="primary", use_container_width=True):
        st.session_state.show_result_for = None # 清除状态
        st.rerun() # 刷新回到主页

# 🔵 分支 B: 正常抽签页面
else:
    # 计算进度
    uncompleted = [p for p in PARTICIPANTS if RESULT_MAP.get(p, {}).get('troll') is None]
    progress = len(PARTICIPANTS) - len(uncompleted)
    st.caption(f"当前进度: {progress} / {len(PARTICIPANTS)} 人已完成")
    st.progress(progress / len(PARTICIPANTS))
    
    st.markdown("---")
    st.subheader("请选择您的名字：")
    
    options = ["-- 点击选择 --"] + uncompleted
    selected_name = st.selectbox("Name", options=options, label_visibility="collapsed")
    
    if selected_name != "-- 点击选择 --":
        st.info(f"准备好了吗，{selected_name}？")
        
        if st.button("🎁 点击开始抽签 😈", type="primary", use_container_width=True):
            current_result = RESULT_MAP.get(selected_name, {})
            
            # --- 抽签逻辑 ---
            
            # 1. 抽 Santa
            if not current_result.get('santa'):
                # 获取候选人列表用于特效
                santa_candidates = get_candidate_list(selected_name, 'santa')
                if not santa_candidates:
                    st.error("Santa 候选人不足！")
                    st.stop()
                
                # 创建一个空容器用于播放动画
                anim_box = st.empty()
                st.info("🎅 正在抽取 Santa...")
                # 播放 1.5 秒动画
                run_wheel_effect(anim_box, santa_candidates, duration=1.5)
                
                # 真正的抽取
                s_res = random.choice(santa_candidates)
                current_result['santa'] = s_res
            
            # 2. 抽 Troll
            if not current_result.get('troll'):
                # 获取候选人列表用于特效
                # 注意：Troll 的候选人稍微复杂点，需要排除掉刚抽到的 Santa
                # 为了特效简单，我们先获取所有合法 Troll，虽然可能包含刚抽到的 Santa，但只是视觉特效无所谓
                # 只要最后真正的逻辑排除掉就行
                troll_candidates_visual = get_candidate_list(selected_name, 'troll')
                
                anim_box_2 = st.empty()
                st.info("😈 正在抽取 Troll...")
                run_wheel_effect(anim_box_2, troll_candidates_visual, duration=1.5)
                
                found_troll = None
                # 尝试多次以避开和 Santa 重复
                for _ in range(20):
                    # 获取真实的候选人池
                    real_candidates = get_candidate_list(selected_name, 'troll')
                    if not real_candidates: break
                    
                    t_res = random.choice(real_candidates)
                    if t_res != current_result['santa']:
                        found_troll = t_res
                        break
                
                if not found_troll:
                    st.error("Troll 候选人冲突！")
                    st.stop()
                current_result['troll'] = found_troll

            # 3. 保存并进入展示模式
            RESULT_MAP[selected_name] = current_result
            save_results(RESULT_MAP)
            
            # 关键：设置 Session State，锁定结果页
            st.session_state.show_result_for = selected_name
            st.rerun()
