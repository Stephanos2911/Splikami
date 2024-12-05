export function initializeLogin(authModal) {
    const loginButton = document.getElementById('login-btn');
    const loginFormContainer = document.getElementById('login-form-container');
    const registerFormContainer = document.getElementById('register-form-container');

    if (loginButton) {
        loginButton.addEventListener('click', () => {
            // Reset modal state
            if (loginFormContainer && registerFormContainer) {
                loginFormContainer.classList.remove('is-hidden');
                registerFormContainer.classList.add('is-hidden');
            }
            authModal.classList.add('is-active');
        });
    }
}

export function initializeLoginForm(authModal, isAuthenticated) {
    const loginForm = document.getElementById('login-form');
    const loginLinks = document.querySelectorAll('.login-required');
    const loginErrorMessage = document.getElementById('login-error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            loginErrorMessage.textContent = '';

            try {
                const response = await fetch(loginForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (response.ok) {
                    const nextPage = loginForm.querySelector('input[name="next"]').value || '/';
                    window.location.href = nextPage;
                } else {
                    const data = await response.json();
                    loginErrorMessage.textContent = data.error || 'Unexpected error occurred. Please try again.';
                }
            } catch (error) {
                loginErrorMessage.textContent = 'Unexpected error occurred. Please try again.';
            }
        });
    }

    loginLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            if (isAuthenticated) return;
            e.preventDefault();
            const nextPage = link.getAttribute('href');
            loginForm.querySelector('input[name="next"]').value = nextPage;
            authModal.classList.add('is-active');
        });
    });
}
