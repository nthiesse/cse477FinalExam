const hamburger = document.querySelector(".hamburger");
const menu = document.querySelector(".menu");


hamburger.addEventListener("click", () => {
    menu.classList.toggle("active");
})

document.querySelector("link").for-each(n => n.addEventListener("click", ()=> {
    menu.classList.remove("active");
}))