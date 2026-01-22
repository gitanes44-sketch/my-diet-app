import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. ページ設定
st.set_page_config(page_title="My Diet Pro", page_icon="🥗", layout="centered")

# カスタムCSSでiPhoneでの見栄えをさらに良くする
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🥗 Body Log Pro")

# 2. スプレッドシート接続
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0s")

# データが空の場合の処理
if df.empty:
    df = pd.DataFrame(columns=["date", "content", "type", "calories"])

# 3. 今日の集計ロジック
today = pd.Timestamp.now().strftime("%Y-%m-%d")
today_df = df[df['date'] == today]
total_in = today_df[today_df['type'] == "摂取"]['calories'].sum()
total_out = today_df[today_df['type'] == "消費"]['calories'].sum()
goal = 2000 # 目標カロリー（仮）

# 4. ダッシュボード（サマリーカード）
st.subheader("Today's Summary")
c1, c2, c3 = st.columns(3)
c1.metric("摂取", f"{total_in} kcal")
c2.metric("消費", f"{total_out} kcal")
c3.metric("残り", f"{goal - total_in + total_out} kcal")

# 進捗バー
progress = min(total_in / goal, 1.0)
st.write(f"目標摂取量まで あと {max(goal - total_in, 0)} kcal")
st.progress(progress)

# 5. メインコンテンツ（タブ分け）
tab1, tab2, tab3 = st.tabs(["＋ 記録", "📈 分析", "📜 履歴"])

with tab1:
    with st.form(key="input_form", clear_on_submit=True):
        st.markdown("### 記録を追加")
        col_a, col_b = st.columns(2)
        with col_a:
            date = st.date_input("日付", value=pd.Timestamp.now())
        with col_b:
            category = st.radio("種別", ["摂取", "消費"], horizontal=True)
        
        content = st.text_input("内容 (例: 昼食, ジョギング)")
        calories = st.number_input("カロリー", step=10)
        
        if st.form_submit_button("データを保存"):
            new_row = pd.DataFrame([{"date": str(date), "content": content, "type": category, "calories": calories}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("保存完了！")
            st.rerun()

with tab2:
    st.subheader("カロリー推移")
    if not df.empty:
        # 日ごとの集計
        daily_df = df.groupby(['date', 'type'])['calories'].sum().reset_index()
        fig = px.bar(daily_df, x='date', y='calories', color='type', barmode='group',
                     color_discrete_map={'摂取': '#FF4B4B', '消費': '#1C83E1'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("データがたまるとここにグラフが表示されます")

with tab3:
    st.subheader("過去の全データ")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    
    if st.button("最新の状態に更新"):
        st.rerun()
