import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'

import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import AlertUpload from './pages/AlertUpload'
import AlertExplorer from './pages/AlertExplorer'
import AlertDetails from './pages/AlertDetails'
import Incidents from './pages/Incidents'
import FatigueAnalytics from './pages/FatigueAnalytics'
import ModelInsights from './pages/ModelInsights'
import Settings from './pages/Settings'

export default function App() {
  const auth = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<Login auth={auth} />} />
      <Route path="/register" element={<Register auth={auth} />} />

      <Route
        element={
          <ProtectedRoute isAuthenticated={auth.isAuthenticated}>
            <AppLayout user={auth.user} onLogout={auth.logout} />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/alerts" element={<AlertExplorer />} />
        <Route path="/alerts/:id" element={<AlertDetails />} />
        <Route path="/upload" element={<AlertUpload />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/fatigue" element={<FatigueAnalytics />} />
        <Route path="/model-insights" element={<ModelInsights />} />
        <Route path="/settings" element={<Settings user={auth.user} />} />
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
