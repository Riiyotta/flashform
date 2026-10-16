import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Enables the pre-animation hidden states in index.css before the first paint (see src/anim).
document.documentElement.classList.add('js-anim')
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
