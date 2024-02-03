$(document).ready(function () {
    $('#searchForm').submit(function (event) {
        event.preventDefault();  // Prevent the form from submitting traditionally
        var query = $('#searchInput').val();

        $.ajax({
            type: 'GET',
            url: '/search',
            data: { query: query },
            success: function (data) {
                displayResults(data);
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });

    function displayResults(results) {
        var resultsContainer = $('#searchResults');
        resultsContainer.empty();

        if (results.length > 0) {
            results.forEach(function (result) {
                var resultItem = $('<div>').text(result.title);
                resultsContainer.append(resultItem);
            });
        } else {
            resultsContainer.append('<div>No results found.</div>');
        }
    }
});
