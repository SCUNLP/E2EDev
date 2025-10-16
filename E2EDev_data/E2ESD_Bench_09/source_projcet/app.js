const scheduleForm = document.querySelector("[data-testid='schedule-form']");
const taskForm = document.querySelector("[data-testid='task-form']");
const scheduleList = document.querySelector("[data-testid='schedule-list']");
const taskList = document.querySelector("[data-testid='task-list']");

scheduleForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const subject = document.querySelector("[data-testid='subject']").value;
  const date = document.querySelector("[data-testid='date']").value;
  const time = document.querySelector("[data-testid='time']").value;
  addSchedule(subject, date, time);
  scheduleForm.reset();
});

taskForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const task = document.querySelector("[data-testid='task']").value;
  const deadline = document.querySelector("[data-testid='deadline']").value;
  addTask(task, deadline);
  taskForm.reset();
});

function addSchedule(subject, date, time) {
  const scheduleItem = document.createElement("li");
  scheduleItem.textContent = `${subject} - ${date} at ${time}`;
  scheduleList.appendChild(scheduleItem);
}

function addTask(task, deadline) {
  const taskItem = document.createElement("li");
  taskItem.textContent = `${task} - Deadline: ${deadline}`;
  taskList.appendChild(taskItem);
}
