document.addEventListener('DOMContentLoaded', function() {
    // Handle transaction submission
    const txForm = document.getElementById('txForm');
    if (txForm) {
        txForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const rawTx = document.getElementById('rawTx').value;
            
            // Extract network from current URL path
            const pathParts = window.location.pathname.split('/').filter(p => p);
            const validNetworks = ['mainchain', 'testnetv3', 'testnetv4', 'signet'];
            const networkIndex = pathParts.findIndex(p => validNetworks.includes(p));
            const network = networkIndex !== -1 ? pathParts[networkIndex] : 'mainchain';
            
            try {
                const response = await fetch(`/${network}/transaction/submit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ raw_tx: rawTx }),
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                window.location.href = `/${network}/transaction/${result.txid}`;
            } catch (error) {
                console.error('Error:', error);
                alert('Error submitting transaction: ' + error.message);
            }
        });
    }

    // Handle push to mempool buttons
    window.pushTransaction = async function(txid) {
        // Extract network from current URL path
        const pathParts = window.location.pathname.split('/').filter(p => p);
        const validNetworks = ['mainchain', 'testnetv3', 'testnetv4', 'signet'];
        const networkIndex = pathParts.findIndex(p => validNetworks.includes(p));
        const network = networkIndex !== -1 ? pathParts[networkIndex] : 'mainchain';
        
        try {
            const response = await fetch(`/${network}/transaction/${txid}/push`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.status === 'success' || result.status === 'confirmed') {
                alert('Transaction pushed successfully');
                location.reload();
            } else {
                alert(`Error: ${result.error || result.analysis_result || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error pushing transaction: ' + error.message);
        }
    };

    // Handle delete transaction buttons
    window.deleteTransaction = async function(txid) {
        if (confirm('Are you sure you want to delete this transaction?')) {
            // Extract network from current URL path
            const pathParts = window.location.pathname.split('/').filter(p => p);
            const validNetworks = ['mainchain', 'testnetv3', 'testnetv4', 'signet'];
            const networkIndex = pathParts.findIndex(p => validNetworks.includes(p));
            const network = networkIndex !== -1 ? pathParts[networkIndex] : 'mainchain';
            
            try {
                const response = await fetch(`/${network}/transaction/${txid}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                if (result.status === 'success') {
                    location.reload();
                } else {
                    alert(`Error: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error deleting transaction: ' + error.message);
            }
        }
    };

    // Handle hide confirmed transactions toggle
    const hideConfirmedToggle = document.getElementById('hideConfirmedToggle');
    if (hideConfirmedToggle) {
        hideConfirmedToggle.addEventListener('change', function() {
            const confirmedRows = document.querySelectorAll('tr[data-status="confirmed"]');
            confirmedRows.forEach(row => {
                row.style.display = this.checked ? 'none' : '';
            });
        });
    }
}); 