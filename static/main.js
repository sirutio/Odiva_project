// static/main.js
const toggleBtn = document.querySelector('.navbar_toogleBtn');
const menu = document.querySelector('.navbar_menu');
const navbar = document.querySelector('.navbar');

toggleBtn.addEventListener('click', () => {
    menu.classList.toggle('active');
});
