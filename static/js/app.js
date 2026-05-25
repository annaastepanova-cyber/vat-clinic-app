document.addEventListener('DOMContentLoaded', () => {
  // 🟢 Клиентская валидация форм
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      let valid = true;
      form.querySelectorAll('[required]').forEach(el => {
        if (!el.value.trim()) {
          valid = false;
          el.classList.add('error');
          showFieldError(el, 'Поле обязательно для заполнения');
        }
      });
      if (!valid) e.preventDefault();
    });

    // Снятие ошибки при вводе
    form.querySelectorAll('input, select, textarea').forEach(el => {
      el.addEventListener('input', () => {
        el.classList.remove('error');
        const err = el.nextElementSibling;
        if (err?.classList.contains('error-msg')) err.style.display = 'none';
      });
    });
  });

  // 🟡 Слайдер
  const slides = document.querySelector('.slides');
  if (slides) {
    let i = 0;
    const imgs = slides.querySelectorAll('img');
    const show = (idx) => {
      i = (idx + imgs.length) % imgs.length;
      slides.style.transform = `translateX(${-i * 100}%)`;
    };
    document.querySelector('.prev')?.addEventListener('click', () => show(i - 1));
    document.querySelector('.next')?.addEventListener('click', () => show(i + 1));
    setInterval(() => show(i + 1), 4000);
  }

  // 🔵 Преобразование Flask flash в toast
  document.querySelectorAll('.flash, .alert').forEach(f => {
    const type = f.classList.contains('error') || f.textContent.includes('ошибка') ? 'error' : 'success';
    showToast(f.textContent, type);
    f.remove();
  });
});

function showFieldError(el, msg) {
  let err = el.nextElementSibling;
  if (!err || !err.classList.contains('error-msg')) {
    err = document.createElement('div');
    err.className = 'error-msg';
    el.parentNode.insertBefore(err, el.nextSibling);
  }
  err.textContent = msg;
  err.style.display = 'block';
}

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 3500);
}

// AJAX отправка формы заявки
const orderForm = document.querySelector('form[action="/new-order"]');
if (orderForm) {
  orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = orderForm.querySelector('button[type="submit"]');
    const loader = document.getElementById('form-loader');
    
    btn.disabled = true;
    loader.style.display = 'block';

    const formData = {
      service_id: orderForm.service_id.value,
      veterinar_id: orderForm.veterinar_id.value,
      order_date: orderForm.order_date.value,
      start_time: orderForm.start_time.value,
      comment: orderForm.comment.value
    };

    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (res.ok) {
        showToast('Заявка успешно создана!', 'success');
        setTimeout(() => window.location.href = '/dashboard', 1000);
      } else {
        showToast(data.error || 'Ошибка сервера', 'error');
      }
    } catch (err) {
      showToast('Нет соединения с сервером', 'error');
    } finally {
      btn.disabled = false;
      loader.style.display = 'none';
    }
  });
}