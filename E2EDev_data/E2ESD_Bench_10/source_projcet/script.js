const quizData = [
  {
    question: "What is the capital of France?",
    options: ["Berlin", "Madrid", "Paris", "Lisbon"],
    answer: "Paris",
  },
  {
    question: "What is 2 + 2?",
    options: ["3", "4", "5", "6"],
    answer: "4",
  },
  {
    question: "What is the largest ocean on Earth?",
    options: [
      "Atlantic Ocean",
      "Indian Ocean",
      "Arctic Ocean",
      "Pacific Ocean",
    ],
    answer: "Pacific Ocean",
  },
];

let currentQuestionIndex = 0;
let score = 0;

const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");
const nextButton = document.getElementById("next-button");
const scoreElement = document.getElementById("score");

function loadQuestion() {
  const currentQuestion = quizData[currentQuestionIndex];
  questionElement.textContent = currentQuestion.question;
  optionsElement.innerHTML = "";

  currentQuestion.options.forEach((option, index) => {
    const optionElement = document.createElement("div");
    optionElement.classList.add("option");
    optionElement.innerHTML = `
      <input type="radio" name="option" value="${option}" data-testid="option-${index}">
      <label data-testid="option-label-${index}">${option}</label>
    `;
    optionsElement.appendChild(optionElement);
  });
}

function calculateScore() {
  const selectedOption = document.querySelector('input[name="option"]:checked');
  if (
    selectedOption &&
    selectedOption.value === quizData[currentQuestionIndex].answer
  ) {
    score++;
  }
}

nextButton.addEventListener("click", () => {
  calculateScore();
  currentQuestionIndex++;

  if (currentQuestionIndex < quizData.length) {
    loadQuestion();
  } else {
    questionElement.classList.add("hidden");
    optionsElement.classList.add("hidden");
    nextButton.classList.add("hidden");
    scoreElement.classList.remove("hidden");
    scoreElement.textContent = `You scored ${score} out of ${quizData.length}`;
  }
});

// Load the first question
loadQuestion();
