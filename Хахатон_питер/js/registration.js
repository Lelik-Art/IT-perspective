
        const roleButtons = document.querySelectorAll('.role-btn');
const form = document.getElementById('registrationForm');
const password = document.getElementById('password');
const confirmPassword = document.getElementById('confirmPassword');
const passwordMessage = document.getElementById('passwordMessage');
let selectedRole = 'student';

// Переключение ролей
roleButtons.forEach(button => {
    button.addEventListener('click', () => {
        form.reset();
        roleButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        selectedRole = button.dataset.role;
        passwordMessage.style.display = 'none';
    });
});

// Показать/скрыть пароль
function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    const toggleButton = input.nextElementSibling;
    input.type = input.type === 'password' ? 'text' : 'password';
    toggleButton.classList.toggle('open');
}

function validateUsername() {
    const username = document.getElementById('username').value.trim();
    const regex = /^[a-zA-Zа-яА-ЯёЁ\s\-]+$/;
    
    if (username.length < 2) {
        showNotification('error', 'Имя должно содержать минимум 2 символа');
        return false;
    }
    
    if (!regex.test(username)) {
        showNotification('error', 'Имя содержит недопустимые символы');
        return false;
    }
    
    return true;
}

// Валидация пароля
function validatePassword() {
    const englishOnlyRegex = /^[a-zA-Z0-9!@#$%^&*()\-_=+\[\]{}|;:,.<>?]+$/;

    if (password.value.length < 6) {
        passwordMessage.textContent = 'Пароль должен быть не менее 6 символов';
        passwordMessage.style.display = 'block';
        passwordMessage.classList.add('password-mismatch');
        return false;
    }

    if (!englishOnlyRegex.test(password.value)) {
        passwordMessage.textContent = 'Пароль должен содержать только английские символы';
        passwordMessage.style.display = 'block';
        passwordMessage.classList.add('password-mismatch');
        return false;
    }

    if (password.value !== confirmPassword.value) {
        passwordMessage.textContent = 'Пароли не совпадают';
        passwordMessage.style.display = 'block';
        passwordMessage.classList.add('password-mismatch');
        return false;
    }

    passwordMessage.textContent = 'Пароли совпадают';
    passwordMessage.style.display = 'block';
    passwordMessage.classList.remove('password-mismatch');
    passwordMessage.classList.add('password-match');
    return true;
}

// Функция показа уведомлений
function showNotification(type, message) {
    const notifications = document.querySelector('.form-notifications');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<div class="alert-content">${message}</div>`;
    
    notifications.insertBefore(alert, notifications.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Обработка формы
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateUsername() || !validatePassword()) return;

    const formData = {
        username: document.getElementById('username').value.trim(),
        email: document.getElementById('email').value,
        password: password.value,
        role: selectedRole
    };

    try {
        const endpoint = selectedRole === 'student' 
            ? '/api/register/student' 
            : '/api/register/teacher';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('success', `На адрес ${formData.email} отправлено письмо с инструкциями для завершения регистрации`);
            form.reset();
        } else {
            const errorMessage = result.message || getErrorMessage(response.status);
            showNotification('error', errorMessage);
        }
    } catch (err) {
        showNotification('error', 'Ошибка соединения с сервером');
    }
});

function getErrorMessage(statusCode) {
    switch(statusCode) {
        case 400: return 'Некорректные данные регистрации';
        case 409: return 'Этот email уже зарегистрирован';
        case 422: return 'Пароль не соответствует требованиям безопасности';
        default: return 'Ошибка регистрации';
    }
}
