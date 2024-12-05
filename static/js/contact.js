document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(contactForm);

            fetch(contactForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const messagesDiv = document.getElementById('form-messages');
                messagesDiv.classList.remove('is-hidden');
                messagesDiv.innerHTML = '';
                if (data.success) {
                    messagesDiv.classList.add('is-success');
                    messagesDiv.innerHTML = '<button class="delete"></button>' + data.message;
                } else {
                    messagesDiv.classList.add('is-danger');
                    messagesDiv.innerHTML = '<button class="delete"></button>' + data.message;
                }

                const deleteButton = messagesDiv.querySelector('.delete');
                if (deleteButton) {
                    deleteButton.addEventListener('click', () => {
                        messagesDiv.classList.add('is-hidden');
                    });
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Drawer Toggle
    const contactButton = document.getElementById('contact-drawer-btn');
    const drawer = document.getElementById('drawer');
    const closeDrawerButton = document.getElementById('drawer-close-btn');
    const drawerOverlay = document.getElementById('drawer-overlay');

    if (contactButton && drawer && closeDrawerButton && drawerOverlay) {
        const toggleDrawer = (show) => {
            drawer.classList.toggle('drawer-show', show);
            drawerOverlay.classList.toggle('drawer-overlay-show', show);
        };

        contactButton.addEventListener('click', () => toggleDrawer(true));
        closeDrawerButton.addEventListener('click', () => toggleDrawer(false));
        drawerOverlay.addEventListener('click', () => toggleDrawer(false));

        document.querySelectorAll('.contact-link').forEach(link => {
            link.addEventListener('click', () => toggleDrawer(true));
        });
    }
});
