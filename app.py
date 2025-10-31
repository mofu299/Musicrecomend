from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import urllib.parse
from gensim.models import KeyedVectors

# Flaskアプリ
app = Flask(__name__)

# データ読み込み
title = np.load("data/name.npy", allow_pickle=True)  # 曲名
bpm = np.load("data/bpm.npy")  # BPM
valence = np.load("data/valence.npy")  # 楽曲の感情的なポジティブさ（0から1の範囲）
energy = np.load("data/energy.npy")  # 曲のエネルギー、活発さ（0から1の範囲）
danceability = np.load("data/danceability.npy")  # 踊りやすさ、リズムの強さ（0から1の範囲）
loudness = np.load("data/loudness.npy")  # 曲の音量レベル（デシベル単位）
object = np.array([valence, energy, danceability, loudness, bpm]).T  # 5つをまとめた2次元配列（曲ごとの特徴ベクトル）
seconds = np.load("data/seconds.npy", allow_pickle=True)  # タイトルと楽曲の再生時間(秒)とアーティスト名と時間(分、秒)

# 各感情の特徴ベクトル（ターゲット特徴量）
mood_targets = {
    "happy": np.array([1, 1, 0.8, -5]),  # ポジティブ、活発、踊りやすい、強め
    "sad": np.array([0, 0.1, 0.2, -10]),  # ネガティブ、落ち着き、低め、弱め
    "relaxed": np.array([0, 0.4, 0, -20]),  # 中間、落ち着き、中間、中間
    "energetic": np.array([1, 1, 1, -2.5])  # ポジティブ、活発、踊りやすい、強め
}
# 運動量に応じたBPM
excersise_targets = {
    "ウォーキング": np.array([120]),
    "ジョギング": np.array([145]),
    "ランニング": np.array([170])
}

# 参照用のマップ
title = title.astype(str)
title_to_idx = {t: i for i, t in enumerate(title)}
secs_map = {str(row[0]): float(row[1]) for row in seconds}

# -------------------------
# トップページ
# -------------------------
@app.route("/", methods=["GET"])
def index():
    """トップページ（入力フォームの表示）"""
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    selected_mood = request.form.get("mood", "").strip()
    selected_exercise = request.form.get("exercise", "").strip()
    selected_time_min = request.form.get("time", "0").strip()

    print(f"ムード: {selected_mood}, 運動量: {selected_exercise}, 時間: {selected_time_min}")

    # 入力チェック
    if not selected_mood or not selected_exercise:
        return jsonify({"error": "ムードと運動量を選択してください。"})

    try:
        target_minutes = max(0, int(float(selected_time_min)))
    except ValueError:
        return jsonify({"error": "時間の値が不正です。"})

    indices = np.arange(len(title))
    # KeyedVectors
    kv = build_kv(indices)

    # ターゲットベクトル
    target_vec = make_target_vector(selected_mood, selected_exercise)
    if target_vec is None:
        return jsonify({"error": "入力値が不正です。"})

    # 類似上位を取得（とりあえず多めにとって後段でBPM/時間で絞る）
    topn = min(200, len(indices)) if len(indices) > 0 else 0
    if topn == 0:
        return jsonify({"error": "該当曲がありません。"})

    sim_list = kv.most_similar(target_vec, topn=topn)  # [(title, score), ...]

    target_bpm = float(excersise_targets[selected_exercise])

    # ---- danceabilityターゲットを設定 ----
    mood_dance_target = {
        "sad": 0.2,
        "relaxed": 0.4,
        "happy": 0.8,
        "energetic": 1.0
    }.get(selected_mood, 0.5)

    picked = []
    total_sec = 0.0

    for rec_title, score in sim_list:
        idx = title_to_idx.get(rec_title)
        if idx is None:
            continue
        tr_bpm = float(bpm[idx]) if idx < len(bpm) else 0.0
        if not bpm_is_ok(tr_bpm, target_bpm, tol=0.1):
            continue  # 目標BPM

        dur = secs_map.get(rec_title, 0.0)
        if dur <= 0:
            continue

        d = float(danceability[idx])
        d_diff = abs(d - mood_dance_target)

        # danceabilityの近さスコア（近いほど高評価）
        dance_score = 1.0 - d_diff  # 0〜1の範囲

        # 総合スコア：KeyedVectorsの類似度＋danceability補正
        combined_score = score * 0.7 + dance_score * 0.3

        # Spotify検索URL作成
        artist_name = seconds[idx][2] if idx < len(seconds) else ""
        query = rec_title if not artist_name else f"{rec_title} {artist_name}"
        sp_search_url = "https://open.spotify.com/search/" + urllib.parse.quote(query)


        picked.append({
            "title": rec_title,
            "bpm": int(round(tr_bpm)),
            "valence": float(valence[idx]),
            "energy": float(energy[idx]),
            "danceability": float(danceability[idx]),
            "score": float(score),
            "dance_score": dance_score,
            "combined_score": combined_score,
            "duration": int(dur),
            "hh_mm": seconds[idx][3] if idx < len(seconds) else "",
            "artist": artist_name,
            "spotify_search": sp_search_url
        })
        total_sec += dur
        if total_sec >= target_minutes * 60:
            break

    if not picked:
        return jsonify({"error": "条件に合う曲が見つかりませんでした。検索条件(BPM許容やムード)を少し広げてください。"})

    # 見やすい並びに整形（score降順）
    picked = sorted(picked, key=lambda x: x["combined_score"], reverse=True)
    np.random.shuffle(picked)  # ランダムにシャッフル

    # 合計時間
    total_hms = hms(total_sec)

    return jsonify({
        "error": None,
        "input_mood": selected_mood,
        "input_exercise": selected_exercise,
        "input_time": target_minutes,
        "total_time": total_hms,
        "recommended": picked
    })

# スコア作成
def dataset(mood, excercise):
    # 選択されたムードと運動量を合体して、スコアを作成
    total_select = np.concatenate([mood, excercise]).T
    return total_select

# 時間計算
def hms(sec: float):
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# フィルタリング後のKeyedVectors作成
def build_kv(indices=None):
    kv = KeyedVectors(vector_size=5)
    if indices is None:
        kv.add_vectors(title.tolist(), object)
    else:
        kv.add_vectors(title[indices].tolist(), object[indices])
    kv.fill_norms()
    return kv

# 選択されたムードと運動量からターゲットベクトルを作成
def make_target_vector(selected_mood: str, selected_exercise: str):
    print(f"選択されたムード: {selected_mood}, 運動量: {selected_exercise}")
    if selected_mood not in mood_targets or selected_exercise not in excersise_targets:
        return None
    mood_vec = mood_targets[selected_mood]                # (4,)
    bpm_target = np.array([float(excersise_targets[selected_exercise])])  # (1,)
    total_vec = np.concatenate([mood_vec, bpm_target])    # (5,)
    print(f"ターゲットベクトル: {total_vec}")
    return total_vec

# BPMフィルタリング
# BPMが目標BPMに十分近いか判定。
# tol=0.08 は ±8% の許容。
def bpm_is_ok(track_bpm: float, target_bpm: float, tol=0.3):
    if track_bpm <= 0:
        return False
    close_direct = abs(track_bpm - target_bpm) <= target_bpm * tol
    return close_direct

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
