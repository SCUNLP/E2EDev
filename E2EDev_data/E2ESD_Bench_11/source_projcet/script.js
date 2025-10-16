let paymentChart;

document.querySelector('[data-testid="dark-mode-switch"]').addEventListener('change', function() {
  document.body.classList.toggle('dark-mode', this.checked);
});

document.querySelector('[data-testid="calculate-button"]').addEventListener('click', function() {
    const amount = document.querySelector('[data-testid="amount-input"]').value;
    const rate = document.querySelector('[data-testid="rate-input"]').value;
    const years = document.querySelector('[data-testid="years-input"]').value;

    const principal = parseFloat(amount);
    const calculatedInterest = parseFloat(rate) / 100 / 12;
    const calculatedPayments = parseFloat(years) * 12;

    const x = Math.pow(1 + calculatedInterest, calculatedPayments);
    const monthly = (principal * x * calculatedInterest) / (x - 1);

    if (isFinite(monthly)) {
        const totalPayment = (monthly * calculatedPayments).toFixed(2);
        const totalInterest = (totalPayment - principal).toFixed(2);

        document.querySelector('[data-testid="monthly-payment"]').textContent = `Monthly Payment: $${monthly.toFixed(2)}`;
        document.querySelector('[data-testid="total-payment"]').textContent = `Total Payment: $${totalPayment}`;
        document.querySelector('[data-testid="total-interest"]').textContent = `Total Interest: $${totalInterest}`;

        updateChart(principal, totalInterest);
    } else {
        alert('Please check your numbers');
    }
});

document.querySelector('[data-testid="year-slider"]').addEventListener('input', function() {
    document.querySelector('[data-testid="years-input"]').value = this.value;
});

function updateChart(principal, interest) {
    if (paymentChart) {
        paymentChart.destroy(); 
    }

    const ctx = document.querySelector('[data-testid="payment-chart"]').getContext('2d');
    paymentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Principal', 'Interest'],
            datasets: [{
                data: [principal, interest],
                backgroundColor: ['#28a745', '#007bff']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom'
            }
        }
    });
}
