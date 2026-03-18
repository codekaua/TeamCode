function toggleMenu() {
  const menu = document.getElementById("menu-perfil");
  menu.style.display =
    menu.style.display === "block" ? "none" : "block";
}

// Fecha o menu se clicar fora
window.onclick = function (event) {
  const menu = document.getElementById("menu-perfil");
  const foto = document.getElementById("foto-perfil");
  if (!foto.contains(event.target) && !menu.contains(event.target)) {
    menu.style.display = "none";
  }
};