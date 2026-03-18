// 1. BLOQUEIO DE CHECKOUT VAZIO
document.addEventListener("DOMContentLoaded", () => {
    // Selecionamos o formulário que aponta para /checkout
    const form = document.querySelector('form[action="/checkout"]');

    if (form) {
        form.addEventListener("submit", (e) => {
            // Conta quantos itens existem no resumo do pedido (lado direito)
            const itensNoCarrinho = document.querySelectorAll(".cart-item").length;

            if (itensNoCarrinho === 0) {
                e.preventDefault(); // Cancela o envio para o servidor
                
                // Dispara o alerta visual
                exibirAviso("Atenção: Seu carrinho está vazio! Adicione produtos para continuar.");
            }
        });
    }
});

// 2. FUNÇÃO DE AVISO (ANIMADA)
function exibirAviso(mensagem) {
    const aviso = document.createElement("div");
    aviso.textContent = mensagem;
    
    // Estilo via JS para não precisar mexer no CSS
    Object.assign(aviso.style, {
        position: "fixed",
        bottom: "30px",
        left: "50%",
        transform: "translateX(-50%)",
        backgroundColor: "#e63946",
        color: "white",
        padding: "16px 32px",
        borderRadius: "12px",
        boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
        zIndex: "9999",
        fontWeight: "bold",
        transition: "all 0.5s ease"
    });

    document.body.appendChild(aviso);

    // Remove após 3 segundos com efeito de sumiço
    setTimeout(() => {
        aviso.style.opacity = "0";
        setTimeout(() => aviso.remove(), 500);
    }, 3000);
}

// 3. SUAS FUNÇÕES ORIGINAIS (MANTIDAS)
function selectPayment(element, type) {
    document
        .querySelectorAll(".option")
        .forEach((opt) => opt.classList.remove("active"));
    element.classList.add("active");

    const cardForm = document.getElementById("card-form");
    cardForm.style.display = type === "card" ? "block" : "none";
}

function buscarCep() {
    let cep = document.getElementById("cep").value.replace(/\D/g, "");
    if (cep !== "") {
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then((res) => res.json())
            .then((dados) => {
                if (!dados.erro) {
                    document.getElementById("rua").value = dados.logradouro;
                    document.getElementById("bairro").value = dados.bairro;
                    document.getElementById("cidade").value = dados.localidade;
                }
            });
    }
}