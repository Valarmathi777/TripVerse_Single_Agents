import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const getDestinations = () =>
  client.get('/destinations').then((r) => r.data.destinations)

export const calculateBudget = (payload) =>
  client.post('/calculate-budget', payload).then((r) => r.data)

export const optimizeBudget = (payload) =>
  client.post('/optimize-budget', payload).then((r) => r.data)

export const predictExpense = (payload) =>
  client.post('/predict-expense', payload).then((r) => r.data)

export const getHotels = (destination, category) =>
  client.get('/hotels', { params: { destination, category } }).then((r) => r.data)

export const getRestaurants = (destination, category) =>
  client.get('/restaurants', { params: { destination, category } }).then((r) => r.data)

export const getWeather = (destination) =>
  client.get('/weather', { params: { destination } }).then((r) => r.data)

export const getCurrency = (amount, from, to) =>
  client.get('/currency', { params: { amount, from, to } }).then((r) => r.data)

export const getTransport = (destination) =>
  client.get('/transport', { params: { destination } }).then((r) => r.data)

export const getHistory = (limit = 10) =>
  client.get('/history', { params: { limit } }).then((r) => r.data.history)

export const getHistoryDetail = (id) =>
  client.get(`/history/${id}`).then((r) => r.data)

export default client
