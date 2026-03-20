// Espera a página carregar completamente
document.addEventListener("DOMContentLoaded", function () {
  // Pega os parâmetros da URL (tudo que vem depois do "?")
  const urlParams = new URLSearchParams(window.location.search);
  const erro = urlParams.get("erro");

  // Verifica se o erro é o de estoque
  if (erro === "estoque_insuficiente") {
    // Dispara o pop-up de aviso
    alert(
      "Ops! Estoque insuficiente. Que tal outras opções similares?",
    );

    // (Opcional) Limpa a URL para o aviso não aparecer de novo se ele atualizar a página
    window.history.replaceState(null, null, window.location.pathname);
  }
});
