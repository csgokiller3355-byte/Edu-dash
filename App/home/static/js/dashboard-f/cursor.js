export function initCustomCursor() {
    // Создаем элемент курсора с вашим классом
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.id = 'customCursor';
    document.body.appendChild(cursor);

    // Respect saved preference: hide cursor if user disabled it
    const savedCursor = localStorage.getItem('customCursorEnabled');
    if (savedCursor === 'false') {
        cursor.style.display = 'none';
    }

    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;

    // Коэффициент плавности (чем меньше число, тем сильнее задержка)
    const speed = 0.15;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        cursorX += (mouseX - cursorX) * speed;
        cursorY += (mouseY - cursorY) * speed;

        cursor.style.transform = `translate(${cursorX}px, ${cursorY}px) translate(-50%, -50%)`;
        requestAnimationFrame(animate);
    }

    animate();

    // Отслеживание наведения на интерактивные элементы
    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('button, a, .menu-btn, .back-btn, input, select');
        if (target) {
            document.body.classList.add('cursor-hover');
        }
    });

    document.addEventListener('mouseout', (e) => {
        const target = e.target.closest('button, a, .menu-btn, .back-btn, input, select');
        if (target) {
            document.body.classList.remove('cursor-hover');
        }
    });
}