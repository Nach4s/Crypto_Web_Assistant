// API Configuration
// В продакшене использует переменную окружения VITE_API_URL
// В разработке использует относительный путь (прокси Vite)

export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Функция для создания полного URL API запроса
export const getApiUrl = (path) => {
  // Если path уже начинается с /, убираем его
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  
  // Если есть базовый URL, используем его
  if (API_BASE_URL) {
    // Убираем trailing slash из базового URL если есть
    const baseUrl = API_BASE_URL.replace(/\/$/, '')
    return `${baseUrl}${cleanPath}`
  }
  
  // В разработке используем относительный путь (работает с прокси Vite)
  return cleanPath
}

