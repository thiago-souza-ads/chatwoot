import React, { useState, useEffect } from 'react';
import { getUsers, createUser } from '../services/api'; // Assuming API functions exist
import { useAuth } from '../contexts/AuthContext';

function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth(); // Get current user info

  // State for creating a new user (simplified)
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserEmpresaId, setNewUserEmpresaId] = useState('');
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      // Only superusers should fetch all users
      if (user?.is_superuser) {
        try {
          setLoading(true);
          const data = await getUsers();
          setUsers(data);
          setError('');
        } catch (err) {
          setError('Falha ao carregar usuários.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      } else {
        // Non-superusers might see users of their own company (implement later if needed)
        setUsers([]); // For now, only superuser sees the list
        setLoading(false);
      }
    };

    fetchUsers();
  }, [user]); // Refetch if user changes

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const userData = {
        email: newUserEmail,
        password: newUserPassword,
        nome: newUserName,
        empresa_id: user.is_superuser ? (newUserEmpresaId ? parseInt(newUserEmpresaId) : null) : user.empresa_id,
        is_superuser: user.is_superuser ? isSuperuser : false, // Only superuser can create superuser
        is_supervisor: isSupervisor,
        is_active: true, // Default to active
      };
      const createdUser = await createUser(userData);
      setUsers([...users, createdUser]); // Add new user to the list
      // Clear form
      setNewUserEmail('');
      setNewUserName('');
      setNewUserPassword('');
      setNewUserEmpresaId('');
      setIsSuperuser(false);
      setIsSupervisor(false);
    } catch (err) {
      setError(`Falha ao criar usuário: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    }
  };

  // Render logic - Only show management features to superusers for now
  if (!user?.is_superuser) {
    return <div>Acesso restrito a Superusuários.</div>;
  }

  return (
    <div>
      <h2>Gerenciamento de Usuários (Superuser)</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <h3>Criar Novo Usuário</h3>
      <form onSubmit={handleCreateUser}>
        <input type="email" value={newUserEmail} onChange={(e) => setNewUserEmail(e.target.value)} placeholder="Email" required />
        <input type="text" value={newUserName} onChange={(e) => setNewUserName(e.target.value)} placeholder="Nome" required />
        <input type="password" value={newUserPassword} onChange={(e) => setNewUserPassword(e.target.value)} placeholder="Senha" required />
        {user.is_superuser && (
            <input type="number" value={newUserEmpresaId} onChange={(e) => setNewUserEmpresaId(e.target.value)} placeholder="ID da Empresa (opcional)" />
        )}
        <label>
          <input type="checkbox" checked={isSupervisor} onChange={(e) => setIsSupervisor(e.target.checked)} />
          É Supervisor?
        </label>
        {user.is_superuser && (
            <label>
              <input type="checkbox" checked={isSuperuser} onChange={(e) => setIsSuperuser(e.target.checked)} />
              É Superuser?
            </label>
        )}
        <button type="submit">Criar Usuário</button>
      </form>

      <h3>Lista de Usuários</h3>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul>
          {users.map((u) => (
            <li key={u.id}>
              {u.nome} ({u.email}) - Empresa: {u.empresa_id || 'N/A'} - Superuser: {u.is_superuser ? 'Sim' : 'Não'} - Supervisor: {u.is_supervisor ? 'Sim' : 'Não'}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default UserManagementPage;

