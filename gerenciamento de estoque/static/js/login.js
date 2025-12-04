const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const submitBtn = loginForm.querySelector('button[type="submit"]');
const submitText = document.getElementById('submitText');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showError('Usuario e senha sao obrigatorios');
        return;
    }

    submitBtn.disabled = true;
    const originalText = submitText.textContent;
    submitText.innerHTML = '<span class="spinner"></span>Entrando...';

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('OK - Login realizado! Redirecionando...');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showError(data.error || 'Erro ao fazer login');
            submitBtn.disabled = false;
            submitText.textContent = originalText;
        }
    } catch (error) {
        showError('Erro ao conectar ao servidor');
        console.error('Erro:', error);
        submitBtn.disabled = false;
        submitText.textContent = originalText;
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
    window.scrollTo(0, 0);
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}
