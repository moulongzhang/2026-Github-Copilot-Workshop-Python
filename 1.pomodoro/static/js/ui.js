
window.addEventListener('DOMContentLoaded', () => {
	const startBtn = document.getElementById('start-btn');
	const pauseBtn = document.getElementById('pause-btn');
	const resetBtn = document.getElementById('reset-btn');
	const timer = window.pomodoroTimer;

	function updateButtonState() {
		startBtn.disabled = timer.isRunning || timer.timeRemaining === 0;
		pauseBtn.disabled = !timer.isRunning;
	}

	startBtn.addEventListener('click', () => {
		try {
			timer.start();
			updateButtonState();
		} catch (e) {
			alert('タイマー開始時にエラーが発生しました');
		}
	});

	pauseBtn.addEventListener('click', () => {
		try {
			timer.pause();
			updateButtonState();
		} catch (e) {
			alert('タイマー停止時にエラーが発生しました');
		}
	});

	resetBtn.addEventListener('click', () => {
		try {
			timer.reset();
			updateButtonState();
		} catch (e) {
			alert('リセット時にエラーが発生しました');
		}
	});

	// タイマー終了時のUI制御
	timer.onComplete = () => {
		updateButtonState();
	};

	updateButtonState();
});
