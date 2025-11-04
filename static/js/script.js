/*ムード選択ボタン*/
const moodButtons = document.querySelectorAll(".group1 button");
const moodInput = document.getElementById("moodInput");

moodButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        // 選択中ボタンのスタイルを切替
        moodButtons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");

        // hidden input に値をセット
        moodInput.value = btn.textContent;
        checkFormValidity();
    });
});

/*運動量ボタン*/
const exerciseButtons = document.querySelectorAll(".group2 button");
const exerciseInput = document.getElementById("exerciseInput");

exerciseButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        exerciseButtons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");

        exerciseInput.value = btn.textContent;
        checkFormValidity();
    });
});

/*推薦ボタン*/
const playlistLink = document.getElementById("playlistLink");
const exerciseForm = document.getElementById("mainForm"); 
const resultContainer = document.getElementById("result");
const DISABLED_CLASS = 'disabled-link'; 

// フォームの入力状態をチェックする関数
// 二つのボタンが選択されているかどうか
function checkFormValidity() {
    const moodSelected = moodInput.value;
    const exerciseSelected = exerciseInput.value;

    if (moodSelected !== "" && exerciseSelected !== "") {
        // 両方選択されている場合、有効化
        playlistLink.classList.remove(DISABLED_CLASS);
        return true; 
    } else {
        // 選択が不十分な場合、無効化
        playlistLink.classList.add(DISABLED_CLASS);
        return false;
    }
}

/*シャッフルボタン*/
const shuffleBtn = document.getElementById("shuffleButton");
shuffleBtn.addEventListener("click", shufflePlaylist);

/*音楽リスト保存用*/
let basePlaylist = [];  // サーバから取得したリスト
let metaData = {};      // メタ情報

/*プレイリスト表示*/
function renderPlaylist(data) {
  if (!data.recommended || data.recommended.length === 0) {
    resultContainer.innerHTML = "<p>おすすめ曲が見つかりませんでした。</p>";
    shuffleBtn.style.display = "none";
    return;
  }

  const songsHTML = data.recommended
    .map(
      (song, index) => `
        <div class="track">
          <span class="track-number">${index + 1}</span>
          <div class="track-title">
            <span>${song.title}</span>
            <span class="track-artist">${song.artist}</span>
          </div>
          <span class="track-time">${song.hh_mm}</span>
          <span class="track-bpm">${song.bpm} BPM</span>
          <a class="open-link" href="${song.spotify_search}" target="_blank" rel="noopener">Spotifyで探す</a>
        </div>
      `
    )
    .join("");

  resultContainer.innerHTML = `
    <h2>生成されたプレイリスト</h2>
    <p>合計再生時間: ${data.total_time}</p>
    <div class="tracks-list">${songsHTML}</div>
  `;

  shuffleBtn.style.display = "inline-block";
}

/*プレイリストシャッフル*/
function shufflePlaylist() {
  if (!basePlaylist.length) return;

  const shuffled = [...basePlaylist];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  renderPlaylist({
    recommended: shuffled,
    total_time: metaData.total_time
  });
}

/*プレイリスト生成*/
playlistLink.addEventListener("click", async (e) => {
  e.preventDefault();

  if (playlistLink.classList.contains(DISABLED_CLASS)) {
    return;
  }

  const formData = new FormData(exerciseForm);

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`サーバエラー: ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      resultContainer.innerHTML = `<p style="color:red;">${data.error}</p>`;
      shuffleBtn.style.display = "none";
      return;
    }
    // 結果を保持
    basePlaylist = data.recommended;
    metaData = { total_time: data.total_time };
    // 描画
    renderPlaylist(data);
  } catch (err) {
    console.error("Fetch失敗:", err);
    resultContainer.innerHTML = `<p style="color:red;">通信エラーが発生しました。</p>`;
    shuffleBtn.style.display = "none";
  }
});
