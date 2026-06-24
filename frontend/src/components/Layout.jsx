import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../api/auth'
import { FiGrid, FiUpload, FiFileText, FiLogOut, FiBarChart2 } from 'react-icons/fi'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>📊 <span>SalesIQ</span></h1>
          <p>Intelligence Platform</p>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <FiGrid /> <span>Dashboard</span>
          </NavLink>
          <NavLink to="/upload" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <FiUpload /> <span>Upload Data</span>
          </NavLink>
          <NavLink to="/reports" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <FiFileText /> <span>Reports</span>
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user?.name?.[0]?.toUpperCase()}</div>
            <div>
              <div className="name">{user?.name}</div>
              <div className="role">{user?.role}</div>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <FiLogOut /> <span>Logout</span>
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
