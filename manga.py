import streamlit as st
import numpy as np
import pandas as pd

from gensim.models import KeyedVectors
import numpy as np

# ── 読み込み ───────────────────────────
vectors = np.load("my_vectors.npy")                    # shape = (V, D)
vocab   = np.load("my_vocab.npy", allow_pickle=True)   # shape = (V,)

# ── KeyedVectors を組み立てる ─────────
kv = KeyedVectors(vector_size=vectors.shape[1])
kv.add_vectors(vocab.tolist(), vectors)      # gensim 4.x 以降の公式 API :contentReference[oaicite:0]{index=0}
kv.fill_norms()                              # 類似度計算を高速化（省略可）


st.write("マンガレコメンドアプリ")

manga_titles = vocab.tolist()

st.markdown("## 1冊のマンガに対して似ているマンガを表示する")
selected_manga = st.selectbox("マンガを選んでください", manga_titles)

if selected_manga:
    st.markdown(f"### {selected_manga} に似ているマンガ")
    results = []
    best_score = 0;
    best_manga = " "
    for recommend_manga, score in kv.most_similar(selected_manga, topn=30):
        results.append({"title": recommend_manga, "score": score})
        if( score > best_score ):
            best_score = score
            best_manga = recommend_manga
    st.dataframe(pd.DataFrame(results))
    url = f"https://www.google.com/search?q={best_manga}+漫画"
    st.markdown(f"[ {best_manga}をGoogleで検索]({url})")


# 本来なら下記のような簡単な読み込みで対抗可能。ただし、gensimバージョンが異なるとエラー出る
# model = gensim.models.word2vec.Word2Vec.load("data/manga_item2vec.model")

st.markdown("## 複数の漫画を選んでおすすめの漫画を表示する")

selected_manga = st.multiselect("漫画を複数選んでください", manga_titles)

if selected_manga:
    try:
        selected_vectors = [kv[m] for m in selected_manga if m in kv]
        user_vector = np.mean(selected_vectors, axis=0)

        st.markdown(f"### {selected_manga} に似ているマンガ")
        results = []
        best_score = 0;
        best_manga = " "
        for recommend_manga, score in kv.similar_by_vector(user_vector, topn=30):
            if recommend_manga not in selected_manga:
                results.append({"title": recommend_manga, "score": score})
                if( score > best_score ):
                    best_score = score
                    best_manga = recommend_manga
        st.dataframe(pd.DataFrame(results))

        url = f"https://www.google.com/search?q={best_manga}+漫画"
        st.markdown(f"[ {best_manga}をGoogleで検索]({url})")
    except KeyError:
        st.error("選択したマンガの一部がベクトルに存在しません。")

