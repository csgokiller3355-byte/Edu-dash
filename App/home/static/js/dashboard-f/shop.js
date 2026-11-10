// static/js/shop.js
export function initShop() {
    let coins = 150;
    const coinDisplays = [
        document.getElementById('sidebar-coins'),
        document.getElementById('header-coins')
    ];

    function updateCoinsUI() {
        coinDisplays.forEach(el => {
            if (el) el.innerHTML = `🪙 ${coins}`;
        });
    }

    const buyButtons = document.querySelectorAll('.buy-btn');
    buyButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const price = parseInt(btn.getAttribute('data-price'));
            if (coins >= price) {
                coins -= price;
                updateCoinsUI();
                alert('Успешно куплено!');
            } else {
                alert('Недостаточно монеток! Сдайте больше домашней работы.');
            }
        });
    });
}