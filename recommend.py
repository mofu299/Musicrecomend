import streamlit as st
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# ── 読み込み ───────────────────────────
title = np.load("data/name.npy", allow_pickle=True) #曲名
bpm = np.load("data/bpm.npy") #BPM
valence = np.load("data/valence.npy")  # 楽曲の感情的なポジティブさ（0から1の範囲）
energy = np.load("data/energy.npy")  # 曲のエネルギー、活発さ（0から1の範囲）
danceability = np.load("data/danceability.npy")  # 踊りやすさ、リズムの強さ（0から1の範囲）
loudness = np.load("data/loudness.npy")  # 曲の音量レベル（デシベル単位）
object = np.array([valence, energy, danceability,loudness,bpm]).T  # 5つをまとめた2次元配列（曲ごとの特徴ベクトル）
seconds = np.load("data/time.npy", allow_pickle=True) #楽曲の再生時間(タイトルと楽曲の再生時間)

# 各感情の特徴ベクトル（ターゲット特徴量）
happy_target = np.array([1, 1, 0.8, -5])  # ポジティブ、活発、踊りやすい、強め
sad_target = np.array([0, 0, 0.2, -10])  # ネガティブ、落ち着き、低め、弱め
relaxed_target = np.array([0, 0.4, 0, -20])  # 中間、落ち着き、中間、中間
energetic_target = np.array([1, 1, 1, -2.5])  # ポジティブ、活発、踊りやすい、強め


# ムードの選択肢
feature_options = {
    "happy": happy_target,
    "sad": sad_target,
    "relaxed": relaxed_target,
    "energetic": energetic_target
}

# ムードの選択
selected_feature = st.selectbox("ムードを選んでください", list(feature_options.keys()))
# 条件に応じてスコアを変更
target_scores = feature_options[selected_feature]

#運動量に応じたBPM
stretch = np.array([60])
work = np.array([120])
jog = np.array([145])
run = np.array([170])

#運動量の選択肢
run_options = {
    "ストレッチ" : stretch,
    "ウォーキング": work,
    "ジョギング" : jog,
    "ランニング": run
}

# 運動量の選択
selected_run = st.selectbox("運動量を選んでください", run_options.keys())
# 条件に応じてスコアを変更
run_scores = run_options[selected_run]

#選択されたムードと運動量を合体して、スコアを作成
total_select = np.concatenate([target_scores, run_scores]).T

print(len(title))
print(object.size)

# KeyedVectorsを選択肢に応じて生成
kv = KeyedVectors(vector_size=5)  # moodのベクトル次元数を使う
kv.add_vectors(title.tolist(), object)  # 曲名をキーとして、moodをベクトルとして追加
kv.fill_norms()

#時間計算
def get_h_m_s(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return h, ":", m, ":", s

st.write("楽曲レコメンドアプリ")

# ここを修正: 検索リストを「曲のタイトル」に変更
#st.markdown("#テーマに対して似ている曲を表示する")
results = []
if selected_feature:
    #st.markdown(f"### {selected_feature} に関連する曲")
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.most_similar(total_select, topn=30):
        results.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    
    st.dataframe(pd.DataFrame(results))
    pd.DataFrame(results)

    #総再生時間を計算する
    #secondsとresultsのタイトルが一致するものの秒数を取り出す
    final = np.array([seconds[i, 1] for i in range(len(seconds)) if seconds[i, 0] in [results[j]["title"] for j in range(len(results))]])
    t = 0 #総再生時間
    for i in range(len(final)):
        t += final[i]
    st.write("再生時間は")
    times = get_h_m_s(t)
    st.write(times)



