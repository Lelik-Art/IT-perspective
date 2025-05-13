        async function verifyEmailToken(token) {
            try {
                const response = await fetch(`/api/verify-email?token=${token}`);

                if (!response.ok) {
                    throw new Error('Ошибка подтверждения');
                }

                const result = await response.json();

                return {
                    success: result.success,
                    message: result.success
                        ? 'Электронная почта успешно подтверждена!'
                        : 'Ошибка входа. Пожалуйста, проверьте данные'
                };

            } catch (error) {
                console.error('Ошибка:', error);
                return {
                    success: false,
                    message: 'Ошибка входа. Попробуйте позже'
                };
            }
        }

        async function checkVerificationToken() {
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');

            if (!token) {
                showResult('error', 'Ошибка входа. Недействительная ссылка');
                return;
            }

            try {
                const result = await verifyEmailToken(token);
                if (result.success) {
                    localStorage.setItem('authToken', token);
                }
                showResult(result.success ? 'success' : 'error', result.message);

            } catch (error) {
                showResult('error', 'Ошибка входа. Попробуйте позже');
            }
        }

        function showResult(status, message) {
            const verificationStatus = document.getElementById('verificationStatus');
            const resultElement = document.getElementById('resultMessage');
            const messageDiv = resultElement.querySelector('.status-message');

            verificationStatus.style.display = 'none';
            resultElement.style.display = 'block';
            messageDiv.textContent = message;
            messageDiv.className = `status-message ${status}`;
        }

        window.onload = checkVerificationToken;