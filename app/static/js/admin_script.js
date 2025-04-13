// app/static/js/admin_script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("عوالمنا - Admin Script Loaded");

    const storiesListContainer = document.getElementById('pending-stories-list');
    const generalFeedbackDiv = document.getElementById('general-feedback');
    // Assuming the no-stories message is initially present (maybe hidden) or dynamically added
    let noStoriesMessage = document.getElementById('no-stories-message');
    const listContainerParent = document.getElementById('stories-list-container'); // Get parent to add message if needed

    // --- Function to show feedback messages ---
    function showFeedback(element, message, type = 'error') {
        if (!element) return;
        element.textContent = message;
        element.className = `feedback-message alert alert-${type === 'success' ? 'success' : 'danger'}`; // Use Bootstrap-like classes or your own
        element.style.display = 'block';
        // Automatically hide after a few seconds (optional)
        /*
        setTimeout(() => {
            hideFeedback(element);
        }, 5000);
        */
    }

    // --- Function to hide feedback messages ---
    function hideFeedback(element) {
        if (!element) return;
        element.style.display = 'none';
        element.textContent = '';
        element.className = 'feedback-message';
    }

    // --- Function to set processing state on story item ---
    function setProcessingState(storyItem, isProcessing) {
        if (!storyItem) return;
        if (isProcessing) {
            storyItem.classList.add('processing'); // Add a class for styling (e.g., opacity)
        } else {
            storyItem.classList.remove('processing');
        }
        // Disable buttons within the item
        storyItem.querySelectorAll('button').forEach(button => button.disabled = isProcessing);
    }

    // --- Function to show the "no stories" message ---
    function showNoStoriesMessage() {
        // If the element exists, show it
        if (noStoriesMessage) {
            noStoriesMessage.style.display = 'block';
        } else if (listContainerParent) {
            // If it doesn't exist, create and append it
            noStoriesMessage = document.createElement('p');
            noStoriesMessage.id = 'no-stories-message';
            noStoriesMessage.textContent = 'لا توجد قصص بحاجة للمراجعة في الوقت الحالي.';
            noStoriesMessage.style.textAlign = 'center';
            noStoriesMessage.style.color = '#6c757d';
            noStoriesMessage.style.padding = '30px';
            noStoriesMessage.style.fontSize = '1.15em';
            noStoriesMessage.style.backgroundColor = '#f8f9fa';
            noStoriesMessage.style.border = '1px dashed #ced4da';
            noStoriesMessage.style.borderRadius = '6px';
            listContainerParent.appendChild(noStoriesMessage); // Append to the parent container
        }
    }
    function hideNoStoriesMessage() {
        if(noStoriesMessage) {
            noStoriesMessage.style.display = 'none';
        }
    }


    // --- Event listener for Approve/Reject buttons ---
    if (storiesListContainer) {
        storiesListContainer.addEventListener('click', async (event) => {
            const target = event.target;
            // Find the clicked button and its parent story item
            const actionButton = target.closest('.approve-button, .reject-button');
            if (!actionButton) return; // Exit if click wasn't on an action button

            const storyItem = actionButton.closest('.story-item');
            if (!storyItem || storyItem.classList.contains('processing')) return; // Exit if not in story or already processing

            const storyId = storyItem.dataset.storyId;
            const action = actionButton.classList.contains('approve-button') ? 'approve' : 'reject';

            // Get CSRF token (assuming it's set in a global var or meta tag by the template)
             // Option 1: From global variable set in template <script> const csrfToken = "{{ csrf_token() }}"; </script>
             // const csrf = typeof csrfToken !== 'undefined' ? csrfToken : null;

             // Option 2: From meta tag <meta name="csrf-token" content="{{ csrf_token() }}">
            const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            if (!csrf) {
                console.error('CSRF token not found!');
                showFeedback(generalFeedbackDiv, 'خطأ: لم يتم العثور على رمز الحماية (CSRF). لا يمكن إرسال الطلب.', 'error');
                return;
            }


            if (action && storyId) {
                console.log(`Action: ${action}, Story ID: ${storyId}`);
                setProcessingState(storyItem, true);
                hideFeedback(generalFeedbackDiv); // Clear previous general feedback

                try {
                    const response = await fetch(`/api/stories/${storyId}/status`, { // Use the Flask API route
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'X-CSRFToken': csrf // Send the CSRF token in the header
                        },
                        body: JSON.stringify({ action: action }) // Send action in JSON body
                    });

                    const result = await response.json(); // Assume API always returns JSON

                    if (response.ok && result.success) {
                        console.log("API Success:", result);
                        // Success: Remove item visually and show feedback
                        showFeedback(generalFeedbackDiv, result.message || `تم ${action === 'approve' ? 'قبول' : 'رفض'} القصة بنجاح.`, 'success');

                        storyItem.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                        storyItem.style.opacity = '0';
                        storyItem.style.transform = 'translateX(-50px)'; // Optional animation

                        setTimeout(() => {
                            storyItem.remove();
                            // Check if the list is now empty
                            if (storiesListContainer.children.length === 0) {
                                showNoStoriesMessage();
                            }
                        }, 500); // Wait for animation

                    } else {
                         // Handle API errors (e.g., validation error, story not found, server error)
                         console.error("API Error Response:", result);
                        throw new Error(result.message || `فشل ${action === 'approve' ? 'القبول' : 'الرفض'}. رمز الحالة: ${response.status}`);
                    }

                } catch (error) {
                    // Handle network errors or exceptions during fetch/processing
                    console.error('Error updating story status:', error);
                    showFeedback(generalFeedbackDiv, `خطأ في الشبكة أو الخادم: ${error.message}`, 'error');
                    setProcessingState(storyItem, false); // Re-enable buttons on error
                }
            } // end if action && storyId
        }); // end event listener

         // Initial check: If list is empty on load, show the message
         if (storiesListContainer && storiesListContainer.children.length === 0 && !noStoriesMessage?.offsetParent) {
              showNoStoriesMessage();
         } else if (storiesListContainer && storiesListContainer.children.length > 0){
              hideNoStoriesMessage();
         }


    } // end if storiesListContainer

});