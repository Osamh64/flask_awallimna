// app/static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("عوالمنا - General Script Loaded");

    // --- Flash Message Closing ---
    // Using delegation for potential dynamically added messages
    document.body.addEventListener('click', function(event) {
        if (event.target.matches('.alert .close')) {
            event.target.closest('.alert').style.display = 'none';
        }
    });

    // --- Age Filtering (from children.php functionality) ---
    // Assumes buttons exist with onclick="filterByAge('...')",
    // or you can add event listeners to buttons with data-age attributes.
    window.filterByAge = function(ageGroup) {
        console.log("Filtering by age:", ageGroup);
        // Construct the URL for the children's page with the age query parameter
        const url = new URL(window.location.origin + '/children'); // Adjust '/children' if the route is different
        url.searchParams.set('age', ageGroup);
        window.location.href = url.toString();
    }

    // --- PDF Viewer Basic Setup (for read_story.html) ---
    // This requires PDF.js library to be loaded in the template.
    const pdfViewerContainer = document.getElementById('pdf-viewer'); // Or '#book' from original PHP
    // Get the PDF URL passed from Flask (e.g., via a data attribute or script variable)
    const pdfDataElement = document.getElementById('pdf-data');
    const pdfUrl = pdfDataElement?.dataset.pdfUrl;

    if (pdfViewerContainer && pdfUrl && typeof pdfjsLib !== 'undefined') {
        console.log("Setting up PDF Viewer for:", pdfUrl);
        // Ensure the worker source is set correctly relative to where pdf.js is served
        pdfjsLib.GlobalWorkerOptions.workerSrc = '//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'; // Example CDN

        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        loadingTask.promise.then(function(pdf) {
            console.log('PDF loaded');
            pdfViewerContainer.innerHTML = ''; // Clear previous content/loading message

            // Loop through pages and render them
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                pdf.getPage(pageNum).then(function(page) {
                    console.log('Page loaded:', pageNum);

                    const scale = 1.5;
                    const viewport = page.getViewport({ scale: scale });

                    // Prepare canvas using PDF page dimensions
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    canvas.style.display = 'block'; // Ensure canvases stack vertically
                    canvas.style.marginBottom = '10px'; // Add some space between pages
                    canvas.style.maxWidth = '100%'; // Make it responsive
                    canvas.style.height = 'auto';

                    // Append canvas to the container
                    pdfViewerContainer.appendChild(canvas);

                    // Render PDF page into canvas context
                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport
                    };
                    const renderTask = page.render(renderContext);
                    renderTask.promise.then(function () {
                        console.log('Page rendered:', pageNum);
                    }).catch(function (reason) {
                       console.error(`Error rendering page ${pageNum}:`, reason);
                     });
                }).catch(function (reason) {
                   console.error(`Error loading page ${pageNum}:`, reason);
                });
            } // end for loop
        }, function (reason) {
            // PDF loading error
            console.error("Error loading PDF:", reason);
            pdfViewerContainer.textContent = 'خطأ في تحميل ملف PDF.';
        }).catch(function (reason) {
            console.error("Unhandled error in PDF loading/rendering:", reason);
            pdfViewerContainer.textContent = 'حدث خطأ غير متوقع أثناء عرض الملف.';
        });
    } else if (pdfViewerContainer && !pdfUrl) {
         console.warn("PDF Viewer container found, but no PDF URL provided.");
    } else if(pdfViewerContainer && typeof pdfjsLib === 'undefined') {
         console.error("PDF Viewer container found, but pdf.js library is not loaded.");
         pdfViewerContainer.textContent = 'مكتبة عرض PDF غير محملة.';
    }

    // --- Other potential general scripts ---
    // Example: Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle'); // Add this button to your header
    const nav = document.querySelector('header nav'); // Assuming your nav element
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }

    // Add more general event listeners or functions as needed

});