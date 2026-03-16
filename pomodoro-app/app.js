const durations = {
  focus: 25 * 60,
  shortBreak: 5 * 60,
  longBreak: 15 * 60,
};

const modeNames = {
  focus: "Focus",
  shortBreak: "Short Break",
  longBreak: "Long Break",
};

const timeDisplay = document.getElementById("timeDisplay");
const modeLabel = document.getElementById("modeLabel");
const startPauseBtn = document.getElementById("startPauseBtn");
const resetBtn = document.getElementById("resetBtn");
const modeButtons = document.querySelectorAll(".mode-btn");
const progressCircle = document.querySelector(".progress-ring__indicator");

const radius = Number(progressCircle.getAttribute("r"));
const circumference = 2 * Math.PI * radius;

progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;

let currentMode = "focus";
let totalSeconds = durations[currentMode];
let remainingSeconds = totalSeconds;
let timerId = null;

function formatTime(seconds) {
  const min = String(Math.floor(seconds / 60)).padStart(2, "0");
  const sec = String(seconds % 60).padStart(2, "0");
  return `${min}:${sec}`;
}

function updateRing() {
  const progress = remainingSeconds / totalSeconds;
  const offset = circumference * (1 - progress);
  progressCircle.style.strokeDashoffset = offset;
}

function render() {
  timeDisplay.textContent = formatTime(remainingSeconds);
  modeLabel.textContent = modeNames[currentMode];
  updateRing();
}

function stopTimer() {
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
  startPauseBtn.textContent = "Start";
}

function startTimer() {
  if (timerId) return;

  startPauseBtn.textContent = "Pause";
  timerId = setInterval(() => {
    if (remainingSeconds <= 0) {
      stopTimer();
      return;
    }

    remainingSeconds -= 1;
    render();

    if (remainingSeconds === 0) {
      stopTimer();
    }
  }, 1000);
}

function setMode(mode) {
  currentMode = mode;
  totalSeconds = durations[mode];
  remainingSeconds = totalSeconds;
  stopTimer();

  modeButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });

  render();
}

startPauseBtn.addEventListener("click", () => {
  if (timerId) {
    stopTimer();
  } else {
    startTimer();
  }
});

resetBtn.addEventListener("click", () => {
  remainingSeconds = totalSeconds;
  stopTimer();
  render();
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

render();
