document.addEventListener('DOMContentLoaded', () => {
  const proxyList = document.getElementById('proxy-list');
  const addProxyBtn = document.getElementById('add-proxy-btn');
  const proxyInput = document.getElementById('proxy-input');

  const fetchProxies = async () => {
    try {
      const response = await fetch('/api/proxies');
      if (!response.ok) {
        throw new Error('Failed to fetch proxies');
      }
      const proxies = await response.json();
      renderProxies(proxies);
    } catch (error) {
      console.error('Error fetching proxies:', error);
      showNotification('Failed to load proxies.', 'error');
    }
  };

  const renderProxies = (proxies) => {
    proxyList.innerHTML = '';
    if (proxies.length === 0) {
      proxyList.innerHTML = '<tr><td colspan="4" class="text-center py-4">No proxies found.</td></tr>';
      return;
    }
    proxies.forEach(proxy => {
      const tr = document.createElement('tr');
      tr.className = 'proxy-list-enter-active';
      tr.innerHTML = `
        <td class="border-b px-4 py-2">${proxy.url}</td>
        <td class="border-b px-4 py-2">${proxy.status || 'Not checked'}</td>
        <td class="border-b px-4 py-2">${proxy.last_checked ? new Date(proxy.last_checked).toLocaleString() : 'N/A'}</td>
        <td class="border-b px-4 py-2 text-right">
          <button class="test-proxy-btn bg-blue-500 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-600 transition-colors" data-url="${proxy.url}">Test</button>
          <button class="delete-proxy-btn bg-red-500 text-white px-3 py-1 rounded-md text-sm hover:bg-red-600 transition-colors" data-id="${proxy.id}">Delete</button>
        </td>
      `;
      proxyList.appendChild(tr);
    });
  };

  const addProxies = async () => {
    const proxies = proxyInput.value.split('\n').map(p => p.trim()).filter(p => p);
    if (proxies.length === 0) {
      showNotification('Please enter at least one proxy URL.', 'error');
      return;
    }

    try {
      const response = await fetch('/api/proxies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ proxies }),
      });
      if (!response.ok) {
        throw new Error('Failed to add proxies');
      }
      const result = await response.json();
      showNotification(result.message, 'success');
      proxyInput.value = '';
      fetchProxies();
    } catch (error) {
      console.error('Error adding proxies:', error);
      showNotification('Failed to add proxies.', 'error');
    }
  };

  const deleteProxy = async (proxyId) => {
    if (!confirm('Are you sure you want to delete this proxy?')) {
      return;
    }

    try {
      const response = await fetch(`/api/proxies/${proxyId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete proxy');
      }
      const result = await response.json();
      showNotification(result.message, 'success');
      fetchProxies();
    } catch (error) {
      console.error('Error deleting proxy:', error);
      showNotification('Failed to delete proxy.', 'error');
    }
  };

  const testProxy = async (proxyUrl) => {
    try {
      const response = await fetch('/api/proxies/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ proxy_url: proxyUrl }),
      });
      if (!response.ok) {
        throw new Error('Failed to test proxy');
      }
      const result = await response.json();
      let statusMessage = `Status: ${result.status}<br>Delay: ${result.delay_ms}ms`;
      if (result.error) {
        statusMessage += `<br>Error: ${result.error}`;
      }
      showNotification(statusMessage, result.status === 'active' ? 'success' : 'error');
      fetchProxies();
    } catch (error) {
      console.error('Error testing proxy:', error);
      showNotification('Failed to test proxy.', 'error');
    }
  };

  addProxyBtn.addEventListener('click', addProxies);

  proxyList.addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-proxy-btn')) {
      const proxyId = e.target.dataset.id;
      deleteProxy(proxyId);
    }
    if (e.target.classList.contains('test-proxy-btn')) {
      const proxyUrl = e.target.dataset.url;
      testProxy(proxyUrl);
    }
  });

  fetchProxies();
});
