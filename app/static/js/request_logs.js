document.addEventListener("DOMContentLoaded", function () {
    const state = {
        currentPage: 1,
        pageSize: 15,
        sortBy: 'id',
        sortOrder: 'desc',
        filters: {}
    };

    const dom = {
        tableBody: document.getElementById('requestLogsTable'),
        loadingIndicator: document.getElementById('loadingIndicator'),
        noDataMessage: document.getElementById('noDataMessage'),
        errorMessage: document.getElementById('errorMessage'),
        pagination: document.getElementById('pagination'),
        pageInput: document.getElementById('pageInput'),
        goToPageBtn: document.getElementById('goToPageBtn'),
        pageSizeSelector: document.getElementById('pageSize'),
        searchBtn: document.getElementById('searchBtn'),
        apiTypeSearch: document.getElementById('apiTypeSearch'),
        modelNameSearch: document.getElementById('modelNameSearch'),
        keySearch: document.getElementById('keySearch'),
        statusCodeSearch: document.getElementById('statusCodeSearch'),
        logDetailModal: document.getElementById('logDetailModal'),
        closeModalBtns: document.querySelectorAll('#closeLogDetailModalBtn, #closeModalFooterBtn'),
        modalRequestBody: document.getElementById('modalRequestBody'),
        modalResponseBody: document.getElementById('modalResponseBody'),
    };

    async function fetchLogs() {
        showLoading(true);
        const params = new URLSearchParams({
            page: state.currentPage,
            limit: state.pageSize,
            sort_by: state.sortBy,
            sort_order: state.sortOrder,
            ...state.filters
        });

        try {
            const response = await fetch(`/api/request-logs?${params}`);
            if (response.status === 401) {
                window.location.href = '/'; // Redirect to login page
                return;
            }
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            renderTable(data.logs);
            renderPagination(data.total_count);
        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    }

    function renderTable(logs) {
        dom.tableBody.innerHTML = '';
        if (!logs || logs.length === 0) {
            showNoData(true);
            return;
        }
        showNoData(false);

        logs.forEach(log => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            const successClass = log.is_success ? 'status-success' : 'status-failure';
            const successIcon = log.is_success ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>';

            row.innerHTML = `
                <td class="px-5 py-3">${log.id}</td>
                <td class="px-5 py-3">${log.ip_address || 'N/A'}</td>
                <td class="px-5 py-3">${log.api_type}</td>
                <td class="px-5 py-3">${log.model_name}</td>
                <td class="px-5 py-3" title="${log.api_key}">${log.api_key ? `${log.api_key.substring(0, 4)}...${log.api_key.substring(log.api_key.length - 4)}` : 'N/A'}</td>
                <td class="px-5 py-3 text-center ${successClass}">${successIcon}</td>
                <td class="px-5 py-3 text-center">${log.status_code || 'N/A'}</td>
                <td class="px-5 py-3">${log.latency_ms}</td>
                <td class="px-5 py-3">${new Date(log.created_at).toLocaleString()}</td>
                <td class="px-5 py-3 text-center">
                    <button class="btn-view-details bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs" data-log-id="${log.id}">Details</button>
                </td>
            `;
            dom.tableBody.appendChild(row);
        });

        document.querySelectorAll('.btn-view-details').forEach(button => {
            button.addEventListener('click', () => showLogDetails(button.dataset.logId));
        });
    }

    function renderPagination(totalCount) {
        const totalPages = Math.ceil(totalCount / state.pageSize);
        dom.pagination.innerHTML = '';
        if (totalPages <= 1) return;

        const createPageLink = (page, text = page, isActive = false, isDisabled = false) => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.innerHTML = text;
            a.className = `px-3 py-1 rounded-md text-sm ${isActive ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'} ${isDisabled ? 'cursor-not-allowed opacity-50' : ''}`;
            if (!isDisabled) {
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    state.currentPage = page;
                    fetchLogs();
                });
            }
            li.appendChild(a);
            return li;
        };

        // Previous button
        dom.pagination.appendChild(createPageLink(state.currentPage - 1, '&laquo;', false, state.currentPage === 1));

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === state.currentPage || Math.abs(i - state.currentPage) < 2 || i === 1 || i === totalPages) {
                dom.pagination.appendChild(createPageLink(i, i, i === state.currentPage));
            } else if (Math.abs(i - state.currentPage) === 2) {
                 dom.pagination.appendChild(createPageLink(i, '...', false, true));
            }
        }

        // Next button
        dom.pagination.appendChild(createPageLink(state.currentPage + 1, '&raquo;', false, state.currentPage === totalPages));
    }

    async function showLogDetails(logId) {
        try {
            const response = await fetch(`/api/request-logs/${logId}`);
            if (!response.ok) throw new Error('Failed to fetch log details.');
            const details = await response.json();

            let requestBody = 'N/A';
            try {
                requestBody = JSON.stringify(JSON.parse(details.request_body), null, 2);
            } catch (e) {
                requestBody = details.request_body;
            }

            let responseBody = 'N/A';
            try {
                responseBody = JSON.stringify(JSON.parse(details.response_body), null, 2);
            } catch (e) {
                responseBody = details.response_body;
            }

            dom.modalRequestBody.textContent = requestBody;
            dom.modalResponseBody.textContent = responseBody;
            dom.logDetailModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        } catch (error) {
            showError(error.message);
        }
    }

    function closeLogDetailModal() {
        dom.logDetailModal.classList.remove('show');
        document.body.style.overflow = '';
    }

    function showLoading(isLoading) {
        dom.loadingIndicator.style.display = isLoading ? 'flex' : 'none';
        if (isLoading) {
            dom.tableBody.innerHTML = '';
            showNoData(false);
            showError(false);
        }
    }

    function showNoData(isNoData) {
        dom.noDataMessage.style.display = isNoData ? 'block' : 'none';
    }

    function showError(message) {
        dom.errorMessage.textContent = message;
        dom.errorMessage.style.display = message ? 'block' : 'none';
    }

    // Event Listeners
    dom.searchBtn.addEventListener('click', () => {
        state.currentPage = 1;
        state.filters = {
            api_type_search: dom.apiTypeSearch.value,
            model_name_search: dom.modelNameSearch.value,
            key_search: dom.keySearch.value,
            status_code_search: dom.statusCodeSearch.value
        };
        fetchLogs();
    });

    dom.pageSizeSelector.addEventListener('change', (e) => {
        state.pageSize = parseInt(e.target.value);
        state.currentPage = 1;
        fetchLogs();
    });

    dom.goToPageBtn.addEventListener('click', () => {
        const page = parseInt(dom.pageInput.value);
        if (page > 0) {
            state.currentPage = page;
            fetchLogs();
        }
    });

    dom.closeModalBtns.forEach(btn => btn.addEventListener('click', closeLogDetailModal));
    dom.logDetailModal.addEventListener('click', (e) => {
        if (e.target === dom.logDetailModal) closeLogDetailModal();
    });

    // Initial Load
    fetchLogs();
});
