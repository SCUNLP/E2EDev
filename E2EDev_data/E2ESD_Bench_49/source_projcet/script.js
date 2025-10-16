const students = [];

function addStudent(event) {
  event.preventDefault();
  
  // Accessing elements using their `data-testid` attributes for consistency
  const name = document.querySelector('[data-testid="student-name"]').value;
  const grade = parseInt(document.querySelector('[data-testid="student-grade"]').value);
  
  students.push({ name, grade });
  document.querySelector('[data-testid="student-form"]').reset();
  displayStudents();
}

function displayStudents() {
  const studentList = document.querySelector('[data-testid="student-list"]');
  studentList.innerHTML = '';

  students.forEach((student, index) => {
    const li = document.createElement('li');
    li.textContent = `${student.name}: ${student.grade}`;
    li.setAttribute('data-id', `student-item-${index + 1}`); // Assigning a unique `data-id` for each student item
    studentList.appendChild(li);
  });
}
