from flask import Flask, render_template, request
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

# Flaskアプリ
app = Flask(__name__)

# データ読み込み
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

#運動量に応じたBPM
stretch = np.array([60])
work = np.array([120])
jog = np.array([145])
run = np.array([170])

# -------------------------
# トップページ
# -------------------------
#@app.route("/")
#def index():
#    return render_template("index.html", titles=title.tolist())


@app.route("/", methods=["GET"])
def index():
    """トップページ（入力フォームの表示）"""
    # 選択された値はGETリクエストでは必要ないので、シンプルにテンプレートを返す
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    
    # 1. request.form から、ムードと運動量の値を取得
    #    HTMLの hidden input の name属性 ("mood", "exercise") を使用
    selected_mood = request.form.get("mood")
    selected_exercise = request.form.get("exercise")
    
    # 2. スライダーの値を取得
    selected_time = request.form.get("time")

    # 3. データ処理（推薦ロジックの実行）
    # 例: printして確認
    print(f"ムード: {selected_mood}, 運動量: {selected_exercise}, 時間: {selected_time}で推薦を実行します。")
    
    # ここに、推薦アルゴリズムやデータベース検索のコードを記述します
    # KeyedVectorsを選択肢に応じて生成
    kv = KeyedVectors(vector_size=5)  # moodのベクトル次元数を使う
    kv.add_vectors(title.tolist(), object)  # 曲名をキーとして、moodをベクトルとして追加
    kv.fill_norms()

    results = []
    best_score = -1  # 初期値として最小スコアを設定
    best_track = ""
    
    total_select = dataset(selected_mood,selected_exercise)
    # 選択された特徴量を基に、最も類似した曲を探す
    for recommend_track, score in kv.most_similar(total_select, topn=30):
        results.append({"title": recommend_track, "score": score})
        if score > best_score:
            best_score = score
            best_track = recommend_track
    pd.DataFrame(results)
ここから
    #総再生時間を計算する
    #secondsとresultsのタイトルが一致するものの秒数を取り出す
if self:
    final = np.array([seconds[i, 1] for i in range(len(seconds)) if seconds[i, 0] in [results[j]["title"] for j in range(len(results))]])
    t = 0 #総再生時間
    count = 0 #プレイリストの楽曲数
    for i in range(len(final)):
        t += final[i]
        count += 1
        if(self<=(t/60)):
            break
    st.write("再生時間は")
    times = get_h_m_s(t)
    #表示の仕方を変更させる必要あり
    st.write(times)
    st.dataframe(pd.DataFrame(results[i]["title"] for i in range(count)))

    recommended_songs = ["おすすめ曲 A", "おすすめ曲 B", "おすすめ曲 C"] 
    
    # 4. 結果テンプレートをレンダリングしてユーザーに返す
    return render_template(
        "result.html", 
        songs=recommended_songs
    )

#スコア作成
def dataset(mood, excercise):
    #選択されたムードと運動量を合体して、スコアを作成
    total_select = np.concatenate([mood, excercise]).T
    return total_select

#時間計算
def get_h_m_s(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return int(h),":",int(m) , ":", int(s)

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
