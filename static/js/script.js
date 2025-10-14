const moodButtons = document.querySelectorAll(".group1 button");
const moodInput = document.getElementById("moodInput");

moodButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        // 選択中ボタンのスタイルを切替
        moodButtons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");

        // hidden input に値をセット
        moodInput.value = btn.textContent;
    });
});

const exerciseButtons = document.querySelectorAll(".group2 button");
const exerciseInput = document.getElementById("exerciseInput");

exerciseButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        exerciseButtons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");

        exerciseInput.value = btn.textContent;
    });
});

const slider = document.getElementById("volume");
const output = document.getElementById("volumeValue");

slider.addEventListener("input", () => {
    output.textContent = slider.value;
});