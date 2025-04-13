// app/static/js/validatePassword.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("عوالمنا - Password Validation Script Loaded");

    // Adjust selectors based on your registration/reset forms
    const registrationForm = document.querySelector('#registration-form'); // Give your registration form an ID
    const passwordInput = document.querySelector('#password'); // Assumes field ID is 'password'
    const password2Input = document.querySelector('#password2'); // Assumes confirmation field ID is 'password2'
    const passwordCriteriaList = document.querySelector('#password-criteria'); // An element to show criteria status

    // Function to update criteria checklist UI
    function updateCriteriaUI(criteriaMet) {
        if (!passwordCriteriaList) return;
        // Clear previous styles/icons
        passwordCriteriaList.querySelectorAll('li').forEach(li => {
            li.classList.remove('valid', 'invalid');
            // Optionally remove icons like checkmarks/crosses if used
        });

        // Apply new styles/icons
        for (const key in criteriaMet) {
            const liElement = passwordCriteriaList.querySelector(`.${key}`); // e.g., <li class="length">...</li>
            if (liElement) {
                liElement.classList.add(criteriaMet[key] ? 'valid' : 'invalid');
                 // You can add icons here too:
                 // liElement.innerHTML = (criteriaMet[key] ? '✅ ' : '❌ ') + liElement.dataset.text;
            }
        }
        // Check overall validity (all criteria met)
         const allValid = Object.values(criteriaMet).every(v => v === true);
         // Enable/disable submit button? Or show overall message?

    }


    // Function to perform validation
    function validatePassword() {
        if (!passwordInput) return;
        const password = passwordInput.value;
        let criteria = {
            length: false,
            uppercase: false,
            lowercase: false,
            number: false,
            // symbol: false, // Uncomment if you add symbol requirement
            match: false
        };

        // 1. Check Length (e.g., minimum 6 characters from form)
        const minLength = parseInt(passwordInput.getAttribute('minlength') || '6', 10);
        criteria.length = password.length >= minLength;

        // 2. Check for Uppercase letter
        criteria.uppercase = /[A-Z]/.test(password);

        // 3. Check for Lowercase letter
        criteria.lowercase = /[a-z]/.test(password);

        // 4. Check for Number
        criteria.number = /[0-9]/.test(password);

        // 5. Check for Symbol (optional)
        // criteria.symbol = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(password);

        // 6. Check if Passwords Match (if confirmation field exists)
        if (password2Input) {
             const password2 = password2Input.value;
             criteria.match = password && password2 && password === password2;
              // Provide direct feedback for mismatch
              const matchFeedback = password2Input.parentNode.querySelector('.match-feedback'); // Add a div for this
              if (matchFeedback) {
                  if (password && password2 && !criteria.match) {
                      matchFeedback.textContent = 'كلمتا المرور غير متطابقتين.';
                      matchFeedback.style.color = 'red';
                      password2Input.classList.add('is-invalid'); // Bootstrap style
                  } else {
                      matchFeedback.textContent = '';
                      password2Input.classList.remove('is-invalid');
                  }
              }

        } else {
            criteria.match = true; // No confirmation field to check against
        }

        // Update the UI (e.g., a checklist)
        updateCriteriaUI(criteria);

        // Return overall validity (optional, could be used for form submission prevention)
        return Object.values(criteria).every(v => v === true);
    }

    // Add event listeners
    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
    }
    if (password2Input) {
        password2Input.addEventListener('input', validatePassword); // Re-validate on confirmation input too
    }

    // Optional: Prevent form submission if password is invalid
    if (registrationForm) {
        registrationForm.addEventListener('submit', function (event) {
             // Perform final validation check on submit
            if (!validatePassword()) {
                 console.log("Password validation failed. Preventing form submission.");
                event.preventDefault(); // Stop the form from submitting
                // You might want to scroll to the password section or show a general error
                alert('يرجى التأكد من أن كلمة المرور تستوفي جميع الشروط وأنها متطابقة مع حقل التأكيد.');
            }
        });
    }

});

// --- HTML Example for Criteria Checklist (place near password field) ---
/*
<ul id="password-criteria" style="font-size: 0.9em; list-style: none; padding: 0; margin-top: 5px;">
    <li class="length" data-text="طول 6 أحرف على الأقل">طول 6 أحرف على الأقل</li>
    <li class="uppercase" data-text="حرف كبير واحد على الأقل">حرف كبير واحد على الأقل</li>
    <li class="lowercase" data-text="حرف صغير واحد على الأقل">حرف صغير واحد على الأقل</li>
    <li class="number" data-text="رقم واحد على الأقل">رقم واحد على الأقل</li>
    <li class="match" data-text="تطابق كلمتي المرور">تطابق كلمتي المرور</li>
</ul>
<div class="match-feedback" style="font-size: 0.85em; height: 1em;"></div> Style this feedback div
*/

// --- CSS Example for Checklist Styling ---
/*
#password-criteria li::before {
    content: '❌ '; /* Default symbol */
    /* display: inline-block;
    width: 20px; */ /* Adjust spacing */
/* } */
/* #password-criteria li.valid { color: green; }
#password-criteria li.invalid { color: red; } */
/* #password-criteria li.valid::before { content: '✅ '; }
#password-criteria li.invalid::before { content: '❌ '; } */
/*
.form-control.is-invalid { border-color: red; }
*/