import { setupCloseModalTriggers } from './modals.js';

export function initializeRegistrationForm(authModal) {
    const registrationForm = document.getElementById('registration-form');
    const errorContainer = document.getElementById('registration-error-message');
    const welcomeModal = document.getElementById('welcome-modal');

    if (registrationForm) {
        registrationForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const formData = new FormData(registrationForm);
            errorContainer.innerHTML = '';

            fetch(registrationForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then((response) => {
                if (response.ok) {
                    if (welcomeModal) {
                        welcomeModal.classList.add('is-active'); 
                        setupCloseModalTriggers(welcomeModal);
                    }
                    if (authModal) {
                        authModal.classList.remove('is-active');
                    }
                } else {
                    return response.json().then((data) => {
                        throw data;
                    });
                }
            })
            .catch((errors) => {
                if (errors && typeof errors === 'object') {
                    for (const [field, messages] of Object.entries(errors)) {
                        const inputField = registrationForm.querySelector(`[name="${field}"]`);
                        if (inputField) {
                            inputField.classList.add('is-danger');
                        }
                        errorContainer.innerHTML += `<p class="help is-danger">${messages.join('<br>')}</p>`;
                    }
                } else {
                    errorContainer.innerHTML = '<p class="help is-danger">Unexpected error occurred. Please try again.</p>';
                }
            });
        });
    }
}
