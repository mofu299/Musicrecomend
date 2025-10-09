import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# ── 読み込み ───────────────────────────
#bpmだけまだ前段階のデータ
bpm = np.load("data/bpm_vector.npy", allow_pickle=True) 
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
energetic_target = np.array([1, 1, 1, -2.5])  # ポジティブ、活発、踊りやすい、強め


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
results = []
if selected_feature:
    st.markdown(f"### {selected_feature} に関連する曲")
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.most_similar(target_scores, topn=30):
        results.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    
    st.dataframe(pd.DataFrame(results))

#resultsのスコアとBPMを組み合わせて、運動量に応じた曲を推薦
stretch = np.array([1, 60])
work = np.array([1, 120])
jog = np.array([1, 145])
run = np.array([1, 170])

# 「BPM」に変更
run_options = {
    "ストレッチ" : stretch,
    "ウォーキング": work,
    "ジョギング" : jog,
    "ランニング": run
}
# 運動量の選択
selected_run = st.selectbox("特徴量を選んでください", run_options.keys())
# 条件に応じてスコアを変更
run_scores = run_options[selected_run]
st.markdown("#テーマに対して似ている曲を表示する")

#resultのスコアを取り出す
score_results = np.array([results[i]["score"] for i in range(len(results))])
#bpmとresultsのタイトルが一致するもののBPMを取り出す
keep = np.array([bpm[i, 1] for i in range(len(bpm)) if bpm[i, 0] in [results[j]["title"] for j in range(len(results))]])

recommend_score = np.array([keep, score_results]).T
keep_titles = list(results[i]["title"] for i in range(len(results)))

kv = KeyedVectors(vector_size=len(run_scores))  # 今回は BPM のみなので 1次元
kv.add_vectors(list(keep_titles), recommend_score)  # numpy 配列に変換して追加
kv.fill_norms()

result2 = []
if selected_run:
    st.markdown(f"### {selected_run} に関連する曲")
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.similar_by_vector(run_scores, topn=30):
        result2.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    
    st.dataframe(pd.DataFrame(result2))
    url = f"https://www.google.com/search?q={best_track}+楽曲"
    st.markdown(f"[ {best_track}をGoogleで検索]({url})")

