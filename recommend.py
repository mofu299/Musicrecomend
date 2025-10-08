import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# ── 読み込み ───────────────────────────
#bpmだけまだ前段階のデータ
bpm = np.load("data/combined_vector.npy", allow_pickle=True) 
title = np.load("data/name.npy", allow_pickle=True)

# ファイル名と特徴量の二次元配列
valence = np.load("data/valence.npy")  # 楽曲の感情的なポジティブさ（0から1の範囲）
energy = np.load("data/energy.npy")  # 曲のエネルギー、活発さ（0から1の範囲）
danceability = np.load("data/danceability.npy")  # 踊りやすさ、リズムの強さ（0から1の範囲）
loudness = np.load("data/loudness.npy")  # 曲の音量レベル（デシベル単位）
mood = np.array([valence, energy, danceability,loudness]).T  # 3つをまとめた2次元配列（曲ごとの特徴ベクトル）

# 各感情の特徴ベクトル（ターゲット特徴量）
happy_target = np.array([1, 1, 0.8, -5])  # ポジティブ、活発、踊りやすい、強め
sad_target = np.array([0, 0, 0.2, 0.-10])  # ネガティブ、落ち着き、低め、弱め
relaxed_target = np.array([0, 0.4, 0, -20])  # 中間、落ち着き、中間、中間
energetic_target = np.array([1, 1, 1, -5])  # ポジティブ、活発、踊りやすい、強め


# 特徴量の選択肢
feature_options = {
    "happy": happy_target,
    "sad": sad_target,
    "relaxed": relaxed_target,
    "energetic": energetic_target
}

# 特徴量の選択
selected_feature = st.selectbox("特徴量を選んでください", list(feature_options.keys()))
# 条件に応じてスコアを変更
target_scores = feature_options[selected_feature]

# KeyedVectorsを選択肢に応じて生成
kv = KeyedVectors(vector_size=len(target_scores))  # moodのベクトル次元数を使う
kv.add_vectors(title.tolist(), mood)  # 曲名をキーとして、moodをベクトルとして追加
kv.fill_norms()

st.write("楽曲レコメンドアプリ")

# ここを修正: 検索リストを「曲のタイトル」に変更
st.markdown("#テーマに対して似ている曲を表示する")

if selected_feature:
    st.markdown(f"### {selected_feature} に関連する曲")
    results = []
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.most_similar(target_scores, topn=30):
        results.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    
    st.dataframe(pd.DataFrame(results))
    url = f"https://www.google.com/search?q={best_track}+楽曲"
    st.markdown(f"[ {best_track}をGoogleで検索]({url})")

# 「BPM」に変更
run_options = {
    "ストレッチ" : 60,
    "ウォーキング": 120,
    "ジョギング" : 145,
    "ランニング": 170,
}
# 運動量の選択
selected_run = st.selectbox("特徴量を選んでください", list(run_options.keys()))
# 条件に応じてスコアを変更
run_scores = run_options[selected_run]
st.markdown("#テーマに対して似ている曲を表示する")

if selected_run:
    st.markdown(f"### {selected_run} に関連する曲")
    results = []
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.most_similar(run_scores, topn=30):
        results.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    
    st.dataframe(pd.DataFrame(results))
    url = f"https://www.google.com/search?q={best_track}+楽曲"
    st.markdown(f"[ {best_track}をGoogleで検索]({url})")

