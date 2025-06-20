document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок сортировки
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const sort = this.dataset.sort;
            const direction = this.dataset.direction;
            applyFilters({sort, direction});
        });
    });

    // Обработчик для формы поиска
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }

    // Функция для применения фильтров
    function applyFilters(additionalParams = {}) {
    const form = document.querySelector('.search-form');
    if (!form) return;

    // Получаем все кнопки сортировки и поиска
    const allButtons = document.querySelectorAll('.sort-btn, .btn-search');
    
    // Блокируем кнопки и показываем индикатор загрузки
    allButtons.forEach(btn => {
        btn.disabled = true;
        btn.classList.add('loading');
    });

    // Очищаем предыдущий таймаут, если есть
    if (this.searchTimeout) clearTimeout(this.searchTimeout);
    
    // Устанавливаем новый таймаут с увеличенной задержкой (500мс)
    this.searchTimeout = setTimeout(() => {
        const params = new URLSearchParams();
        
        // Собираем параметры с проверкой на валидность
        const origin = document.getElementById('origin')?.value;
        if (origin) params.append('origin', origin);
        
        const destination = document.getElementById('destination')?.value;
        if (destination) params.append('destination', destination);
        
        const departureDate = document.getElementById('departure_date')?.value;
        if (departureDate) params.append('departure_date', departureDate);
        
        const minPrice = parseInt(document.getElementById('min_price')?.value || '');
        if (!isNaN(minPrice) && minPrice > 0) params.append('min_price', minPrice);
        
        const maxPrice = parseInt(document.getElementById('max_price')?.value || '');
        if (!isNaN(maxPrice) && maxPrice > 0) params.append('max_price', maxPrice);
        
        const airline = document.getElementById('airline')?.value;
        if (airline) params.append('airline', airline);

        // Добавляем параметры сортировки
        if (additionalParams.sort) {
            params.append('sort', additionalParams.sort);
            params.append('direction', additionalParams.direction || 'asc');
        }

        // Добавляем индикатор загрузки в контейнер результатов
        const resultsContainer = document.querySelector('.tickets-list');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="loading-indicator">Загрузка...</div>';
        }

        fetch(`${form.action}?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            if (resultsContainer) resultsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Search error:', error);
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="error">
                        Ошибка загрузки данных. Пожалуйста, попробуйте позже.
                    </div>
                `;
            }
        })
        .finally(() => {
            // Восстанавливаем кнопки после завершения запроса
            allButtons.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('loading');
            });
            
            // Привязываем обработчики к новым кнопкам бронирования
            bindBookingButtons();
        });
    }, 500); // Увеличенная задержка 500мс
}

    // Функция для привязки обработчиков к кнопкам бронирования
    function bindBookingButtons() {
        document.querySelectorAll('.btn-book').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const flightId = this.getAttribute('data-flight-id');
                const price = this.closest('.ticket-card').querySelector('.price').textContent.trim().replace(/\D/g, '');
                
                fetch('/add_booking', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        flight_id: flightId,
                        price: price
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        alert('Бронирование успешно создано!');
                        window.location.href = '/bookings';
                    } else {
                        alert('Ошибка при бронировании: ' + (data.message || 'Неизвестная ошибка'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при бронировании');
                });
            });
        });
    }

    // Первоначальная привязка обработчиков
    bindBookingButtons();
});
document.addEventListener('DOMContentLoaded', function() {
    // Обработка бронирования
    document.querySelectorAll('.btn-book').forEach(button => {
        button.addEventListener('click', function() {
            const flightId = this.getAttribute('data-flight-id');
            
            fetch('/add_booking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flight_id: flightId,
                    price: this.closest('.ticket-card').querySelector('.price').textContent.trim().replace(/\D/g, '')
                })
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    alert('Бронирование успешно создано!');
                    window.location.href = '/bookings';
                } else {
                    alert('Ошибка при бронировании: ' + (data.message || 'Неизвестная ошибка'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при бронировании');
            });
        });
    });
});