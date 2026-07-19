// Генерация случайного цвета
export function getRandomColor() {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

// Получение контрастного цвета (черный или белый)
export function getContrastColor(hexcolor) {
  if (!hexcolor) return '#000000';
  
  // Убираем # если есть
  hexcolor = hexcolor.replace('#', '');
  
  const r = parseInt(hexcolor.substr(0, 2), 16);
  const g = parseInt(hexcolor.substr(2, 2), 16);
  const b = parseInt(hexcolor.substr(4, 2), 16);
  
  // Формула для вычисления яркости
  const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  
  return brightness > 128 ? '#000000' : '#FFFFFF';
}

// Затемнение цвета
export function darkenColor(color, percent) {
  if (!color) return '#000000';
  
  let R = parseInt(color.substring(1, 3), 16);
  let G = parseInt(color.substring(3, 5), 16);
  let B = parseInt(color.substring(5, 7), 16);

  R = parseInt(R * (100 - percent) / 100);
  G = parseInt(G * (100 - percent) / 100);
  B = parseInt(B * (100 - percent) / 100);

  R = (R < 0) ? 0 : R;
  G = (G < 0) ? 0 : G;
  B = (B < 0) ? 0 : B;

  R = (R < 255) ? R : 255;
  G = (G < 255) ? G : 255;
  B = (B < 255) ? B : 255;

  const RR = ((R.toString(16).length === 1) ? "0" + R.toString(16) : R.toString(16));
  const GG = ((G.toString(16).length === 1) ? "0" + G.toString(16) : G.toString(16));
  const BB = ((B.toString(16).length === 1) ? "0" + B.toString(16) : B.toString(16));

  return "#" + RR + GG + BB;
}

// Вычисление времени выполнения с учетом зависимостей
export function calculateRunTime(task, allTasks) {
  if (!task.dependencies || task.dependencies.length === 0) {
    return {
      start_time: task.start_time || 0,
      finish_time: task.finish_time || (task.start_time || 0) + (task.duration || 0)
    };
  }

  // Находим максимальное время завершения среди зависимостей
  let maxDependencyFinish = 0;
  task.dependencies.forEach(depId => {
    const dependency = allTasks.find(t => t.id === depId);
    if (dependency && dependency.finish_time > maxDependencyFinish) {
      maxDependencyFinish = dependency.finish_time;
    }
  });

  const startTime = Math.max(task.start_time || 0, maxDependencyFinish);
  const finishTime = task.finish_time || startTime + (task.duration || 0);

  return {
    start_time: startTime,
    finish_time: finishTime
  };
}

// Форматирование времени
export function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}с`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}м ${remainingSeconds}с`;
  }
}

// Валидация email
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Глубокое клонирование объекта
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// Дебаунс функция
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Генерация уникального ID
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}