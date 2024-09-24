document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');

    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')  // Ensure this token is included
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update comments list
                    const commentsContainer = document.querySelector('.ratings-comments');
                    if (commentsContainer) {
                        commentsContainer.innerHTML = data.comments_html; // Ensure this matches your Django response
                    }
                } else {
                    alert('Error adding comment.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});
