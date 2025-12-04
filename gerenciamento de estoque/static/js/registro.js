const registerForm = document.getElementById('registerForm');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const submitBtn = registerForm.querySelector('button[type="submit"]');
const submitText = document.getElementById('submitText');

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const acceptTerms = document.getElementById('acceptTerms').checked;

    // Validacoes
    if (!acceptTerms) {
        showError('Voce deve aceitar os termos de uso');
        return;
    }

    if (password.length < 6) {
        showError('A senha deve ter no minimo 6 caracteres');
        return;
    }

    if (password !== confirmPassword) {
        showError('As senhas nao conferem');
        return;
    }

    if (username.length < 3) {
        showError('O nome de usuario deve ter no minimo 3 caracteres');
        return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showError('Usuario deve conter apenas letras, numeros e underscore');
        return;
    }

    submitBtn.disabled = true;
    const originalText = submitText.textContent;
    submitText.innerHTML = '<span class="spinner"></span>Criando...';

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                phone: phone,
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('OK - Conta criada com sucesso! Redirecionando...');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showError(data.error || 'Erro ao criar conta');
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
