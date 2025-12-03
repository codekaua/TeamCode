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

const opcao_categoria = document.getElementById("opcao-categoria");
const opcoes_side_cetegoria = document.getElementById("opcoes-side-cetegoria");
const icone_mais = document.getElementById("icone-mais");
const icone_menos = document.getElementById("icone-menos");

const opcao_cor = document.getElementById("opcao-cor");
const opcoes_side_cor = document.getElementById("opcoes-side-cor");
const icone_mais_cor = document.getElementById("icone-mais-cor");
const icone_menos_cor = document.getElementById("icone-menos-cor");


const radios = document.querySelectorAll('input[name="categoria"]');
const radios_cor = document.querySelectorAll('input[name="cor"]');
const limpar_filtro = document.getElementById("limpar-filtro");

const filtro_mobile = document.getElementById("filtro-mobile")
const side = document.getElementById("side")
const fechar_filtro_mobile = document.getElementById("icone-fechar")

fechar_filtro_mobile.addEventListener("click", () => {
  side.style.display = "none";
  overlay.style.display = "none";       // esconde overlay
  document.body.style.overflow = "auto";  // libera scroll da página
})

filtro_mobile.addEventListener("click", () =>{
  side.style.display = "block";
  overlay.style.display = "block";       // mostra overlay
  document.body.style.overflow = "hidden"; // bloqueia scroll da página
})

overlay.addEventListener("click", () => {
  side.style.display = "none";
  overlay.style.display = "none";
  document.body.style.overflow = "auto";
});

radios.forEach((radio) => {
  radio.addEventListener("click", () => {
    limpar_filtro.style.display = "block";
  });
});

radios_cor.forEach((radio) => {
  radio.addEventListener("click", () => {
    limpar_filtro.style.display = "block";
  });
});

limpar_filtro.addEventListener("click", () => {
  radios.forEach((r) => (r.checked = false));
  limpar_filtro.style.display = "none";
  window.location.href = window.location.pathname;
});

opcao_categoria.addEventListener("click", () => {
  if (opcoes_side_cetegoria.style.display === "none") {
    opcoes_side_cetegoria.style.display = "block";
    icone_menos.style.display = "block";
    icone_mais.style.display = "none";
  } else {
    opcoes_side_cetegoria.style.display = "none";
    icone_menos.style.display = "none";
    icone_mais.style.display = "block";
  }
});

opcao_cor.addEventListener("click", () => {
  if (opcoes_side_cor.style.display === "none") {
    opcoes_side_cor.style.display = "block";
    icone_menos_cor.style.display = "block";
    icone_mais_cor.style.display = "none";
  } else {
    opcoes_side_cor.style.display = "none";
    icone_menos_cor.style.display = "none";
    icone_mais_cor.style.display = "block";
  }
});
