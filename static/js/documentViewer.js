document.addEventListener("DOMContentLoaded", function() {
    let currentPage = parseInt(document.getElementById('current-page').value, 10);
    const totalPages = parseInt(document.getElementById('total-pages').value, 10);
    const pages = JSON.parse(document.getElementById('pages-data').textContent);

    loadPage(currentPage);

    function centerImage(fullscreen = false) {
        const img = document.getElementById('interactive-image');
        const container = document.querySelector('.view-document-container');

        const viewportWidth = fullscreen ? window.innerWidth : container.offsetWidth;
        const viewportHeight = fullscreen ? window.innerHeight : container.offsetHeight;
        const imgNaturalWidth = img.naturalWidth;
        const imgNaturalHeight = img.naturalHeight;
        const imgAspectRatio = imgNaturalWidth / imgNaturalHeight;

        let displayWidth = viewportWidth;
        let displayHeight = fullscreen ? viewportHeight * 0.9 : viewportHeight;

        if (viewportWidth / viewportHeight > imgAspectRatio) {
            displayWidth = displayHeight * imgAspectRatio;
        } else {
            displayHeight = displayWidth / imgAspectRatio;
        }

        const offsetX = (viewportWidth - displayWidth) / 2;
        const offsetY = (viewportHeight - displayHeight) / 2;

        img.style.width = `${displayWidth}px`;
        img.style.height = `${displayHeight}px`;
        img.style.top = `${offsetY}px`;
        img.style.left = `${offsetX}px`;
        img.style.position = 'absolute';
    }

    // Page navigation
    function loadPage(pageNumber) {
        const skeleton = document.getElementById("skeleton");
        const image = document.getElementById("interactive-image");
        const prevButton = document.getElementById("prev-button");
        const nextButton = document.getElementById("next-button");

        if (prevButton && nextButton) {
            prevButton.style.display = pageNumber > 1 ? 'block' : 'none';
            nextButton.style.display = pageNumber < totalPages ? 'block' : 'none';
        }

        skeleton.classList.remove('hidden');
        image.style.display = 'none';

        const pageData = pages.find(page => page.page_number === pageNumber);

        if (pageData) {
            if (image.src !== pageData.image) {
                image.src = pageData.image;
            }
            image.onload = function() {
                skeleton.classList.add('hidden');
                image.style.display = 'block';
                centerImage(!!document.fullscreenElement);
            };
        } else {
            console.error(`Data for page number ${pageNumber} not found.`);
        }

        // Update page number display
        document.getElementById("current-page-display").innerText = pageNumber;
        document.getElementById('current-page').value = pageNumber;
        // Update active state
        document.querySelectorAll('.page-box').forEach(box => box.classList.remove('active'));
        const activeBox = document.querySelector(`.page-box[data-page-number="${pageNumber}"]`);
        if (activeBox) {
            activeBox.classList.add('active');
        }
    }

    window.navigatePage = function(direction) {
        currentPage = Math.max(1, Math.min(currentPage + direction, totalPages));
        loadPage(currentPage);
        document.getElementById("page-selector").value = currentPage;
    };

    window.goToPage = function(pageNumber) {
        const parsedPageNumber = parseInt(pageNumber, 10);
        if (!isNaN(parsedPageNumber) && parsedPageNumber > 0 && parsedPageNumber <= totalPages) {
            currentPage = parsedPageNumber;
            loadPage(currentPage);
        }
    };

    // Document viewer
    let drag = false;
    let startX, startY;
    let transX = 0, transY = 0, scale = 1, rotation = 0;
    const img = document.getElementById('interactive-image');
    const container = document.querySelector('.view-document-container');

    img.addEventListener('load', function() {
        centerImage(!!document.fullscreenElement);
    });

    window.addEventListener('resize', function() {
        centerImage(!!document.fullscreenElement);
    });

    img.addEventListener('mousedown', function(e) {
        e.preventDefault();
        drag = true;

        const style = window.getComputedStyle(img);
        const matrix = new WebKitCSSMatrix(style.transform);

        transX = matrix.m41 || 0;
        transY = matrix.m42 || 0;

        startX = e.clientX - transX;
        startY = e.clientY - transY;

        return false;
    });

    document.addEventListener('mousemove', function(e) {
        if (drag) {
            transX = e.clientX - startX;
            transY = e.clientY - startY;

            img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
            img.style.transition = 'none';
        }
    });

    document.addEventListener('mouseup', function() {
        drag = false;
        img.style.transition = 'transform 0.3s ease';
    });

    container.addEventListener('wheel', function(e) {
        e.preventDefault();
        const zoomIntensity = 0.1;
        const newScale = scale + (e.deltaY < 0 ? zoomIntensity : -zoomIntensity);
        if (newScale >= 1) {
            scale = newScale;
            img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
            img.style.transition = 'transform 0.3s ease';
        }
    });

    window.zoomIn = function() {
        scale *= 1.1;
        img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
        img.style.transition = 'transform 0.3s ease';
    };

    window.zoomOut = function() {
        if (scale > 1) {
            scale *= 0.9;
            img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
            img.style.transition = 'transform 0.3s ease';
        }
    };

    window.resetImage = function() {
        // Reset the transformation variables
        transX = 0;
        transY = 0;
        scale = 1;
        rotation = 0;

        // Apply the reset transformation to the image
        img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
        img.style.transition = 'transform 0.3s ease'; // Smooth reset

        // Re-center the image to its original position in the container
        centerImage(!!document.fullscreenElement);
    };

    window.rotateImage = function() {
        rotation -= 90;
        img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
        img.style.transition = 'transform 0.3s ease';
    };

    window.toggleFullScreen = function() {
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => {
                console.error(`Error attempting to enter fullscreen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen().catch(err => {
                console.error(`Error attempting to exit fullscreen mode: ${err.message} (${err.name})`);
            });
        }
    };

    document.addEventListener('fullscreenchange', () => {
        const isFullscreen = !!document.fullscreenElement;
        centerImage(isFullscreen);
        img.style.transform = `translate(${transX}px, ${transY}px) scale(${scale}) rotate(${rotation}deg)`;
        img.style.transition = 'transform 0.3s ease';

        // Adjust controls based on fullscreen state
        const controls = document.querySelector('.controls');
        if (controls) {
            controls.style.position = isFullscreen ? 'fixed' : 'absolute';
            controls.style.top = '10px';
            controls.style.right = '10px';
            controls.style.display = 'flex';
            controls.style.zIndex = '1000';
        }
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

    // Add click event listeners to page boxes
    document.querySelectorAll('.page-box').forEach(box => {
        box.addEventListener('click', function() {
            const selectedPageNumber = parseInt(this.getAttribute('data-page-number'));
            loadPage(selectedPageNumber);
            // Update active state
            document.querySelectorAll('.page-box').forEach(box => box.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
