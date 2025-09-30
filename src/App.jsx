import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-bg text-white">
        <Routes>
          <Route path="/" element={
            <div className="relative">
              <div className="fixed top-0 left-0 right-0 z-50">
                <Navbar />
              </div>
              <LandingPage />
            </div>
          } />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App