/**
 * Dashboard Calendar JavaScript
 * Handles calendar rendering, task management, and API interactions
 * 
 * Backend Integration Points:
 * - GET /api/tasks - Fetch all tasks for the current user
 * - POST /api/tasks - Create a new task
 * 
 * Task object structure:
 * { id, title, description, due_date (ISO string), status }
 */

class CalendarDashboard {
    constructor() {
        this.currentDate = new Date();
        this.tasks = new Map(); // Map of date strings to task arrays
        this.selectedDate = null;

        this.initializeElements();
        this.attachEventListeners();
        this.loadTasks();
        this.renderCalendar();
    }

    initializeElements() {
        // Calendar elements
        this.monthTitle = document.getElementById('monthTitle');
        this.prevMonthBtn = document.getElementById('prevMonth');
        this.nextMonthBtn = document.getElementById('nextMonth');
        this.calendarGrid = document.querySelector('.calendar-grid');
        this.addTaskBtn = document.getElementById('addTaskBtn');

        // Modal elements
        this.modal = document.getElementById('taskModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalClose = document.getElementById('modalClose');
        this.existingTasks = document.getElementById('existingTasks');
        this.tasksList = document.getElementById('tasksList');

        // Form elements
        this.taskForm = document.getElementById('taskForm');
        this.taskTitle = document.getElementById('taskTitle');
        this.taskDescription = document.getElementById('taskDescription');
        this.taskDueDate = document.getElementById('taskDueDate');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.saveBtn = document.getElementById('saveBtn');

        // Error elements
        this.formError = document.getElementById('formError');
        this.titleError = document.getElementById('titleError');
        this.dateError = document.getElementById('dateError');
    }

    attachEventListeners() {
        // Calendar navigation
        this.prevMonthBtn.addEventListener('click', () => this.navigateMonth(-1));
        this.nextMonthBtn.addEventListener('click', () => this.navigateMonth(1));

        // Add task button
        this.addTaskBtn.addEventListener('click', () => this.openModal());

        // Modal controls
        this.modalClose.addEventListener('click', () => this.closeModal());
        this.cancelBtn.addEventListener('click', () => this.closeModal());

        // Form submission
        this.taskForm.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Modal overlay click to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Keyboard accessibility
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display !== 'none') {
                this.closeModal();
            }
        });
    }

    /**
     * Load tasks from the backend API
     * Endpoint: GET /api/tasks
     * Expected response: Array of task objects
     */
    async loadTasks() {
        try {
            const response = await fetch('/api/tasks', {
                method: 'GET',
                credentials: 'same-origin' // Include session cookies
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const tasks = await response.json();

            // Group tasks by due date (YYYY-MM-DD format)
            this.tasks.clear();
            tasks.forEach(task => {
                const dueDate = this.formatDateForKey(task.due_date);
                if (!this.tasks.has(dueDate)) {
                    this.tasks.set(dueDate, []);
                }
                this.tasks.get(dueDate).push(task);
            });

            // Re-render calendar to show task indicators
            this.renderCalendar();

        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showError('Failed to load tasks. Please refresh the page.');
        }
    }

    /**
     * Create a new task via the backend API
     * Endpoint: POST /api/tasks
     * Expected payload: { title, description, due_date }
     */
    async createTask(taskData) {
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const newTask = await response.json();

            // Add task to local cache
            const dateKey = this.formatDateForKey(newTask.due_date);
            if (!this.tasks.has(dateKey)) {
                this.tasks.set(dateKey, []);
            }
            this.tasks.get(dateKey).push(newTask);

            // Update calendar display
            this.renderCalendar();
            this.closeModal();

            // Show success feedback (optional)
            this.showSuccess('Task created successfully!');

        } catch (error) {
            console.error('Error creating task:', error);
            this.showError(error.message || 'Failed to create task. Please try again.');
        }
    }
    // Add these methods to your dashboard.js class

    /**
     * Delete a task via API
     */
    async deleteTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error('Failed to delete task');
            }

            // Remove from local cache
            this.removeTaskFromCache(taskId);

            // Update calendar display
            this.renderCalendar();

            // Update modal if open
            if (this.selectedDate) {
                const dayTasks = this.tasks.get(this.formatDateForKey(this.selectedDate)) || [];
                this.renderTasksList(dayTasks);
            }

            this.showSuccess('Task deleted successfully!');

        } catch (error) {
            console.error('Error deleting task:', error);
            this.showError('Failed to delete task. Please try again.');
        }
    }

    /**
     * Update task status via API
     */
    async updateTaskStatus(taskId, status) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });

            if (!response.ok) {
                throw new Error('Failed to update task');
            }

            const updatedTask = await response.json();

            // Update local cache
            this.updateTaskInCache(updatedTask);

            // Update calendar display
            this.renderCalendar();

            // Update modal if open
            if (this.selectedDate) {
                const dayTasks = this.tasks.get(this.formatDateForKey(this.selectedDate)) || [];
                this.renderTasksList(dayTasks);
            }

            this.showSuccess('Task updated successfully!');

        } catch (error) {
            console.error('Error updating task:', error);
            this.showError('Failed to update task. Please try again.');
        }
    }

    /**
     * Remove task from local cache
     */
    removeTaskFromCache(taskId) {
        for (let [dateKey, tasks] of this.tasks.entries()) {
            const taskIndex = tasks.findIndex(task => task.id === taskId);
            if (taskIndex !== -1) {
                tasks.splice(taskIndex, 1);
                if (tasks.length === 0) {
                    this.tasks.delete(dateKey);
                }
                break;
            }
        }
    }

    /**
     * Update task in local cache
     */
    updateTaskInCache(updatedTask) {
        const dateKey = this.formatDateForKey(updatedTask.due_date);
        const tasks = this.tasks.get(dateKey) || [];
        const taskIndex = tasks.findIndex(task => task.id === updatedTask.id);

        if (taskIndex !== -1) {
            tasks[taskIndex] = updatedTask;
        }
    }

    /**
     * Check if complete button should be shown
     */
    shouldShowCompleteButton(taskDueDate) {
        const today = new Date();
        const todayStr = this.formatDateString(today.getFullYear(), today.getMonth(), today.getDate());
        const dueDateStr = this.formatDateForKey(taskDueDate);

        // Show for today or past dates only
        return dueDateStr <= todayStr;
    }

    /**
     * Updated renderTasksList method with buttons
     */
    /**
 * Updated renderTasksList method with buttons
 */
renderTasksList(tasks) {
    this.tasksList.innerHTML = '';
    
    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        
        const showCompleteBtn = this.shouldShowCompleteButton(task.due_date);
        const isCompleted = task.status === 'completed';
        
        taskItem.innerHTML = `
            <div class="task-content">
                <div class="task-title ${isCompleted ? 'completed' : ''}">${this.escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${this.escapeHtml(task.description)}</div>` : ''}
                <div class="task-status status-${task.status}">${this.escapeHtml(task.status)}</div>
            </div>
            <div class="task-actions">
                ${showCompleteBtn && !isCompleted ? `
                    <button class="btn-complete" data-task-id="${task.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 6L9 17l-5-5"/>
                        </svg>
                        Complete
                    </button>
                ` : ''}
                <button class="btn-delete" data-task-id="${task.id}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18m-2 0v14c0 2-1 3-3 3H8c-2 0-3-1-3-3V6m3 0V4c0-1 1-2 2-2h4c0 1 1 2V6"/>
                    </svg>
                    Delete
                </button>
            </div>
        `;
        
        this.tasksList.appendChild(taskItem);
    });
    
    // Add event listeners for buttons
    this.tasksList.querySelectorAll('.btn-complete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.closest('.btn-complete').dataset.taskId);
            this.updateTaskStatus(taskId, 'completed');
        });
    });
    
    this.tasksList.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.closest('.btn-delete').dataset.taskId);
            if (confirm('Are you sure you want to delete this task?')) {
                this.deleteTask(taskId);
            }
        });
    });
}


    navigateMonth(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        this.renderCalendar();
    }

    renderCalendar() {
        // Update month title
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        const monthYear = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
        this.monthTitle.textContent = monthYear;

        // Get first day of month and number of days
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        // Clear existing day cells (keep headers)
        const dayCells = this.calendarGrid.querySelectorAll('.day-cell');
        dayCells.forEach(cell => cell.remove());

        // Calculate days to show from previous month
        const prevMonth = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 0);
        const daysInPrevMonth = prevMonth.getDate();

        // Generate calendar grid
        let dayCount = 1;
        let nextMonthDay = 1;

        // Generate 6 weeks (42 days) to ensure consistent calendar size
        for (let week = 0; week < 6; week++) {
            for (let day = 0; day < 7; day++) {
                const cellIndex = week * 7 + day;
                const dayCell = this.createDayCell();

                if (cellIndex < startingDayOfWeek) {
                    // Previous month days
                    const dayNum = daysInPrevMonth - startingDayOfWeek + cellIndex + 1;
                    this.populateDayCell(dayCell, dayNum, 'prev', this.currentDate.getMonth() - 1, this.currentDate.getFullYear());
                } else if (dayCount <= daysInMonth) {
                    // Current month days
                    this.populateDayCell(dayCell, dayCount, 'current', this.currentDate.getMonth(), this.currentDate.getFullYear());
                    dayCount++;
                } else {
                    // Next month days
                    this.populateDayCell(dayCell, nextMonthDay, 'next', this.currentDate.getMonth() + 1, this.currentDate.getFullYear());
                    nextMonthDay++;
                }

                this.calendarGrid.appendChild(dayCell);
            }
        }
    }

    createDayCell() {
        const dayCell = document.createElement('div');
        dayCell.className = 'day-cell';
        dayCell.setAttribute('role', 'button');
        dayCell.setAttribute('tabindex', '0');

        // Keyboard accessibility
        dayCell.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                dayCell.click();
            }
        });

        return dayCell;
    }

    populateDayCell(dayCell, dayNum, monthType, month, year) {
        // Adjust month and year for prev/next month calculations
        let adjustedMonth = month;
        let adjustedYear = year;

        if (monthType === 'prev' && month < 0) {
            adjustedMonth = 11;
            adjustedYear = year - 1;
        } else if (monthType === 'next' && month > 11) {
            adjustedMonth = 0;
            adjustedYear = year + 1;
        }

        const dateStr = this.formatDateString(adjustedYear, adjustedMonth, dayNum);
        const dateKey = this.formatDateForKey(dateStr);

        // Add day number
        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = dayNum;
        dayCell.appendChild(dayNumber);

        // Check if this day has tasks
        const dayTasks = this.tasks.get(dateKey) || [];
        if (dayTasks.length > 0) {
            dayCell.classList.add('has-tasks');

            const taskCount = document.createElement('div');
            taskCount.className = 'task-count';
            taskCount.textContent = `${dayTasks.length} task${dayTasks.length > 1 ? 's' : ''}`;
            dayCell.appendChild(taskCount);
        }

        // Style other month days
        if (monthType !== 'current') {
            dayCell.classList.add('other-month');
        }

        // Add click handler
        dayCell.addEventListener('click', () => this.handleDayClick(dateStr, dayTasks));

        // Add aria-label for accessibility
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];
        dayCell.setAttribute('aria-label',
            `${monthNames[adjustedMonth]} ${dayNum}, ${adjustedYear}${dayTasks.length > 0 ? ` - ${dayTasks.length} task${dayTasks.length > 1 ? 's' : ''}` : ''}`
        );
    }

    handleDayClick(dateStr, dayTasks) {
        this.selectedDate = dateStr;
        this.openModal(dateStr, dayTasks);
    }

    openModal(dateStr = null, dayTasks = []) {
        // Set selected date to today if not specified
        if (!dateStr) {
            const today = new Date();
            dateStr = this.formatDateString(today.getFullYear(), today.getMonth(), today.getDate());
            dayTasks = this.tasks.get(this.formatDateForKey(dateStr)) || [];
        }

        this.selectedDate = dateStr;

        // Format date for display
        const date = new Date(dateStr);
        const formattedDate = date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        this.modalTitle.textContent = `Tasks for ${formattedDate}`;

        // Show existing tasks if any
        if (dayTasks.length > 0) {
            this.existingTasks.style.display = 'block';
            this.renderTasksList(dayTasks);
        } else {
            this.existingTasks.style.display = 'none';
        }

        // Pre-fill the due date
        this.taskDueDate.value = this.formatDateForInput(dateStr);

        // Clear form
        this.taskForm.reset();
        this.taskDueDate.value = this.formatDateForInput(dateStr);
        this.clearErrors();

        // Show modal
        this.modal.style.display = 'flex';

        // Focus on title input
        setTimeout(() => {
            this.taskTitle.focus();
        }, 100);
    }

    closeModal() {
        this.modal.style.display = 'none';
        this.selectedDate = null;
        this.clearErrors();
        this.taskForm.reset();
    }

    // renderTasksList(tasks) {
    //     this.tasksList.innerHTML = '';

    //     tasks.forEach(task => {
    //         const taskItem = document.createElement('div');
    //         taskItem.className = 'task-item';

    //         taskItem.innerHTML = `
    //             <div class="task-title">${this.escapeHtml(task.title)}</div>
    //             ${task.description ? `<div class="task-description">${this.escapeHtml(task.description)}</div>` : ''}
    //             <div class="task-status">${this.escapeHtml(task.status)}</div>
    //         `;

    //         this.tasksList.appendChild(taskItem);
    //     });
    // }

    async handleFormSubmit(e) {
        e.preventDefault();

        // Clear previous errors
        this.clearErrors();

        // Get form data
        const formData = new FormData(this.taskForm);
        const title = formData.get('title').trim();
        const description = formData.get('description').trim();
        const dueDate = formData.get('due_date');

        // Validate form
        let hasErrors = false;

        if (!title) {
            this.showFieldError('titleError', 'Title is required');
            hasErrors = true;
        }

        if (!dueDate) {
            this.showFieldError('dateError', 'Due date is required');
            hasErrors = true;
        }

        if (hasErrors) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        // Create task data
        const taskData = {
            title,
            description: description || undefined,
            due_date: dueDate // Backend expects YYYY-MM-DD format
        };

        // Submit to backend
        await this.createTask(taskData);

        // Reset loading state
        this.setLoadingState(false);
    }

    setLoadingState(loading) {
        const btnText = this.saveBtn.querySelector('.btn-text');
        const btnSpinner = this.saveBtn.querySelector('.btn-spinner');

        if (loading) {
            btnText.style.display = 'none';
            btnSpinner.style.display = 'block';
            this.saveBtn.disabled = true;
        } else {
            btnText.style.display = 'block';
            btnSpinner.style.display = 'none';
            this.saveBtn.disabled = false;
        }
    }

    // Utility methods
    formatDateString(year, month, day) {
        return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    }

    formatDateForKey(dateStr) {
        // Handle both ISO datetime strings and date-only strings
        if (dateStr.includes('T')) {
            return dateStr.split('T')[0]; // Extract date part from ISO string
        }
        return dateStr;
    }

    formatDateForInput(dateStr) {
        // Ensure format is YYYY-MM-DD for date input
        return this.formatDateForKey(dateStr);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    clearErrors() {
        document.querySelectorAll('.error-message').forEach(error => {
            error.classList.remove('show');
            error.textContent = '';
        });
    }

    showFieldError(fieldId, message) {
        const errorElement = document.getElementById(fieldId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }

    showError(message) {
        this.formError.textContent = message;
        this.formError.classList.add('show');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.formError.classList.remove('show');
        }, 5000);
    }

    showSuccess(message) {
        // Create temporary success message
        const successEl = document.createElement('div');
        successEl.className = 'success-message';
        successEl.textContent = message;
        successEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10B981;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 1001;
            font-weight: 500;
        `;

        document.body.appendChild(successEl);

        // Remove after 3 seconds
        setTimeout(() => {
            if (successEl.parentNode) {
                successEl.parentNode.removeChild(successEl);
            }
        }, 3000);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CalendarDashboard();
});