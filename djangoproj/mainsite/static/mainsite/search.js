var isDown = false;
var startX;
var scrollLeft;
var check_scroll = true;
function listenall() {
    
    let slider = document.getElementsByClassName("scroll");

    for (let y = 0; y < slider.length; y++) {
        slider[y].addEventListener("mousedown", e => {
        isDown = true;
        slider[y].classList.add("active");
        startX = e.pageX - slider[y].offsetLeft;
        scrollLeft = slider[y].scrollLeft;
        check_scroll = true; //
        });
        slider[y].addEventListener("mouseleave", () => {
        isDown = false;
        slider[y].classList.remove("active");
        });
        slider[y].addEventListener("mouseup", () => {
        isDown = false;
        slider[y].classList.remove("active");
        });
        slider[y].addEventListener("mousemove", e => {
        if (!isDown) return;
        e.preventDefault();
        check_scroll = false; 
        const x = e.pageX - slider[y].offsetLeft;
        const walk = (x - startX)*1.4;
        slider[y].scrollLeft = scrollLeft - walk;
        });
    }

};

listenall();