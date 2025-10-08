# MusicRecommendapp
プロジェクトで作成した推薦アプリです。

pip install gensim
pip install streamlit
streamlit run recommend.py
をターミナル上で実行

もしmodulederrorが出たら
pip install "numpy<2"

もしくは
pip uninstall -y numpy
pip install numpy==1.26.4