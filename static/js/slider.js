const slider = document.getElementById("time"); 
const output = document.getElementById("timeValue"); 

function updateSliderColor() {
    const value = slider.value;
    const max = slider.max || 60; // max="60"なので、60にしておく
    const percent = (value / max) * 100;

    //スライダー要素のスタイルにCSS変数を設定する
    slider.style.setProperty('--track-progress', `${percent}%`);
}

// 初期表示
updateSliderColor();
output.textContent = slider.value;

// スライダー操作時に更新
slider.addEventListener("input", () => {
    output.textContent = slider.value;
    updateSliderColor();
});