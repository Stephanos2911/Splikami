document.addEventListener('DOMContentLoaded', function() {
    const pagesData = JSON.parse(document.getElementById('pages-data').textContent);
    const pageList = document.getElementById('page-list');
    let currentPage = parseInt(document.getElementById('current-page').value);

    pagesData.forEach(page => {
        const isActive = page.page_number === currentPage;
        const pageBox = document.createElement('div');
        pageBox.className = 'column is-full';
        pageBox.innerHTML = `
            <div class="box page-box ${isActive ? 'active' : ''}" data-page-number="${page.page_number}">
                <div class="media">
                    <div class="media-left">
                        <figure class="image is-64x64">
                            <img src="${page.thumbnail}" alt="Page ${page.page_number}">
                        </figure>
                    </div>
                    <div class="media-content">
                        <p class="title is-6 mb-0">Pagina ${page.page_number}</p>
                        <small>"${page.text_snippet}..."</small>
                    </div>
                </div>
            </div>
        `;
        pageList.appendChild(pageBox);
    });

    // Function to load the selected page
    function loadPage(pageNumber) {
        const selectedPage = pagesData.find(p => p.page_number === pageNumber);
        if (selectedPage) {
            // Initiate loading state
            const skeleton = document.getElementById("skeleton");
            const image = document.getElementById("interactive-image");
            skeleton.classList.remove('hidden');
            image.style.display = 'none';

            // Update the image source
            document.getElementById('interactive-image').src = selectedPage.image;
            // Update the current page display
            document.getElementById('current-page-display').textContent = pageNumber;
            document.getElementById('current-page').value = pageNumber;
            // Update active state
            document.querySelectorAll('.page-box').forEach(box => box.classList.remove('active'));
            document.querySelector(`.page-box[data-page-number="${pageNumber}"]`).classList.add('active');
            // Close the drawer if desired
            // toggleDrawer(); // Uncomment this line if you want to close the drawer after selection
        }
    }

    // Add click event listeners to page boxes
    document.querySelectorAll('.page-box').forEach(box => {
        box.addEventListener('click', function() {
            const selectedPageNumber = parseInt(this.getAttribute('data-page-number'));
            loadPage(selectedPageNumber);
        });
    });

    // Drawer Toggle
    const pageButton = document.getElementById('page-drawer-btn');
    const drawer = document.getElementById('page-drawer');
    const closeDrawerButton = document.getElementById('page-drawer-close-btn');
    const drawerOverlay = document.getElementById('page-drawer-overlay');

    if (pageButton && drawer && closeDrawerButton && drawerOverlay) {
        const toggleDrawer = (show) => {
            drawer.classList.toggle('drawer-show', show);
            drawerOverlay.classList.toggle('drawer-overlay-show', show);
        };

        pageButton.addEventListener('click', () => toggleDrawer(true));
        closeDrawerButton.addEventListener('click', () => toggleDrawer(false));
        drawerOverlay.addEventListener('click', () => toggleDrawer(false));
    }
});
