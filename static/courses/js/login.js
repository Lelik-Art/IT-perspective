document.getElementById("togglePassword").addEventListener("click", function () {
    const passwordInput = document.getElementById("password");
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);
    this.textContent = type === "password" ? "👁️" : "🙈";
  });
  
  document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault(); // Останавливаем отправку формы
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const remember = document.getElementById("remember").checked;
  
    if (!email || !password) {
      alert("Пожалуйста, заполните все поля.");
      return;
    }
  
    console.log("Email:", email);
    console.log("Password:", password);
    console.log("Запомнить меня:", remember);
  
    // Тут может быть запрос на сервер
    alert("Авторизация выполнена!");
  });
  