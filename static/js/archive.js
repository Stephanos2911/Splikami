// SEARCH
function performSearch() {
    var query = document.getElementById('search-input').value;
    if (query.length === 0) {
        document.getElementById('search-results').style.display = 'none';
        return; // Hide search results if query is empty
    }

    var url = "/archive/search/?q=" + encodeURIComponent(query);

    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        var resultsContainer = document.getElementById('search-results');
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = data.html;
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.getElementById('search-input');
    var clearIcon = document.getElementById('clear-search-icon');
    
    // Initially hide the "X" icon
    clearIcon.style.display = 'none';

    // Attach event listener to the input field
    searchInput.addEventListener('input', function() {
        if (searchInput.value.length > 0) {
            clearIcon.style.display = 'inline-block';  // Show the "X" icon
        } else {
            clearIcon.style.display = 'none';  // Hide the "X" icon
        }
    });

    // Attach click event to the clear icon
    clearIcon.addEventListener('click', function() {
        clearSearch();
    });

    function clearSearch() {
        // Clear the input field
        searchInput.value = '';
        // Hide the "X" icon
        clearIcon.style.display = 'none';
        // Hide the search results container
        document.getElementById('search-results').style.display = 'none';
    }

    // Handle sorting via dropdown
    var sortSelect = document.getElementById('sort-select');
    sortSelect.addEventListener('change', function() {
        updateDocumentList(1);
    });

    // Update total results on initial page load
    var totalResultsElement = document.getElementById('total-results');
    if (totalResultsElement) {
        var initialTotalResults = totalResultsElement.textContent.match(/\d+/)[0];
        updateTotalResults(initialTotalResults);
    }
});

// Function to update total results
function updateTotalResults(total) {
    var totalResultsElement = document.getElementById('total-results');
    if (totalResultsElement) {
        totalResultsElement.textContent = total + ' resultaten';
    }
}

// Filter and sorting
function updateDocumentList(page = 1) {
    var form = document.querySelector('#filter-form');
    var formData = new FormData(form);

    // Get sorting parameters from dropdown
    var sortValue = document.getElementById('sort-select').value;
    var [sortField, sortOrder] = sortValue.split('-');
    formData.append('sort', sortField);
    formData.append('order', sortOrder);

    formData.append('page', page);
    var url = "/archive/";

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams(formData)  // Serialize formData
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('#document-list').innerHTML = data.html;
        document.querySelector('#pagination').innerHTML = data.pagination_html;
        updateTotalResults(data.total_results);  // Update total results
        toggleResetButton();
    })
    .catch(error => console.error('Error:', error));
}

// Function to reset all filters
function resetFilters() {
    document.querySelector('select[name="rubric"]').value = "";
    document.querySelector('select[name="subject"]').value = "";
    document.querySelector('select[name="collections"]').value = "";
    // Reset sorting options
    document.querySelectorAll('.sort-option .sort-link').forEach(link => {
        link.classList.remove('is-active');
        link.dataset.order = link.dataset.sort === 'title' ? 'asc' : 'desc'; // Reset to default order
    });
    updateDocumentList();
    toggleResetButton();

    // Remove 'sort' and 'order' parameters from the URL
    var url = new URL(window.location.href);
    url.searchParams.delete('sort');
    url.searchParams.delete('order');
    window.history.pushState({}, '', url);
}

// Function to toggle the visibility of the reset button
function toggleResetButton() {
    var rubric = document.querySelector('select[name="rubric"]').value;
    var subject = document.querySelector('select[name="subject"]').value;
    var collection = document.querySelector('select[name="collections"]').value;

    // Check if any sorting option is active
    var sortingChanged = false;
    document.querySelectorAll('.sort-option .sort-link').forEach(link => {
        if (link.classList.contains('is-active')) {
            sortingChanged = true;
        }
    });

    if (rubric || subject || collection || sortingChanged) {
        document.getElementById('reset-filters-button').style.display = 'block';
    } else {
        document.getElementById('reset-filters-button').style.display = 'none';
    }
}

// Attach event listeners to form elements
document.querySelectorAll('#filter-form select').forEach(select => {
    select.addEventListener('change', function() {
        updateDocumentList(1); // Reset to page 1 when a filter is selected
    });
    select.addEventListener('change', toggleResetButton); // Add listener to toggle reset button
});

// Update the active sort link after AJAX request
function updateSortLinks() {
    var params = new URLSearchParams(window.location.search);
    document.querySelectorAll('.sort-option a').forEach(link => {
        var sort = params.get('sort');
        var order = params.get('order');
        if (link.href.includes(`sort=${sort}`) && link.href.includes(`order=${order}`)) {
            link.classList.add('is-active');
        } else {
            link.classList.remove('is-active');
        }
    });
}

// Initialize sort links and toggle reset button on page load
updateSortLinks();
toggleResetButton();

// Handle sorting option clicks
document.querySelectorAll('.sort-option .sort-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        // Toggle sort order if already active
        if (this.classList.contains('is-active')) {
            this.dataset.order = this.dataset.order === 'asc' ? 'desc' : 'asc';
        } else {
            // Remove active class from other links
            document.querySelectorAll('.sort-option .sort-link').forEach(l => l.classList.remove('is-active'));
            // Set default order based on sort field
            this.dataset.order = this.dataset.sort === 'title' ? 'asc' : 'desc';
        }
        // Add active class to clicked link
        this.classList.add('is-active');
        updateDocumentList(1);
        toggleResetButton();
    });
});

// Add event listener for pagination links using event delegation
document.addEventListener('click', function(e) {
    // Target both pagination-link class and pagination-previous/pagination-next classes
    if (e.target.matches('.pagination-link, .pagination-previous, .pagination-next')) {
        e.preventDefault();
        if (!e.target.hasAttribute('disabled')) {  // Check if the button is not disabled
            const page = e.target.dataset.page;
            if (page) {
                updateDocumentList(page);
            }
        }
    }
});
