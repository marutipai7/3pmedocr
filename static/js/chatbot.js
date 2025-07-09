document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const chatPopup = document.getElementById('chat-popup');
    const initialBotMessageElem = document.getElementById('initial-bot-message');
    const messageContainer = document.getElementById('message-container');
    const initialOptionsArea = document.getElementById('initial-options-area');
    const subOptionsArea = document.getElementById('sub-options-area');

    // --- Global State ---
    let currentBotContent = {}; 
    let currentOptions = []; 
    let isSubOptionsDisplayed = false; 

    // --- Main Functions ---
    // Toggles the visibility of the chatbot popup
    window.toggleChat = function() {
        if (chatPopup.classList.contains('hidden')) {
            chatPopup.classList.remove('hidden');
            // Always reset visibility state when opening
            initialOptionsArea.classList.remove('hidden');
            subOptionsArea.classList.add('hidden');
            isSubOptionsDisplayed = false;
            fetchBotContent();
        } else {
            chatPopup.classList.add('hidden'); // clear content when closing 
            messageContainer.innerHTML = '';
            initialBotMessageElem.textContent = '';
            clearOptions(initialOptionsArea);
            clearOptions(subOptionsArea);
            subOptionsArea.classList.add('hidden');
            initialOptionsArea.classList.remove('hidden');
            isSubOptionsDisplayed = false;
        }
    };

    // Fetches chatbot content from the Django API
    async function fetchBotContent() {
        try {
            messageContainer.innerHTML = '<div class="bot-message text-gray-500">Loading chat content...</div>';
            clearOptions(initialOptionsArea);
            clearOptions(subOptionsArea);
            subOptionsArea.classList.add('hidden');
            isSubOptionsDisplayed = false;

            const response = await fetch('/support/get-bot-content/', {
                method: 'GET', headers: {'Content-Type': 'application/json'},
            });

            // Remove loading message before displaying new content
            messageContainer.innerHTML = '';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.initial_message || `HTTP error! Status: ${response.status}`);
            }

            currentBotContent = await response.json();
            console.log('Fetched Bot Content:', currentBotContent);

            initialBotMessageElem.textContent = currentBotContent.initial_message || "How can I assist you?";
            currentOptions = currentBotContent.options || [];

            displayMessage(currentBotContent.initial_message, 'bot');
            displayOptions(currentOptions, initialOptionsArea);

        } catch (error) {
            // Remove loading message before showing error
            messageContainer.innerHTML = '';
            console.error('Error fetching bot content:', error);
            initialBotMessageElem.textContent = "Error loading chat.";
            displayMessage("Sorry, I'm having trouble loading content right now. Please try again later.", 'bot');
            displayOptions([{ label: "Reload", icon: "🔄", action: "reload" }], initialOptionsArea);
        }
    }

    // Displays a message in the chat history
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('p-2', 'rounded-lg', 'max-w-[75%]', 'my-2');

        if (sender === 'user') {
            messageDiv.classList.add('bg-violet-sky', 'text-white', 'ml-auto'); // User messages align right
        } else {
            messageDiv.classList.add('bg-gray-200', 'text-gray-800'); // Bot messages align left
        }

        messageDiv.textContent = message;
        messageContainer.appendChild(messageDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight; // Scroll to bottom
    }

    // Displays clickable options as buttons
    function displayOptions(options, container) {
        clearOptions(container); // Clear existing options first

        if (!options || options.length === 0) {
            if (isSubOptionsDisplayed) { 
                displayOptions([{ label: "Go Back", icon: "⬅️", action: "back_to_initial" }], container);
            } else {
                displayMessage("It seems there are no options available. Please contact support if you need help.", 'bot');
                displayOptions([{ label: "Contact Support", icon: "📞", action: "log_ticket_redirect", question: "Please describe your issue." }], container);
            }
            return;
        }

        options.forEach(option => {
            const button = document.createElement('button');
            button.classList.add(
                'bg-violet-sky', 'text-white', 'px-3', 'py-2', 'rounded-md',
                'hover:bg-violet-700', 'transition', 'duration-200', 'ease-in-out',
                'flex', 'items-center', 'gap-2', 'text-sm', 'text-left', 'flex-grow', 'sm:flex-grow-0'
            );
            
            // Add icon if present
            if (option.icon) {
                const iconSpan = document.createElement('span');
                iconSpan.classList.add('material-symbols-outlined');
                iconSpan.textContent = option.icon;
                button.appendChild(iconSpan);
            }
            
            button.innerHTML += option.label; 

            button.onclick = () => handleOptionClick(option);
            container.appendChild(button);
        });
        messageContainer.scrollTop = messageContainer.scrollHeight; 
    }

    // Clears all options from a specific container
    function clearOptions(container) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }

    // Handles the click event on an option button
    function handleOptionClick(option) {
        displayMessage(option.label, 'user'); 

        clearOptions(initialOptionsArea); 
        clearOptions(subOptionsArea);    

        subOptionsArea.classList.add('hidden');
        isSubOptionsDisplayed = false;

        switch (option.action) {
            case 'display_answer':
                displayMessage(option.answer, 'bot');
                displayOptions([
                    { label: "Go Back", icon: "⬅️", action: "reset_bot" }
                ], initialOptionsArea);
                initialOptionsArea.classList.remove('hidden');
                break;
            case 'reset_bot':
                messageContainer.innerHTML = '';
                initialBotMessageElem.textContent = '';
                clearOptions(initialOptionsArea);
                clearOptions(subOptionsArea);
                subOptionsArea.classList.add('hidden');
                initialOptionsArea.classList.remove('hidden');
                isSubOptionsDisplayed = false;
                fetchBotContent();
                break;

            case 'display_sub_options':
                displayMessage(option.question, 'bot'); 
                displayOptions(option.sub_options, subOptionsArea);
                initialOptionsArea.classList.add('hidden'); 
                subOptionsArea.classList.remove('hidden'); 
                isSubOptionsDisplayed = true;
                break;

            case 'redirect':
                displayMessage(`Redirecting you to: ${option.url}`, 'bot');
                setTimeout(() => window.location.href = option.url, 1000); // Redirect after a short delay
                break;

            case 'log_ticket_redirect':
                displayMessage(option.question || "Please describe your issue.", 'bot');
                setTimeout(() => {
                    alert("Redirecting to support ticket page.");
                    window.location.href = option.url || "support\templates\support.html";
                }, 1000);
                break;

            case 'back_to_initial':
                displayMessage("Okay, returning to main options.", 'bot');
                clearOptions(subOptionsArea);
                subOptionsArea.classList.add('hidden');
                initialOptionsArea.classList.remove('hidden');
                isSubOptionsDisplayed = false;
                displayOptions(currentOptions, initialOptionsArea); // Redisplay main options
                break;

            case 'reload':
                displayMessage("Reloading chat content...", 'bot');
                fetchBotContent();
                break;

            default:
                displayMessage("I'm sorry, I don't understand that option.", 'bot');
                // Fallback: Re-display current set of options or initial options
                if (isSubOptionsDisplayed) {
                    displayOptions(currentOptions.find(o => o.sub_options && o.label === option.parentLabel)?.sub_options || [], subOptionsArea);
                } else {
                    displayOptions(currentOptions, initialOptionsArea);
                }
                break;
        }
        messageContainer.scrollTop = messageContainer.scrollHeight; // Ensure scroll to bottom after action
    }

    // --- Initial Fetch on Page Load (Optional, but good for immediate display if chat is open by default) ---
    // If you want the chat to start with content immediately on page load (if open), uncomment:
    // fetchBotContent();
});