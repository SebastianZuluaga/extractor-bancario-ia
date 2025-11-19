document.addEventListener('DOMContentLoaded', () => {
    // --- NAVIGATION ---
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            views.forEach(view => view.classList.remove('active'));

            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // --- API KEY PERSISTENCE ---
    const apiKeyInput = document.getElementById('api-key');
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) apiKeyInput.value = savedKey;

    apiKeyInput.addEventListener('change', () => {
        localStorage.setItem('gemini_api_key', apiKeyInput.value);
    });

    // --- GOALS MANAGEMENT ---
    let goals = JSON.parse(localStorage.getItem('user_goals')) || [];
    const goalsList = document.getElementById('goals-list');
    const goalModal = document.getElementById('goal-modal');
    const addGoalBtn = document.getElementById('add-goal-btn');
    const cancelGoalBtn = document.getElementById('cancel-goal');
    const saveGoalBtn = document.getElementById('save-goal');

    function renderGoals() {
        goalsList.innerHTML = '';
        if (goals.length === 0) {
            goalsList.innerHTML = '<div class="empty-state-small">No goals set. Click + to add one.</div>';
            return;
        }

        goals.forEach((goal, index) => {
            const percent = Math.min((goal.current / goal.target) * 100, 100);
            const html = `
                <div class="goal-item">
                    <div class="goal-info">
                        <span style="font-weight:600">${goal.name}</span>
                        <span>${formatCurrency(goal.current)} / ${formatCurrency(goal.target)}</span>
                    </div>
                    <div class="goal-progress-bg">
                        <div class="goal-progress-fill" style="width: ${percent}%"></div>
                    </div>
                </div>
            `;
            goalsList.insertAdjacentHTML('beforeend', html);
        });
    }

    addGoalBtn.addEventListener('click', () => {
        document.getElementById('goal-name').value = '';
        document.getElementById('goal-target').value = '';
        document.getElementById('goal-current').value = '';
        goalModal.classList.remove('hidden');
    });

    cancelGoalBtn.addEventListener('click', () => goalModal.classList.add('hidden'));

    saveGoalBtn.addEventListener('click', () => {
        const name = document.getElementById('goal-name').value;
        const target = parseFloat(document.getElementById('goal-target').value);
        const current = parseFloat(document.getElementById('goal-current').value);

        if (name && target) {
            goals.push({ name, target, current: current || 0 });
            localStorage.setItem('user_goals', JSON.stringify(goals));
            renderGoals();
            goalModal.classList.add('hidden');
        } else {
            alert('Please fill in at least Name and Target.');
        }
    });

    // Initial Render
    renderGoals();
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

    // --- CHART INITIALIZATION ---
    let spendingChart = null;

    function initChart(categories) {
        const ctx = document.getElementById('spendingChart').getContext('2d');

        if (spendingChart) spendingChart.destroy();

        const labels = categories.map(c => c.name);
        const data = categories.map(c => c.spent);

        spendingChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#00f0ff', '#10b981', '#ef4444', '#8b5cf6', '#f59e0b', '#ec4899'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#9ca3af' }
                    }
                }
            }
        });
    }

    // --- FILE UPLOAD & PROCESSING ---
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const passwordInput = document.getElementById('pdf-password');
    const loader = document.getElementById('loader-overlay');
    const dropZone = document.querySelector('.upload-area-large');
    const fileListContainer = document.getElementById('file-list');

    let selectedFiles = [];

    // Click to browse
    dropZone.addEventListener('click', (e) => {
        // Don't trigger if clicking remove button or inputs
        if (e.target.closest('.file-remove') || e.target.closest('input') || e.target.closest('button')) return;
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

    // Drag & Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (!files.length) return;

        // Add new files to array
        for (let i = 0; i < files.length; i++) {
            if (files[i].type === 'application/pdf') {
                selectedFiles.push(files[i]);
            } else {
                alert(`File ${files[i].name} is not a PDF.`);
            }
        }
        renderFileList();
    }

    function renderFileList() {
        fileListContainer.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const div = document.createElement('div');
            div.className = 'file-item';
            div.innerHTML = `
                <span>${file.name}</span>
                <span class="file-remove" data-index="${index}">✕</span>
            `;
            fileListContainer.appendChild(div);
        });

        // Add remove listeners
        document.querySelectorAll('.file-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering file input
                const index = parseInt(e.target.getAttribute('data-index'));
                selectedFiles.splice(index, 1);
                renderFileList();
            });
        });

        // Update button text
        uploadBtn.textContent = selectedFiles.length > 0 ? `Process ${selectedFiles.length} Statement(s)` : 'Process Statements';
    }

    // Process Button Click
    uploadBtn.addEventListener('click', async (e) => {
        e.stopPropagation(); // Prevent bubbling

        if (selectedFiles.length === 0) {
            alert('Please select or drop PDF files first.');
            return;
        }

        if (!apiKeyInput.value) {
            alert('Please enter your Gemini API Key');
            return;
        }

        const formData = new FormData();
        for (const file of selectedFiles) {
            formData.append('files', file);
        }

        formData.append('gemini_api_key', apiKeyInput.value);
        if (passwordInput.value) {
            formData.append('password', passwordInput.value);
        }

        loader.classList.remove('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Analysis failed');

            const data = await response.json();
            updateDashboard(data);

            // Clear files after success
            selectedFiles = [];
            renderFileList();

            // Switch to Dashboard
            document.querySelector('[data-target="view-dashboard"]').click();

        } catch (error) {
            console.error('Error:', error);
            alert('Error processing files. Check API Key or file format.');
        } finally {
            loader.classList.add('hidden');
            fileInput.value = '';
        }
    });

    function updateDashboard(data) {
        // Update Cards
        document.getElementById('total-balance').textContent = formatCurrency(data.total_balance);
        document.getElementById('monthly-income').textContent = formatCurrency(data.monthly_income);
        document.getElementById('monthly-expenses').textContent = formatCurrency(data.monthly_expenses);

        // Update Chart
        if (data.categories) {
            initChart(data.categories);
        }

        // Update AI Content
        const aiContent = document.getElementById('ai-content');
        if (data.recommendations) {
            // Format the AI text (convert newlines to breaks)
            let html = `
                <div style="margin-bottom: 20px;">
                    <h4 style="color:var(--accent-cyan); margin-bottom:8px;">💡 Key Insights</h4>
                    <p>${data.recommendations.tip}</p>
                </div>
                <div>
                    <h4 style="color:var(--accent-green); margin-bottom:8px;">🚀 Action Plan</h4>
                    <p>${data.recommendations.advice}</p>
                </div>
            `;
            aiContent.innerHTML = html;
        }
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(value);
    }
});
