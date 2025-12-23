import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8001/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 요청 인터셉터: 토큰이 있으면 자동으로 헤더에 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 401 에러 시 로그아웃 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// 인증 API
export const authAPI = {
  signup: (userData) => api.post('/auth/signup', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getMe: () => api.get('/auth/users/me'),
  updateMe: (userData) => api.patch('/auth/users/me', userData)
}

// 도서 API
export const bookAPI = {
  getBooks: (params) => api.get('/books/', { params }),
  getBook: (id) => api.get(`/books/${id}/`),
  getBestSellers: () => api.get('/books/best-sellers/'),
  getTopRecommended: () => api.get('/books/top-recommended/'),
  getAgeBased: (age) => api.get('/books/age-based/', { params: { age } }),
  getSimilar: (id) => api.get(`/books/${id}/similar/`)
}

// 리뷰 API
export const reviewAPI = {
  getReviews: (bookId) => api.get('/reviews/', { params: { book: bookId } }),
  createReview: (reviewData) => api.post('/reviews/', reviewData),
  updateReview: (id, content) => api.patch(`/reviews/${id}/`, { content }),
  deleteReview: (id) => api.delete(`/reviews/${id}/`)
}

// 찜/읽음 API
export const userBookAPI = {
  addFavorite: (bookId) => api.post(`/auth/users/me/favorites/${bookId}`),
  removeFavorite: (bookId) => api.delete(`/auth/users/me/favorites/${bookId}`),
  getFavorites: () => api.get('/auth/me/favorites'),
  addReadBook: (bookId) => api.post(`/auth/users/me/read_books/${bookId}`),
  removeReadBook: (bookId) => api.delete(`/auth/users/me/read_books/${bookId}`)
}

// 추천 API
export const recommendAPI = {
  getPersonalized: () => api.get('/recommendations/me/')
}

// 카테고리/장르/작가 API
export const metaAPI = {
  getCategories: () => api.get('/categories/'),
  getGenres: () => api.get('/genres/'),
  getAuthors: () => api.get('/authors/')
}

export default api
