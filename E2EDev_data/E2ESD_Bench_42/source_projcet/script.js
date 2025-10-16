document.querySelector("[data-testid='calculate-button']").addEventListener("click", function () {
    const job = document.querySelector("[data-testid='job-input']").value || "______";
    const workHour = parseInt(document.querySelector("[data-testid='work-hour-input']").value) || 0;
    const workWeek = parseInt(document.querySelector("[data-testid='work-week-input']").value) || 0;
    const grossSalary = parseFloat(document.querySelector("[data-testid='gross-salary-input']").value) || 0;
    const tax = parseFloat(document.querySelector("[data-testid='tax-input']").value) || 0;
    const overtimeHours = parseInt(document.querySelector("[data-testid='overtime-hours-input']").value) || 0;
    const overtimeRate = parseFloat(document.querySelector("[data-testid='overtime-rate-input']").value) || 0;

    const monthlyTaxDeduction = (grossSalary * tax) / 100;
    const netMonthlySalary = grossSalary - monthlyTaxDeduction;
    const hourlySalary = netMonthlySalary / (workWeek * workHour * 4);
    const dailySalary = hourlySalary * workHour;
    const yearlySalary = netMonthlySalary * 12;
    const overtimeEarnings = overtimeHours * overtimeRate * 4;
    const totalEarnings = yearlySalary + overtimeEarnings;

    document.querySelector("[data-testid='job-title']").textContent = job;
    document.querySelector("[data-testid='hourly-salary']").textContent = `$${hourlySalary.toFixed(2)}`;
    document.querySelector("[data-testid='daily-salary']").textContent = `$${dailySalary.toFixed(2)}`;
    document.querySelector("[data-testid='monthly-gross-salary']").textContent = `$${grossSalary.toFixed(2)}`;
    document.querySelector("[data-testid='tax-deduction']").textContent = `-$${monthlyTaxDeduction.toFixed(2)}`;
    document.querySelector("[data-testid='monthly-net-salary']").textContent = `$${netMonthlySalary.toFixed(2)}`;
    document.querySelector("[data-testid='yearly-net-salary']").textContent = `$${yearlySalary.toFixed(2)}`;
    document.querySelector("[data-testid='overtime-earnings']").textContent = `$${overtimeEarnings.toFixed(2)}`;
    document.querySelector("[data-testid='total-earnings']").textContent = `$${totalEarnings.toFixed(2)}`;
});

document.querySelector("[data-testid='clear-button']").addEventListener("click", function () {
    document.querySelector("[data-testid='salary-form']").reset();
    document.querySelector("[data-testid='job-title']").textContent = "______";
    document.querySelector("[data-testid='hourly-salary']").textContent = "$0";
    document.querySelector("[data-testid='daily-salary']").textContent = "$0";
    document.querySelector("[data-testid='monthly-gross-salary']").textContent = "$0";
    document.querySelector("[data-testid='tax-deduction']").textContent = "$0";
    document.querySelector("[data-testid='monthly-net-salary']").textContent = "$0";
    document.querySelector("[data-testid='yearly-net-salary']").textContent = "$0";
    document.querySelector("[data-testid='overtime-earnings']").textContent = "$0";
    document.querySelector("[data-testid='total-earnings']").textContent = "$0";
});
