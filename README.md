# MusicRecommendapp
プロジェクトで作成した推薦アプリです。
StreamLitとFlask版があります。

<StreamLit版>
pip install gensim
pip install streamlit
streamlit run recommend.py
をターミナル上で実行

もしmodulederrorが出たら
pip install "numpy<2"

もしくは
pip uninstall -y numpy
pip install numpy==1.26.4

<Flask版>
初めにstreamlitが起動するので^cをしてから、「pyhton3 app.py」にすると表示できます。
