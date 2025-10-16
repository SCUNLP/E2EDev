const currencyOne = document.querySelector('[data-testid="currency-one"]');
const amountOne = document.querySelector('[data-testid="amount-one"]');
const currencyTwo = document.querySelector('[data-testid="currency-two"]');
const amountTwo = document.querySelector('[data-testid="amount-two"]');
const rate = document.querySelector('[data-testid="exchange-rate"]');
const swap = document.querySelector('[data-testid="swap-button"]');

function calculate() {
  const currency_one = currencyOne.value;
  const currency_two = currencyTwo.value;
  fetch(`https://api.exchangerate-api.com/v4/latest/${currency_one}`)
    .then((res) => res.json())
    .then((data) => {
      const currentRate = data.rates[currency_two];
      rate.innerText = `1 ${currency_one} = ${currentRate} ${currency_two}`;
      amountTwo.value = (amountOne.value * currentRate).toFixed(2);
    });
}

currencyOne.addEventListener("change", calculate);
amountOne.addEventListener("input", calculate);
currencyTwo.addEventListener("change", calculate);
amountTwo.addEventListener("input", calculate);

swap.addEventListener("click", () => {
  const storedValue = currencyOne.value;
  currencyOne.value = currencyTwo.value;
  currencyTwo.value = storedValue;
  calculate();
});

calculate();
