document.addEventListener('DOMContentLoaded', function() {
    // Обработка загрузки фото профиля
    const photoUpload = document.getElementById('photo-upload');
    if (photoUpload) {
        photoUpload.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const form = document.getElementById('photo-form');
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const img = document.getElementById('profile-photo');
                        if (img) {
                            img.src = data.photo_url + '?' + new Date().getTime();
                        }
                        alert('Фото профиля успешно обновлено!');
                    } else {
                        throw new Error(data.error || 'Неизвестная ошибка');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Ошибка при загрузке фото: ' + error.message);
                });
            }
        });
    }

    // Обработка загрузки паспорта
    const passportUpload = document.getElementById('passport-upload');
    if (passportUpload) {
        passportUpload.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const form = document.getElementById('passport-form');
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const passportLink = document.getElementById('passport-link');
                        if (passportLink) {
                            // Обновляем ссылку на паспорт
                            passportLink.href = data.file_url + '?' + new Date().getTime();
                            passportLink.textContent = 'Просмотреть';
                            // Обновляем кнопку
                            const uploadBtn = document.querySelector('.passport-upload .upload-btn');
                            if (uploadBtn) {
                                uploadBtn.textContent = 'Заменить';
                            }
                        }
                        alert('Паспорт успешно загружен!');
                    } else {
                        throw new Error(data.error || 'Неизвестная ошибка');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Ошибка при загрузке паспорта: ' + error.message);
                });
            }
        });
    }
});