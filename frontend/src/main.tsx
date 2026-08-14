import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { I18nextProvider } from 'react-i18next'
import App from './App'
import './index.css'
import { initializeTheme, ThemeProvider } from './lib/theme'
import i18n from './lib/i18n'
const queryClient = new QueryClient(); initializeTheme()
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><I18nextProvider i18n={i18n}><QueryClientProvider client={queryClient}><ThemeProvider><BrowserRouter><App /></BrowserRouter></ThemeProvider></QueryClientProvider></I18nextProvider></React.StrictMode>)
