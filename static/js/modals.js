export function initializeModalToggle(authModal) {
    const loginFormContainer = document.getElementById('login-form-container');
    const registerFormContainer = document.getElementById('register-form-container');
    const showRegisterForm = document.getElementById('show-register-form');
    const showLoginForm = document.getElementById('show-login-form');


    if (showRegisterForm && showLoginForm) {
        showRegisterForm.addEventListener('click', (e) => {
            e.preventDefault();
            loginFormContainer.classList.add('is-hidden');
            registerFormContainer.classList.remove('is-hidden');
        });

        showLoginForm.addEventListener('click', (e) => {
            e.preventDefault();
            registerFormContainer.classList.add('is-hidden');
            loginFormContainer.classList.remove('is-hidden');
        });
    }
}

export function handleModalBackgroundClick(modal) {
    const modalBackground = modal.querySelector('.modal-background');
    if (modalBackground) {
        modalBackground.addEventListener('click', () => {
            modal.classList.remove('is-active');
        });
    }
}

export function setupCloseModalTriggers(modal) {
    const closeTriggers = modal.querySelectorAll('.modal-close, #cancel-login-btn, #cancel-registration-btn, #close-welcome-modal');
    closeTriggers.forEach((trigger) => {
        trigger.addEventListener('click', () => {
            modal.classList.remove('is-active');
        });
    });
}
