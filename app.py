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

# -------------------------
# トップページ
# -------------------------
#@app.route("/")
#def index():
#    return render_template("index.html", titles=title.tolist())


@app.route("/", methods=["GET", "POST"])
def index():
    selected = None
    if request.method == "POST":
        selected = request.form.get("exercise")  # 選択された運動量
    return render_template("index.html", selected=selected)

@app.route("/", methods=["GET", "POST"])
def index0():
    volume = None
    if request.method == "POST":
        volume = request.form.get("volume")  # スライダーの値
    return render_template("index.html", volume=volume)

# -------------------------
# 推薦ページ
# -------------------------
#@app.route("/recommend", methods=["POST"])
#def recommend():
    input_song = request.form["song"]  # フォームから曲名取得

    # 入力曲のインデックスを取得
    try:
        idx = np.where(title == input_song)[0][0]
    except IndexError:
        return render_template("result.html", input_song=input_song, recommended=[], error="曲が見つかりません。")

    # 類似度計算（コサイン類似度）
    input_vector = features[idx].reshape(1, -1)
    similarity = cosine_similarity(features, input_vector).flatten()

    # 自分自身は除外
    similarity[idx] = -1

    # 上位10曲を取得
    top_indices = similarity.argsort()[::-1][:10]
    recommended = [{"title": title[i], "score": round(similarity[i], 4)} for i in top_indices]

    return render_template("result.html", input_song=input_song, recommended=recommended, error=None)

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
