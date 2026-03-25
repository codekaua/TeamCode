// Função que busca a quantidade e atualiza a bolinha
document.addEventListener("DOMContentLoaded", async function () {
    try {
        // Faz a requisição para a sua NOVA rota
        const response = await fetch("/api/contador-carrinho");

        if (response.ok) {
            const data = await response.json();
            const contador = document.getElementById("contador-carrinho");

            // Atualiza o número dentro da bolinha com o valor que veio do Python
            contador.innerText = data.quantidade;

            // Se tiver mais de 0 produtos, mostra a bolinha. Se não, esconde.
            if (data.quantidade > 0) {
                contador.style.display = "inline-block";
            } else {
                contador.style.display = "none";
            }
        }
    } catch (error) {
        console.error("Erro ao carregar o contador do carrinho:", error);
    }
});