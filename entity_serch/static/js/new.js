// Функция для получения значения из URL
function getValueFromUrl() {
    // Получаем текущий URL
    const currentUrl = window.location.href;
    
    // Разбиваем URL на части
    const urlParts = currentUrl.split('/');
    
    // Поскольку URL начинается с 'http://' или 'https://', 
    // и далее идут домен, протокол и т.д., нам нужно найти нужную часть
    // Нам нужно значение после '/current/', значит нужно найти индекс '/current/' и взять следующий элемент
    const currentIndex = urlParts.indexOf('current');
    
    if (currentIndex !== -1) {
        // Если '/current/' нашлось, берем следующее значение
        const value = urlParts[currentIndex + 1];
        return value;
    } else {
        // Если '/current/' не нашлось, возвращаем что-то по умолчанию или обрабатываем ошибку
        return "Не найдено";
    }
}

// Функция для обновления значения в форме
function updateFormValue() {
    const value = getValueFromUrl();
    document.getElementById('currentValue').value = value;
}

// Вызываем функцию обновления при загрузке страницы
document.addEventListener('DOMContentLoaded', updateFormValue);
