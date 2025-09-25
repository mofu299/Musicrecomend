import streamlit as st
import numpy as np
import pandas as pd

from gensim.models import KeyedVectors
import numpy as np

# ── 読み込み ───────────────────────────
vectors = np.load("data/Benergy.npy")                    # shape = (V, D)
vocab   = np.load("data/name.npy", allow_pickle=True)   # shape = (V,)

# ── KeyedVectors を組み立てる ─────────
kv = KeyedVectors(vector_size=vectors.shape[1])
kv.add_vectors(vocab.tolist(), vectors)      # gensim 4.x 以降の公式 API :contentReference[oaicite:0]{index=0}
kv.fill_norms()                              # 類似度計算を高速化（省略可）


st.write("楽曲レコメンドアプリ")

music_titles = vocab.tolist()

st.markdown("## 似ている楽曲を表示する")
selected_music = st.selectbox("楽曲を選んでください", music_titles)

if selected_music:
    st.markdown(f"### {selected_music} に似ている楽曲")
    results = []
    best_score = 0;
    best_music = " "
    for recommend_music, score in kv.most_similar(selected_music, topn=30):
        results.append({"title": recommend_music, "score": score})
        if( score > best_score ):
            best_score = score
            best_music = recommend_music
    st.dataframe(pd.DataFrame(results))
    url = f"https://www.google.com/search?q={best_music}+楽曲"
    st.markdown(f"[ {best_music}をGoogleで検索]({url})")


# 本来なら下記のような簡単な読み込みで対抗可能。ただし、gensimバージョンが異なるとエラー出る
# model = gensim.models.word2vec.Word2Vec.load("data/manga_item2vec.model")

st.markdown("## 複数の楽曲を選んでおすすめの楽曲を表示する")

selected_music = st.multiselect("楽曲を複数選んでください", music_titles)

if selected_music:
    try:
        selected_vectors = [kv[m] for m in selected_music if m in kv]
        user_vector = np.mean(selected_vectors, axis=0)

        st.markdown(f"### {selected_music} に似ている楽曲")
        results = []
        best_score = 0;
        best_music = " "
        for recommend_music, score in kv.similar_by_vector(user_vector, topn=30):
            if recommend_music not in selected_music:
                results.append({"title": recommend_music, "score": score})
                if( score > best_score ):
                    best_score = score
                    best_music = recommend_music
        st.dataframe(pd.DataFrame(results))

        url = f"https://www.google.com/search?q={best_music}+楽曲"
        st.markdown(f"[ {best_music}をGoogleで検索]({url})")
    except KeyError:
        st.error("選択したマンガの一部がベクトルに存在しません。")

