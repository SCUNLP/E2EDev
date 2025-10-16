'use strict';

/*
console.log(document.querySelector('[data-testid="game-message"]').textContent);
document.querySelector('[data-testid="game-message"]').textContent = '🎉 Correct Number!';

document.querySelector('[data-testid="hidden-number"]').textContent = 13;
document.querySelector('[data-testid="current-score"]').textContent = 10;

document.querySelector('[data-testid="guess-input"]').value = 23;
console.log(document.querySelector('[data-testid="guess-input"]').value);
*/

let secretNumber = Math.trunc(Math.random() * 20) + 1;
let score = 20;
let highscore = 0;

const displayMessage = function (message) {
  document.querySelector('[data-testid="game-message"]').textContent = message;
};

document.querySelector('[data-testid="check-button"]').addEventListener('click', function () {
  const guess = Number(document.querySelector('[data-testid="guess-input"]').value);
  console.log(guess, typeof guess);

  // When there is no input
  if (!guess) {
    displayMessage('⛔️ No number!');

    // When player wins
  } else if (guess === secretNumber) {
    displayMessage('🎉 Correct Number!');
    document.querySelector('[data-testid="hidden-number"]').textContent = secretNumber;

    document.querySelector('body').style.backgroundColor = '#60b347';
    document.querySelector('[data-testid="hidden-number"]').style.width = '30rem';

    if (score > highscore) {
      highscore = score;
      document.querySelector('[data-testid="highscore-value"]').textContent = highscore;
    }

    // When guess is wrong
  } else if (guess !== secretNumber) {
    if (score > 1) {
      displayMessage(guess > secretNumber ? '📈 Too high!' : '📉 Too low!');
      score--;
      document.querySelector('[data-testid="current-score"]').textContent = score;
    } else {
      displayMessage('💥 You lost the game!');
      document.querySelector('[data-testid="current-score"]').textContent = 0;
    }
  }
});

document.querySelector('[data-testid="again-button"]').addEventListener('click', function () {
  score = 20;
  secretNumber = Math.trunc(Math.random() * 20) + 1;

  displayMessage('Start guessing...');
  document.querySelector('[data-testid="current-score"]').textContent = score;
  document.querySelector('[data-testid="hidden-number"]').textContent = '?';
  document.querySelector('[data-testid="guess-input"]').value = '';

  document.querySelector('body').style.backgroundColor = '#222';
  document.querySelector('[data-testid="hidden-number"]').style.width = '15rem';
});
