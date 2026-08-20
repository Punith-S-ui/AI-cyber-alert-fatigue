import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

export default function AppLayout({ user, onLogout }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar user={user} onLogout={onLogout} />
      <main className="flex-1 p-8 max-w-[1600px]">
        <Outlet />
      </main>
    </div>
  )
}
