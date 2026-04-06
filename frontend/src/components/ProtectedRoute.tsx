import { Navigate } from 'react-router-dom'
import { tokenStore } from '../api/client'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!tokenStore.get()) {
    return <Navigate to="/auth" replace />
  }
  return <>{children}</>
}
