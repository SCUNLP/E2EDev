document.querySelector('[data-testid="generate-random-number-button"]').addEventListener('click', function() {
  const min = parseInt(document.querySelector('[data-testid="min"]').value) || 1;
  const max = parseInt(document.querySelector('[data-testid="max"]').value) || 100;
  
  const randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;

  const numberDisplay = document.querySelector('[data-testid="random-number-display"]');
  numberDisplay.innerText = randomNumber;

  numberDisplay.style.transform = 'scale(1.2)';
  setTimeout(() => {
    numberDisplay.style.transform = 'scale(1)';
  }, 300);
});

document.querySelector('[data-testid="copy-to-clipboard-button"]').addEventListener('click', function() {
  const randomNumber = document.querySelector('[data-testid="random-number-display"]').innerText;
  
  const tempInput = document.createElement('input');
  document.body.appendChild(tempInput);
  tempInput.value = randomNumber;
  tempInput.select();
  document.execCommand('copy');
  document.body.removeChild(tempInput);

  const copyButton = document.querySelector('[data-testid="copy-to-clipboard-button"]');
  copyButton.innerText = 'Copied!';
  setTimeout(() => {
    copyButton.innerText = 'Copy to Clipboard';
  }, 2000);
});
