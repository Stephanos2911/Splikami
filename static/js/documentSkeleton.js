
function checkImagesLoaded() {
    const images = document.querySelectorAll('#document-content img');
    let imagesLoaded = 0;

    images.forEach(img => {
        if (img.complete) {
            imagesLoaded++;
        } else {
            img.addEventListener('load', () => {
                imagesLoaded++;
                if (imagesLoaded === images.length) {
                    document.getElementById('skeleton-loader').style.display = 'none';
                    document.getElementById('document-content').style.display = 'block';
                }
            });
        }
    });

    if (imagesLoaded === images.length) {
        document.getElementById('skeleton-loader').style.display = 'none';
        document.getElementById('document-content').style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    checkImagesLoaded();
});

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        document.getElementById('skeleton-loader').style.display = 'block';
        document.getElementById('document-content').style.display = 'none';
        checkImagesLoaded();
    }
});