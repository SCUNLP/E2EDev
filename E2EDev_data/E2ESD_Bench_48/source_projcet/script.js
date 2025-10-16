let selectedCar = { type: "", pricePerDay: 0 };

function selectCar(type, price) {
  selectedCar.type = type;
  selectedCar.pricePerDay = price;
  document.querySelector('[data-testid="car-type"]').value = type;
  document.querySelector('[data-testid="total-price"]').value = ""; // Clear total price on new selection
}

function calculateTotal() {
  const rentalDays = parseInt(document.querySelector('[data-testid="rental-days"]').value);
  if (rentalDays && selectedCar.pricePerDay) {
    const totalPrice = rentalDays * selectedCar.pricePerDay;
    document.querySelector('[data-testid="total-price"]').value = `$${totalPrice}`;
  } else {
    alert("Please select a car and enter the number of days.");
  }
}

document
  .querySelector('[data-testid="rental-form"]')
  .addEventListener("submit", function (event) {
    event.preventDefault();
    if (selectedCar.type && document.querySelector('[data-testid="total-price"]').value) {
      alert(`Your ${selectedCar.type} rental has been booked!`);
    } else {
      alert(
        "Please select a car and calculate the total price before booking."
      );
    }
  });
