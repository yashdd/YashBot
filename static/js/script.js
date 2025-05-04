document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const uploadForm = document.getElementById('upload-form');
    const documentUpload = document.getElementById('document-upload');
    const uploadStatus = document.getElementById('upload-status');
    const documentList = document.getElementById('document-list');
    const websiteForm = document.getElementById('website-form');
    const websiteUrl = document.getElementById('website-url');
    const maxPages = document.getElementById('max-pages');
    const maxDepth = document.getElementById('max-depth');
    const websiteStatus = document.getElementById('website-status');
    const websiteList = document.getElementById('website-list');
    
    // Track uploaded documents and processed websites
    let uploadedDocuments = [];
    let processedWebsites = [];
    
    // Initialize
    scrollToBottom();
    
    // Event Listeners
    chatForm.addEventListener('submit', handleChatSubmit);
    uploadForm.addEventListener('submit', handleFileUpload);
    websiteForm.addEventListener('submit', handleWebsiteProcess);
    
    // Chat functionality
    function handleChatSubmit(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add bot response to chat
            addMessageToChat('bot', data.response, data.sources);
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessageToChat('system', 'Sorry, there was an error processing your request.');
        });
    }
    
    function addMessageToChat(sender, content, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMessageContent(content);
        messageDiv.appendChild(contentDiv);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            
            const sourcesText = document.createElement('small');
            sourcesText.textContent = 'Sources:';
            sourcesDiv.appendChild(sourcesText);
            
            const sourcesList = document.createElement('ul');
            sources.forEach(source => {
                const sourceItem = document.createElement('li');
                sourceItem.textContent = source;
                sourcesList.appendChild(sourceItem);
            });
            sourcesDiv.appendChild(sourcesList);
            messageDiv.appendChild(sourcesDiv);
        }
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function formatMessageContent(content) {
        // Convert URLs to links
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Convert line breaks to <br>
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // File upload functionality
    function handleFileUpload(e) {
        e.preventDefault();
        
        const files = documentUpload.files;
        if (files.length === 0) {
            showUploadStatus('Please select files to upload', 'warning');
            return;
        }
        
        // Create FormData
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        // Show upload in progress
        showUploadStatus('Uploading...', 'info');
        
        // Create progress element
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress';
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated upload-progress';
        progressBar.style.width = '100%';
        progressContainer.appendChild(progressBar);
        uploadStatus.appendChild(progressContainer);
        
        // Upload files
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Handle successful upload
            showUploadStatus(`Successfully processed ${data.files.length} document(s)`, 'success');
            
            // Add uploaded files to the list
            data.files.forEach(file => {
                if (!uploadedDocuments.includes(file)) {
                    uploadedDocuments.push(file);
                    addDocumentToList(file);
                }
            });
            
            // Clear file input
            documentUpload.value = '';
            
            // Add system message to chat
            addMessageToChat('system', `Added ${data.files.length} document(s) to my knowledge base. I can now answer questions about these documents.`);
        })
        .catch(error => {
            console.error('Error:', error);
            showUploadStatus('Error uploading files. Please try again.', 'danger');
        });
    }
    
    function showUploadStatus(message, type) {
        uploadStatus.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
    }
    
    function addDocumentToList(filename) {
        const item = document.createElement('li');
        item.className = 'list-group-item';
        
        // Get icon based on file extension
        const icon = getFileIcon(filename);
        
        item.innerHTML = `
            <span><i class="${icon} document-icon"></i>${filename}</span>
        `;
        
        documentList.appendChild(item);
    }
    
    function getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        
        switch (ext) {
            case 'pdf':
                return 'fas fa-file-pdf';
            case 'doc':
            case 'docx':
                return 'fas fa-file-word';
            case 'xls':
            case 'xlsx':
                return 'fas fa-file-excel';
            case 'ppt':
            case 'pptx':
                return 'fas fa-file-powerpoint';
            case 'txt':
                return 'fas fa-file-alt';
            case 'csv':
                return 'fas fa-file-csv';
            default:
                return 'fas fa-file';
        }
    }
    
    // Website processing functionality
    function handleWebsiteProcess(e) {
        e.preventDefault();
        
        const url = websiteUrl.value.trim();
        if (!url) {
            showWebsiteStatus('Please enter a website URL', 'warning');
            return;
        }
        
        // Prepare request data
        const requestData = {
            url: url,
            max_pages: parseInt(maxPages.value) || 5,
            max_depth: parseInt(maxDepth.value) || 1
        };
        
        // Show processing in progress
        showWebsiteStatus('Processing website...', 'info');
        
        // Create progress element
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress';
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated website-progress';
        progressBar.style.width = '100%';
        progressContainer.appendChild(progressBar);
        websiteStatus.appendChild(progressContainer);
        
        // Process website
        fetch('/process-website', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Handle successful processing
            showWebsiteStatus(`Successfully processed website with ${data.chunks_created} content chunks from ${data.pages_processed} pages`, 'success');
            
            // Add processed website to the list
            if (!processedWebsites.includes(data.url)) {
                processedWebsites.push(data.url);
                addWebsiteToList(data.url, data.pages_processed);
            }
            
            // Clear URL input (but keep settings)
            websiteUrl.value = '';
            
            // Add system message to chat
            addMessageToChat('system', `Added content from ${data.url} to my knowledge base. I can now answer questions about this website.`);
        })
        .catch(error => {
            console.error('Error:', error);
            showWebsiteStatus('Error processing website. Please check the URL and try again.', 'danger');
        });
    }
    
    function showWebsiteStatus(message, type) {
        websiteStatus.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
    }
    
    function addWebsiteToList(url, pageCount) {
        const item = document.createElement('li');
        item.className = 'list-group-item';
        
        // Truncate URL if too long
        let displayUrl = url;
        if (displayUrl.length > 40) {
            displayUrl = displayUrl.substring(0, 37) + '...';
        }
        
        item.innerHTML = `
            <div>
                <span><i class="fas fa-globe website-icon"></i> 
                <a href="${url}" target="_blank">${displayUrl}</a></span>
                <span class="badge bg-primary ms-2">${pageCount} pages</span>
            </div>
        `;
        
        websiteList.appendChild(item);
    }
});
