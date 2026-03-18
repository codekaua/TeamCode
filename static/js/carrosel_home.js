const track = document.getElementById('track');
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');

let index = 0;

function moveCarousel() {
    const cardWidth = document.querySelector('.product-card').offsetWidth + 15;
    track.style.transform = `translateX(${-index * cardWidth}px)`;
}

nextBtn.addEventListener('click', () => {
    if (index < track.children.length - 4) { // Impede de passar do fim
        index++;
        moveCarousel();
    }
});

prevBtn.addEventListener('click', () => {
    if (index > 0) {
        index--;
        moveCarousel();
    }
});