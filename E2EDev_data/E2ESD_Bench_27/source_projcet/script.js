const search = document.querySelector('[data-testid="search-input"]');
const submit = document.querySelector('[data-testid="submit-form"]');
const random = document.querySelector('[data-testid="random-button"]');
const mealsElement = document.querySelector('[data-testid="meals-container"]');
const resultHeading = document.querySelector('[data-testid="result-heading"]');
const singleMealElement = document.querySelector('[data-testid="single-meal-container"]');

// 搜索事件
function searchMeal(e) {
  e.preventDefault();
  singleMealElement.innerHTML = "";

  const term = search.value.trim();

  if (term) {
    fetch(`https://www.themealdb.com/api/json/v1/1/search.php?s=${term}`)
      .then((res) => res.json())
      .then((data) => {
        resultHeading.innerHTML = `<h2>Search results for "${term}":</h2>`;
        if (data.meals === null) {
          mealsElement.innerHTML = "";
          resultHeading.innerHTML = `<p>No results found. Try another keyword!</p>`;
        } else {
          mealsElement.innerHTML = data.meals
            .map(
              (meal) => `
              <div class="meal">
                <img src="${meal.strMealThumb}" alt="${meal.strMeal}" />
                <div class="meal-info" data-mealid="${meal.idMeal}">
                  <h3>${meal.strMeal}</h3>
                </div>
              </div>
            `
            )
            .join("");
        }
      })
      .catch(() => {
        resultHeading.innerHTML = `<p>Failed to fetch meals. Please try again later.</p>`;
      });

    search.value = "";
  } else {
    getRandomMeal();
  }
}

// 获取详情
function getMealById(mealID) {
  fetch(`https://www.themealdb.com/api/json/v1/1/lookup.php?i=${mealID}`)
    .then((res) => res.json())
    .then((data) => {
      const meal = data.meals[0];
      addMealToDOM(meal);
      singleMealElement.scrollIntoView({ behavior: "smooth" });
    })
    .catch(() => {
      singleMealElement.innerHTML = "<p>Failed to load meal details.</p>";
    });
}

// 获取随机菜单
function getRandomMeal() {
  mealsElement.innerHTML = "";
  resultHeading.innerHTML = "";
  singleMealElement.innerHTML = "";

  fetch("https://www.themealdb.com/api/json/v1/1/random.php")
    .then((res) => res.json())
    .then((data) => {
      const meal = data.meals[0];
      addMealToDOM(meal);
    })
    .catch(() => {
      singleMealElement.innerHTML = "<p>Failed to fetch a random meal.</p>";
    });
}

// 将详细菜品添加到页面
function addMealToDOM(meal) {
  const ingredients = [];

  for (let i = 1; i <= 20; i++) {
    const ingredient = meal[`strIngredient${i}`];
    const measure = meal[`strMeasure${i}`];

    if (ingredient && ingredient.trim()) {
      ingredients.push(`${ingredient} - ${measure}`);
    } else {
      break;
    }
  }

  singleMealElement.innerHTML = `
    <div class="single-meal">
      <h1>${meal.strMeal}</h1>
      <img src="${meal.strMealThumb}" alt="${meal.strMeal}" />
      <div class="single-meal-info">
        ${meal.strCategory ? `<p><strong>Category:</strong> ${meal.strCategory}</p>` : ""}
        ${meal.strArea ? `<p><strong>Area:</strong> ${meal.strArea}</p>` : ""}
      </div>
      <div class="main">
        <h2>Ingredients</h2>
        <ul>
          ${ingredients.map((item) => `<li>${item}</li>`).join("")}
        </ul>
        <h2>Instructions</h2>
        <p>${meal.strInstructions}</p>
      </div>
    </div>
  `;
}

// 事件绑定
submit.addEventListener("submit", searchMeal);
random.addEventListener("click", getRandomMeal);

// 监听点击事件，进入详情页
mealsElement.addEventListener("click", (e) => {
  const path = e.composedPath(); // 标准方式
  const mealInfo = path.find((el) => el.classList?.contains("meal-info"));

  if (mealInfo) {
    const mealID = mealInfo.getAttribute("data-mealid");
    getMealById(mealID);
  }
});

// 初始化显示一个随机菜单
getRandomMeal();
