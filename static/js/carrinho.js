document.addEventListener("DOMContentLoaded", async () => {
  const contador = document.getElementById("contador-carrinho");
  const carrinhoIcon = document.querySelector(".carrinho-icon");

  if (!contador || !carrinhoIcon) return;

  try {
    const resposta = await fetch("/api/contador-carrinho");
    const dados = await resposta.json();
    const quantidade = dados.quantidade || 0;

    contador.textContent = quantidade;

    // ⚡ Animação suave no número (badge)
    contador.style.transition = "transform 0.4s ease, background 0.4s";
    contador.style.transform = "scale(1.3)";
    contador.style.background = "#ffc107";

    setTimeout(() => {
      contador.style.transform = "scale(1)";
      contador.style.background = "#ff4747";
    }, 400);

    // 🛒 Animação no ícone
    carrinhoIcon.style.transition = "transform 0.4s ease";
    carrinhoIcon.style.transform = "rotate(-15deg)";
    setTimeout(() => (carrinhoIcon.style.transform = "rotate(0deg)"), 400);
  } catch (error) {
    console.error("Erro ao buscar contador do carrinho:", error);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const cepInput = document.querySelector('input[name="cep"]');
  const estadoSelect = document.querySelector('select[name="estado"]');
  const bairroInput = document.querySelector('input[name="bairro"]');
  const logradouroInput = document.querySelector('input[name="logradouro"]');
  // Usar name para o endereço evita pegar o input errado
  const enderecoInput = document.querySelector('input[name="endereco"]');

  cepInput.addEventListener("blur", async () => {
    const cep = cepInput.value.replace(/\D/g, "");
    if (cep.length !== 8) {
      alert("CEP inválido!");
      return;
    }

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      const data = await response.json();

      if (data.erro) {
        alert("CEP não encontrado!");
        return;
      }

      bairroInput.value = data.bairro || "";
      logradouroInput.value = data.logradouro || "";
      if (data.uf) estadoSelect.value = data.uf;
      enderecoInput.value = `${cep} - ${data.uf}, ${data.bairro}, ${data.logradouro}`;
    } catch (error) {
      console.error("Erro ao consultar CEP:", error);
    }
  });
});
