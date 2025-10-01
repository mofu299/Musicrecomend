import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# ── 読み込み ───────────────────────────
# ...既存の読み込み...
bpm = np.load("data/combined_vector.npy") 
title = np.load("data/name.npy", allow_pickle=True)
mood = np.load("data/mood_vector.npy")

# 特徴量の選択肢
feature_options = {
    "bpmのみ": bpm,
    "moodのみ": mood,
    "bpm + mood": np.concatenate([bpm, mood], axis=1)
}

# 特徴量の選択
selected_feature = st.selectbox("特徴量を選んでください", list(feature_options.keys()))
selected_vectors = feature_options[selected_feature]

# KeyedVectorsを選択肢に応じて生成
kv = KeyedVectors(vector_size=selected_vectors.shape[1])
kv.add_vectors(title.tolist(), selected_vectors)
kv.fill_norms()

st.write("楽曲レコメンドアプリ")

# ここを修正: 検索リストを「曲のタイトル」に変更
track_titles = title.tolist()
mood = ["元気", "落ち着き", "切ない", "明るい", "暗い"]

st.markdown("## 1曲に対して似ている曲を表示する")
selected_track = st.selectbox("曲を選んでください", track_titles)

if selected_track:
    st.markdown(f"### {selected_track} に似ている曲")
    results = []
    best_score = 0;
    best_track = ""
    for recommend_track, score in kv.most_similar(selected_track, topn=30):
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