import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# ── 読み込み ───────────────────────────
bpm = np.load("data/combined_vector.npy", allow_pickle=True) 
title = np.load("data/name.npy", allow_pickle=True)

# ファイル名と特徴量の二次元配列
valence = np.load("data/valence.npy")  # 楽曲の感情的なポジティブさ（0から1の範囲）
energy = np.load("data/energy.npy")  # 曲のエネルギー、活発さ（0から1の範囲）
danceability = np.load("data/danceability.npy")  # 踊りやすさ、リズムの強さ（0から1の範囲）
mood = np.array([valence, energy, danceability]).T  # 3つをまとめた2次元配列（曲ごとの特徴ベクトル）

# 各感情の特徴ベクトル（ターゲット特徴量）
happy_target = np.array([1, 1, 0.8])  # ポジティブ、活発、踊りやすい
sad_target = np.array([0.2, 0.5, 0.2])  # ネガティブ、落ち着き、低め
relaxed_target = np.array([0, 0.7, 0.4])  # 中間、落ち着き、中間
energetic_target = np.array([1, 1, 1])  # ポジティブ、活発、踊りやすい

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

    
st.markdown("## 複数の曲を選んでおすすめの曲を表示する")
selected_tracks = st.multiselect("曲を複数選んでください", track_titles)

if selected_tracks:
    try:
        selected_vectors = [kv[t] for t in selected_tracks if t in kv]
        user_vector = np.mean(selected_vectors, axis=0)

        st.markdown(f"### {selected_tracks} に似ている曲")
        results = []
        best_score = 0
        best_track = ""
        for recommend_track, score in kv.similar_by_vector(user_vector, topn=30):
            if recommend_track not in selected_tracks:
                results.append({"title": recommend_track, "score": score})
                if score > best_score:
                    best_score = score
                    best_track = recommend_track
        st.dataframe(pd.DataFrame(results))

        url = f"https://www.google.com/search?q={best_track}+楽曲"
        st.markdown(f"[ {best_track}をGoogleで検索]({url})")
    except KeyError:
        st.error("選択した曲の一部がベクトルに存在しません。")