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
const DISABLED_CLASS = 'disabled-link'; 

// フォームの入力状態をチェックする関数
//二つのボタンが選択されているかどうか
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
playlistLink.addEventListener("click", (e) => {
    // 1. 無効状態なら、リンク移動をキャンセルして処理を終了
    if (playlistLink.classList.contains(DISABLED_CLASS)) {
        e.preventDefault(); 
        return;
    }

    // 2. 有効状態なら、リンク移動をキャンセルし、フォームを送信
    e.preventDefault(); 
    exerciseForm.submit(); // フォームをサーバーに送信
});

// 初期状態のチェック (ページロード時)
checkFormValidity();
