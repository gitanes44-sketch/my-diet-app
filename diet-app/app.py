import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. ページ設定
st.set_page_config(page_title="Body Log Pro", page_icon="🥗", layout="centered")

# 背景を白にするデザイン設定
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetric"] {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #EEEEEE;
    }
    .stButton button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. スプレッドシート接続
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0s")
if df.empty:
    df = pd.DataFrame(columns=["date", "content", "type", "calories"])

# 3. 目標設定（サイドバー）
st.sidebar.header("🎯 目標設定")
current_weight = st.sidebar.number_input("現在の体重 (kg)", value=70.0, step=0.1)
target_weight = st.sidebar.number_input("目標体重 (kg)", value=65.0, step=0.1)

# 目標までの総カロリー計算 (1kg = 7200kcal)
diff_weight = current_weight - target_weight
total_needed_kcal = diff_weight * 7200

# 実績の計算（全期間の 消費 - 摂取）
net_burned = df[df['type'] == "消費"]['calories'].sum() - df[df['type'] == "摂取"]['calories'].sum()
remaining_kcal = total_needed_kcal - net_burned

# 4. メイン画面：サマリー
st.title("🥗 Body Log Pro")

st.subheader("🏁 目標までの道のり")
col_target, col_remain = st.columns(2)
col_target.metric("目標までの総ノルマ", f"{int(total_needed_kcal)} kcal")
col_remain.metric("あと...", f"{int(remaining_kcal)} kcal", delta=f"{int(-net_burned)} kcal", delta_color="inverse")

# 進捗バー
progress_percent = min(max(net_burned / total_needed_kcal, 0.0), 1.0) if total_needed_kcal > 0 else 1.0
st.write(f"達成度: {int(progress_percent * 100)}%")
st.progress(progress_percent)

# 5. タブ構成
tab1, tab2, tab3 = st.tabs(["📝 記録", "📊 分析", "⚙️ 設定"])

with tab1:
    # クイック入力ボタン
    st.markdown("### ⚡️ クイック入力")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    quick_items = [
        ("☕️ コーヒー", 10, "摂取"),
        ("🍙 おにぎり", 200, "摂取"),
        ("🏃 ジョギング", 300, "消費")
    ]
    
    for i, (name, cal, c_type) in enumerate(quick_items):
        with [q_col1, q_col2, q_col3][i]:
            if st.button(f"{name}\n({cal}kcal)"):
                new_row = pd.DataFrame([{"date": pd.Timestamp.now().strftime("%Y-%m-%d"), "content": name, "type": c_type, "calories": cal}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success(f"{name} を追加しました！")
                st.rerun()

    st.divider()
    
    # 通常入力フォーム
    with st.expander("手動で詳しく入力"):
        with st.form(key="manual_form", clear_on_submit=True):
            d = st.date_input("日付", value=pd.Timestamp.now())
            t = st.radio("種別", ["摂取", "消費"], horizontal=True)
            c = st.text_input("内容")
            cal = st.number_input("カロリー", step=10)
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([{"date": str(d), "content": c, "type": t, "calories": cal}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.rerun()

with tab2:
    st.subheader("カロリー収支グラフ")
    if not df.empty:
        daily_df = df.groupby(['date', 'type'])['calories'].sum().reset_index()
        fig = px.bar(daily_df, x='date', y='calories', color='type', barmode='group',
                     color_discrete_map={'摂取': '#FF4B4B', '消費': '#1C83E1'})
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("データ管理")
    st.dataframe(df.sort_values("date", ascending=False))
    if st.button("全データを削除 (慎重に！)", type="primary"):
        conn.update(data=pd.DataFrame(columns=["date", "content", "type", "calories"]))
        st.rerun()
