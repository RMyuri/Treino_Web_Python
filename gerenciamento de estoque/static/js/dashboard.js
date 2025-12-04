let items = [];

async function loadItems() {
    try {
        const response = await fetch('/api/items');
        if (response.ok) {
            const data = await response.json();
            items = data.items;
            displayItems();
            updateSummary();
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Erro ao carregar itens:', error);
    }
}

function displayItems() {
    const container = document.getElementById('itemsContainer');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">[ ]</div>
                <p>Nenhum produto adicionado ainda</p>
            </div>
        `;
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Qtd</th>
                    <th>Valor Unit.</th>
                    <th>Total (R$)</th>
                    <th>Acoes</th>
                </tr>
            </thead>
            <tbody>
    `;

    items.forEach(item => {
        html += `
            <tr>
                <td><strong>${item.name}</strong></td>
                <td>${item.item_type}</td>
                <td>${item.quantity}</td>
                <td>R$ ${item.value.toFixed(2)}</td>
                <td><strong>R$ ${item.total.toFixed(2)}</strong></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-edit" onclick="openEditModal(${item.id})">Editar</button>
                        <button class="btn-delete" onclick="deleteItem(${item.id})">Deletar</button>
                    </div>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

function updateSummary() {
    const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
    const totalValue = items.reduce((sum, item) => sum + item.total, 0);

    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalValue').textContent = `R$ ${totalValue.toFixed(2)}`;
}

document.getElementById('addItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('itemName').value;
    const item_type = document.getElementById('itemType').value;
    const quantity = parseInt(document.getElementById('itemQuantity').value);
    const value = parseFloat(document.getElementById('itemValue').value);

    try {
        const response = await fetch('/api/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, item_type, quantity, value })
        });

        if (response.ok) {
            const newItem = await response.json();
            items.push(newItem);
            displayItems();
            updateSummary();
            document.getElementById('addItemForm').reset();
            showMessage('formMessage', 'OK - Produto adicionado com sucesso!', 'success');
        } else {
            const data = await response.json();
            showMessage('formMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('formMessage', 'Erro ao adicionar produto', 'error');
    }
});

function openEditModal(itemId) {
    const item = items.find(i => i.id === itemId);
    if (item) {
        document.getElementById('editItemId').value = item.id;
        document.getElementById('editItemName').value = item.name;
        document.getElementById('editItemType').value = item.item_type;
        document.getElementById('editItemQuantity').value = item.quantity;
        document.getElementById('editItemValue').value = item.value;
        document.getElementById('editModal').classList.add('show');
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('show');
}

document.getElementById('editForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const itemId = parseInt(document.getElementById('editItemId').value);
    const name = document.getElementById('editItemName').value;
    const item_type = document.getElementById('editItemType').value;
    const quantity = parseInt(document.getElementById('editItemQuantity').value);
    const value = parseFloat(document.getElementById('editItemValue').value);

    try {
        const response = await fetch(`/api/items/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, item_type, quantity, value })
        });

        if (response.ok) {
            const updatedItem = await response.json();
            const index = items.findIndex(i => i.id === itemId);
            if (index !== -1) {
                items[index] = updatedItem;
            }
            displayItems();
            updateSummary();
            closeEditModal();
            showMessage('formMessage', 'OK - Produto atualizado!', 'success');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
});

async function deleteItem(itemId) {
    if (confirm('Tem certeza que deseja deletar este produto?')) {
        try {
            const response = await fetch(`/api/items/${itemId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                items = items.filter(i => i.id !== itemId);
                displayItems();
                updateSummary();
                showMessage('formMessage', 'OK - Produto deletado!', 'success');
            }
        } catch (error) {
            console.error('Erro:', error);
        }
    }
}

async function logout() {
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    setTimeout(() => {
        element.className = 'message';
    }, 3500);
}

// Event listener para fechar modal ao clicar fora
document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('editModal')) {
        closeEditModal();
    }
});

loadItems();
