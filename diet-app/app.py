import streamlit as st
import pandas as pd
import os

# ファイル名
DATA_FILE = "diet_data.csv"

# データを読み込む関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["日付", "内容", "種別", "カロリー"])

# データを保存する関数
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("🔥 24時間カロリーマネージャー")

# --- データの準備 ---
if 'logs' not in st.session_state:
    st.session_state.logs = load_data()

# --- サイドバー設定 ---
st.sidebar.header("基本設定")
weight = st.sidebar.number_input("体重 (kg)", value=60.0)
height = st.sidebar.number_input("身長 (cm)", value=165.0)
age = st.sidebar.number_input("年齢", value=25)
bmr = 10 * weight + 6.25 * height - 5 * age + 5 # 簡易的に男性用

# --- 入力エリア ---
col1, col2 = st.columns(2)
with col1:
    food_name = st.text_input("食べたもの")
    food_cal = st.number_input("カロリー", min_value=0, key="f_cal")
    if st.button("食事を記録"):
        new_data = pd.DataFrame([{"日付": pd.Timestamp.now().strftime("%Y-%m-%d"), "内容": food_name, "種別": "摂取", "カロリー": food_cal}])
        st.session_state.logs = pd.concat([st.session_state.logs, new_data], ignore_index=True)
        save_data(st.session_state.logs)

# --- 履歴の表示とリセット ---
st.subheader("今日の記録")
st.table(st.session_state.logs)

if st.button("データをすべて消去"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.session_state.logs = pd.DataFrame(columns=["日付", "内容", "種別", "カロリー"])
    st.rerun()