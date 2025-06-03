import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'; // Import Link
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import UserManagementPage from './pages/UserManagementPage'; // Import UserManagementPage
import CompanyManagementPage from './pages/CompanyManagementPage'; // Import CompanyManagementPage
import ChatInterface from './components/ChatInterface'; // Import ChatInterface

// Placeholder for Dashboard component
const Dashboard = () => {
  const { user, logout } = useAuth();
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: '250px', borderRight: '1px solid #ccc', padding: '10px' }}>
        <h1>Menu</h1>
        <p>Bem-vindo, {user?.nome || user?.email}!</p>
        <p>Empresa ID: {user?.empresa_id || 'N/A (Superuser)'}</p>
        <nav>
          <ul>
            <li><Link to="/dashboard">Dashboard Home</Link></li>
            {/* Add links to other sections */} 
            {user?.is_superuser && (
              <> 
                <li><Link to="/admin/users">Gerenciar Usuários</Link></li>
                <li><Link to="/admin/companies">Gerenciar Empresas</Link></li>
              </>
            )}
            {/* Add links for regular users/supervisors later (Chat, CRM, Instancias) */} 
             <li><Link to="/crm">CRM Kanban</Link></li> 
             <li><Link to="/instancias">Instâncias</Link></li> 
          </ul>
        </nav>
        <button onClick={logout} style={{ marginTop: '20px' }}>Logout</button>
      </div>
      <div style={{ flexGrow: 1, padding: '20px', display: 'flex', flexDirection: 'column' }}>
         {/* Main content area - Render based on route or state */} 
         <h2>Área Principal</h2>
         <p>Conteúdo do dashboard aqui...</p>
         
         {/* Integrate Chat Interface directly or conditionally */} 
         <div style={{ marginTop: 'auto', height: '40%' }}> {/* Position chat at the bottom */} 
            <ChatInterface />
         </div>
      </div>
    </div>
  );
};

// Placeholder for Login Page component
const LoginPage = () => {
  return (
    <div>
      <LoginForm />
    </div>
  );
};

// Placeholder for CRM Page
const CrmPage = () => <h2>Página do CRM Kanban (Em desenvolvimento)</h2>;

// Placeholder for Instancias Page
const InstanciasPage = () => <h2>Página de Gerenciamento de Instâncias (Em desenvolvimento)</h2>;


// Component to handle protected routes
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Carregando...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Component for Superuser-only routes
const SuperuserRoute = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Carregando...</div>;
    }

    // Redirect if not authenticated or not a superuser
    if (!user || !user.is_superuser) {
        return <Navigate to="/dashboard" />; // Or to a specific 'unauthorized' page
    }

    return children;
};


function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          {/* Admin/Superadmin Routes */}
          <Route 
            path="/admin/users" 
            element={
              <ProtectedRoute>
                <SuperuserRoute>
                   <UserManagementPage />
                </SuperuserRoute>
              </ProtectedRoute>
            }
          />
           <Route 
            path="/admin/companies" 
            element={
              <ProtectedRoute>
                <SuperuserRoute>
                   <CompanyManagementPage />
                </SuperuserRoute>
              </ProtectedRoute>
            }
          />
          {/* Other User Routes */}
           <Route 
            path="/crm" 
            element={
              <ProtectedRoute>
                <CrmPage />
              </ProtectedRoute>
            }
          />
           <Route 
            path="/instancias" 
            element={
              <ProtectedRoute>
                <InstanciasPage />
              </ProtectedRoute>
            }
          />
          
          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/dashboard" />} /> 
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

