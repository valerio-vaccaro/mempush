document.addEventListener('DOMContentLoaded', function() {
    // Handle transaction submission
    const txForm = document.getElementById('txForm');
    if (txForm) {
        txForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const rawTx = document.getElementById('rawTx').value;
            
            try {
                const response = await fetch('/transaction/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ raw_tx: rawTx }),
                });
                
                if (response.ok) {
                    const result = await response.json();
                    window.location.href = `/transaction/${result.txid}`;
                } else {
                    alert('Error submitting transaction');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error submitting transaction');
            }
        });
    }

    // Handle push to mempool buttons
    window.pushTransaction = async function(txid) {
        try {
            const response = await fetch(`/transaction/${txid}/push`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            if (response.ok) {
                alert('Transaction pushed successfully');
                location.reload();
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error pushing transaction');
        }
    };

    // Handle delete transaction buttons
    window.deleteTransaction = async function(txid) {
        if (confirm('Are you sure you want to delete this transaction?')) {
            try {
                const response = await fetch(`/transaction/${txid}/delete`, {
                    method: 'POST',
                });
                
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error deleting transaction');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error deleting transaction');
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