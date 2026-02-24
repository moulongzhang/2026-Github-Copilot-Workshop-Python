
class PomodoroTimer {
	constructor(duration = 25 * 60) {
		this.defaultDuration = duration;
		this.timeRemaining = duration;
		this.isRunning = false;
		this.intervalId = null;
	}


	start() {
		if (this.isRunning) return;
		if (this.timeRemaining <= 0) {
			this.timeRemaining = this.defaultDuration;
			this.updateDisplay();
		}
		this.isRunning = true;
		this.intervalId = setInterval(() => this.tick(), 1000);
	}

	pause() {
		if (!this.isRunning) return;
		this.isRunning = false;
		clearInterval(this.intervalId);
	}

	reset() {
		this.pause();
		this.timeRemaining = this.defaultDuration;
		this.updateDisplay();
	}


	tick() {
		if (this.timeRemaining > 0) {
			this.timeRemaining--;
			this.updateDisplay();
		} else {
			this.timeRemaining = 0;
			this.updateDisplay();
			this.pause();
			// セッション切り替え等はMVPでは未実装
			if (typeof this.onComplete === 'function') {
				this.onComplete();
			}
		}
	}

	updateDisplay() {
		let t = this.timeRemaining;
		if (typeof t !== 'number' || isNaN(t) || t < 0) t = 0;
		const minutes = String(Math.floor(t / 60)).padStart(2, '0');
		const seconds = String(t % 60).padStart(2, '0');
		document.getElementById('minutes').textContent = minutes;
		document.getElementById('seconds').textContent = seconds;
	}
}

window.pomodoroTimer = new PomodoroTimer();
window.addEventListener('DOMContentLoaded', () => {
	window.pomodoroTimer.updateDisplay();
});
