import { initializeModalToggle, handleModalBackgroundClick, setupCloseModalTriggers } from './modals.js';
import { initializeLogin, initializeLoginForm } from './login.js';
import { initializeRegistrationForm } from './register.js';

document.addEventListener('DOMContentLoaded', () => {
    const authModal = document.getElementById('auth-modal');
    const isAuthenticated = document.body.getAttribute('data-is-authenticated') === 'true';
    const loginFormContainer = document.getElementById('login-form-container');
    const registerFormContainer = document.getElementById('register-form-container');
    const welcomeModal = document.getElementById('welcome-modal');
    const navbarBurgers = Array.from(document.querySelectorAll('.navbar-burger'));
    const archiveLink = document.getElementById('archive-link');
        

    if (authModal) {
        // Modal functionalities
        handleModalBackgroundClick(authModal);
        setupCloseModalTriggers(authModal);
        initializeModalToggle(authModal);
    }

    if (welcomeModal) {
        handleModalBackgroundClick(welcomeModal);
        setupCloseModalTriggers(welcomeModal);
    }

    // Ensure only login form is visible initially
    if (loginFormContainer && registerFormContainer) {
        loginFormContainer.classList.remove('is-hidden');
        registerFormContainer.classList.add('is-hidden');
    }

    // Navbar Burger Toggle
    if (navbarBurgers.length > 0) {
        navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = el.dataset.target;
                const targetElement = document.getElementById(target);
                el.classList.toggle('is-active');
                targetElement.classList.toggle('is-active');
            });
        });
    }
    
    // Login button functionality
    initializeLogin(authModal);

    // Login and registration functionality
    initializeLoginForm(authModal, isAuthenticated);
    initializeRegistrationForm(authModal);

    if (archiveLink) {
        archiveLink.addEventListener('click', (e) => {
            if (!isAuthenticated) {
                e.preventDefault();
                const nextPage = archiveLink.getAttribute('href');
                document.querySelector('#login-form input[name="next"]').value = nextPage;
                authModal.classList.add('is-active');
            }
        });
    }
});
