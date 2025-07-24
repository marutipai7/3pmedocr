document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const chatPopup = document.getElementById('chat-popup');
    const initialBotMessageElem = document.getElementById('initial-bot-message');
    const messageContainer = document.getElementById('message-container');
    const initialOptionsArea = document.getElementById('initial-options-area');
    const subOptionsArea = document.getElementById('sub-options-area');
    const startChatButton = document.getElementById('startChatButton');
    const customQueryInputArea = document.getElementById('custom-query-input-area');
    const customQueryTextarea = document.getElementById('custom-query-textarea');
    const ticketChatArea = document.getElementById('ticket-chat-area');
    const ticketChatMessages = document.getElementById('ticket-chat-messages');
    const ticketChatInput = document.getElementById('ticket-chat-input');
    const sendTicketMessageBtn = document.getElementById('send-ticket-message-btn');
    const backToTicketsBtn = document.getElementById('back-to-tickets-btn');


    // --- Global State ---
    let currentBotContent = {}; 
    let currentOptions = []; 
    let isSubOptionsDisplayed = false; 
    let currentOpenTicket = null;
 

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
            customQueryInputArea.classList.add('hidden');
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
        customQueryInputArea.classList.add('hidden');
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
                    window.location.href = option.url || "support.html";
                }, 1000);
                break;

            case 'back_to_initial':
                displayMessage("Okay, returning to main options.", 'bot');
                clearOptions(subOptionsArea);
                subOptionsArea.classList.add('hidden');
                initialOptionsArea.classList.remove('hidden');
                isSubOptionsDisplayed = false;
                displayOptions(currentOptions, initialOptionsArea); 
                break;

            case 'reload':
                displayMessage("Reloading chat content...", 'bot');
                fetchBotContent();
                break;

            case 'display_user_tickets':
                displayMessage(option.question || "Please wait while we fetch your tickets.", 'bot');
                clearOptions(initialOptionsArea);
                clearOptions(subOptionsArea);
                customQueryInputArea.classList.add('hidden');
                initialOptionsArea.classList.add('hidden');
                subOptionsArea.classList.add('hidden');

                fetchUserTickets(option.api_endpoint);
                break;

            case 'open_ticket_chat':
                currentOpenTicket = option.ticket_details;

                // Clear current display and messages
                clearOptions(initialOptionsArea);
                clearOptions(subOptionsArea);
                customQueryInputArea.classList.add('hidden');
                initialOptionsArea.classList.add('hidden');
                subOptionsArea.classList.add('hidden');
                ticketChatMessages.innerHTML = ''; 

                displayMessage(`**Ticket #${currentOpenTicket.ticket_id}** (Status: ${currentOpenTicket.status})`, 'bot');
                displayMessage(`*Description:* ${currentOpenTicket.description}`, 'bot');
                displayMessage("Chat history would load here if live chat were active.", 'bot'); 

                ticketChatArea.classList.remove('hidden');
                ticketChatInput.value = ''; 
                ticketChatInput.focus();
                break;

            default:
                displayMessage("I'm sorry, I don't understand that option.", 'bot');
                if (isSubOptionsDisplayed) {
                    displayOptions(currentOptions.find(o => o.sub_options && o.label === option.parentLabel)?.sub_options || [], subOptionsArea);
                } else {
                    displayOptions(currentOptions, initialOptionsArea);
                }
                break;
        }
        messageContainer.scrollTop = messageContainer.scrollHeight; // Ensure scroll to bottom after action
    }


     async function fetchUserTickets(apiEndpoint) {
        try {
            messageContainer.innerHTML = '<div class="bot-message text-gray-500">Loading your tickets...</div>';
            
            const response = await fetch(apiEndpoint, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
            });

            messageContainer.innerHTML = '';
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const tickets = data.tickets || [];

            if (tickets.length === 0) {
                displayMessage("You haven't raised any tickets yet.", 'bot');
                displayOptions([
                    { label: "Go Back", icon: "⬅️", action: "reset_bot" }
                ], initialOptionsArea);
                initialOptionsArea.classList.remove('hidden'); 
                return;
            }

            displayMessage("Here are your recent tickets:", 'bot');
            
            const ticketOptions = tickets.map(ticket => ({
                label: `Ticket #${ticket.ticket_id}: ${ticket.description.substring(0, 50)}${ticket.description.length > 50 ? '...' : ''} - Status: ${ticket.status}`,
                icon: '🎫', 
                action: 'open_ticket_chat', 
                ticket_details: ticket 
            }));

            displayOptions(ticketOptions, initialOptionsArea);
            initialOptionsArea.classList.remove('hidden'); 

        } catch (error) {
            messageContainer.innerHTML = ''; 
            console.error('Error fetching user tickets:', error);
            displayMessage("Sorry, I couldn't retrieve your tickets right now. Please try again later.", 'bot');
            displayOptions([
                { label: "Reload", icon: "🔄", action: "display_user_tickets", api_endpoint: apiEndpoint },
                { label: "Go Back", icon: "⬅️", action: "reset_bot" }
            ], initialOptionsArea);
            initialOptionsArea.classList.remove('hidden');
        }
        messageContainer.scrollTop = messageContainer.scrollHeight; 
    }
});