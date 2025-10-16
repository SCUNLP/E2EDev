document.querySelectorAll('[data-testid="register-tab-button"], [data-testid="view-tab-button"]').forEach((button) => {
  button.addEventListener('click', () => {
    const tab = button.getAttribute('data-tab');

    // Update active tab button
    document.querySelectorAll('[data-testid="register-tab-button"], [data-testid="view-tab-button"]').forEach((btn) => btn.classList.remove('active'));
    button.classList.add('active');

    // Update active tab content
    document.querySelectorAll('[data-testid="register-tab-content"], [data-testid="view-tab-content"]').forEach((content) => content.classList.remove('active'));
    document.getElementById(tab).classList.add('active');
  });
});

// Registration Form Logic
document.addEventListener('DOMContentLoaded', () => {
  loadRegistrations(); // Load saved registrations on page load
});

const form = document.getElementById('registrationForm');
const registrationTable = document.getElementById('registrationTable');
let editIndex = null;

// Load registrations from local storage
function loadRegistrations() {
  const registrations = JSON.parse(localStorage.getItem('registrations')) || [];
  displayRegistrations(registrations);
}

// Save new or updated registration to local storage
function saveRegistration(registration) {
  let registrations = JSON.parse(localStorage.getItem('registrations')) || [];
  if (editIndex !== null) {
    registrations[editIndex] = registration;
    editIndex = null;
  } else {
    registrations.push(registration);
  }
  localStorage.setItem('registrations', JSON.stringify(registrations));
  loadRegistrations();
}

// Delete a registration
function deleteRegistration(index) {
  let registrations = JSON.parse(localStorage.getItem('registrations')) || [];
  registrations.splice(index, 1);
  localStorage.setItem('registrations', JSON.stringify(registrations));
  loadRegistrations();
}

// Display registrations in the table
function displayRegistrations(registrations) {
  const tableBody = registrationTable.querySelector('tbody');
  tableBody.innerHTML = '';
  registrations.forEach((registration, index) => {
    const row = `
      <tr data-id="registration-row-${index}">
        <td>${registration.ownerName}</td>
        <td>${registration.carModel}</td>
        <td>${registration.licenseNumber}</td>
        <td>${registration.registrationDate}</td>
        <td>
          <button class="edit-btn" onclick="editRegistration(${index})" data-id="edit-btn-${index}">Edit</button>
          <button class="delete-btn" onclick="deleteRegistration(${index})" data-id="delete-btn-${index}">Delete</button>
        </td>
      </tr>
    `;
    tableBody.insertAdjacentHTML('beforeend', row);
  });
}

// Handle form submission
form.addEventListener('submit', (e) => {
  e.preventDefault();
  const registration = {
    ownerName: document.getElementById('ownerName').value.trim(),
    carModel: document.getElementById('carModel').value.trim(),
    licenseNumber: document.getElementById('licenseNumber').value.trim(),
    registrationDate: document.getElementById('registrationDate').value,
  };

  if (!registration.ownerName || !registration.carModel || !registration.licenseNumber || !registration.registrationDate) {
    alert('Please fill out all fields.');
    return;
  }

  saveRegistration(registration);
  form.reset();
});

// Edit a registration
window.editRegistration = function (index) {
  const registrations = JSON.parse(localStorage.getItem('registrations')) || [];
  const registration = registrations[index];

  document.getElementById('ownerName').value = registration.ownerName;
  document.getElementById('carModel').value = registration.carModel;
  document.getElementById('licenseNumber').value = registration.licenseNumber;
  document.getElementById('registrationDate').value = registration.registrationDate;

  editIndex = index; // Set index for editing
};
