document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Lógica do Formulário de Login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });

                // Tratamento de JSON: garante que a resposta seja lida como objeto
                const data = await response.json();

                if (response.ok && data.success) {
                    // Redireciona para a URL enviada pelo Flask
                    window.location.href = data.redirect_url;
                } else {
                    // Mostra a mensagem de erro vinda do servidor ou padrão
                    alert(data.message || 'Erro ao realizar login.');
                }
            } catch (err) {
                console.error("Erro na comunicação com o servidor:", err);
                alert("Ocorreu um erro de conexão. Tente novamente.");
            }
        });
    }

    // 2. Lógica da Busca de Usuários
    const inputBusca = document.getElementById('busca_nome');
    const divResultados = document.getElementById('resultados_busca');
    const inputHidden = document.getElementById('usuario_selecionado');
    const tipoBusca = document.getElementById('tipo_busca'); 

    if (inputBusca && divResultados && inputHidden) {
        inputBusca.addEventListener('input', async function() {
            const termo = this.value.trim();
            const tipo = tipoBusca ? tipoBusca.value : 'supervisor'; 
            
            if (termo.length < 2) {
                divResultados.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`/api/search/${tipo}?q=${encodeURIComponent(termo)}`);
                const dados = await response.json();

                divResultados.innerHTML = '';
                
                if (Array.isArray(dados) && dados.length > 0) {
                    dados.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'p-3 hover:bg-blue-50 cursor-pointer border-b text-sm';
                        div.textContent = item.nome;
                        
                        div.onclick = () => {
                            inputBusca.value = item.nome;
                            // Aqui definimos o formato do valor que o Python vai receber (split)
                            inputHidden.value = `${tipo}:${item.id}:${item.nome}:email_placeholder`;
                            divResultados.style.display = 'none';
                        };
                        divResultados.appendChild(div);
                    });
                    divResultados.style.display = 'block';
                } else {
                    divResultados.innerHTML = '<div class="p-2 text-gray-500 text-sm">Nenhum resultado encontrado</div>';
                    divResultados.style.display = 'block';
                }
            } catch (err) {
                console.error("Erro na busca de usuários:", err);
            }
        });
    }
});

// FUNÇÃO DE LOGOUT
async function logout() {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (err) {
        console.error("Erro ao fazer logout:", err);
    }
}