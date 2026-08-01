import axios from 'axios'

export const getAuthToken = () => localStorage.getItem('token') ?? sessionStorage.getItem('token')
export const setAuthToken = (token: string, remember: boolean) => {
  if (remember) {
    localStorage.setItem('token', token)
    sessionStorage.removeItem('token')
  } else {
    sessionStorage.setItem('token', token)
    localStorage.removeItem('token')
  }
}
export const clearAuthToken = () => {
  localStorage.removeItem('token')
  sessionStorage.removeItem('token')
}

export const api = axios.create({
  baseURL: 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
