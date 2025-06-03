import React, { useState, useEffect } from 'react';
import { getCompanies, createCompany } from '../services/api'; // Assuming API functions exist
import { useAuth } from '../contexts/AuthContext';

function CompanyManagementPage() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth(); // Get current user info

  // State for creating a new company
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newCompanyCnpj, setNewCompanyCnpj] = useState(''); // Optional field

  useEffect(() => {
    const fetchCompanies = async () => {
      // Only superusers can fetch all companies
      if (user?.is_superuser) {
        try {
          setLoading(true);
          const data = await getCompanies();
          setCompanies(data);
          setError('');
        } catch (err) {
          setError('Falha ao carregar empresas.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      } else {
        setCompanies([]); // Non-superusers don't see this list
        setLoading(false);
      }
    };

    fetchCompanies();
  }, [user]); // Refetch if user changes

  const handleCreateCompany = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const companyData = {
        nome: newCompanyName,
        cnpj: newCompanyCnpj || null, // Send null if empty
        is_active: true, // Default to active
        // plano_id and data_expiracao_plano will be handled later or by default in backend
      };
      const createdCompany = await createCompany(companyData);
      setCompanies([...companies, createdCompany]); // Add new company to the list
      // Clear form
      setNewCompanyName('');
      setNewCompanyCnpj('');
    } catch (err) {
      setError(`Falha ao criar empresa: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    }
  };

  // Render logic - Only show management features to superusers
  if (!user?.is_superuser) {
    return <div>Acesso restrito a Superusuários.</div>;
  }

  return (
    <div>
      <h2>Gerenciamento de Empresas (Superuser)</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <h3>Criar Nova Empresa</h3>
      <form onSubmit={handleCreateCompany}>
        <input type="text" value={newCompanyName} onChange={(e) => setNewCompanyName(e.target.value)} placeholder="Nome da Empresa" required />
        <input type="text" value={newCompanyCnpj} onChange={(e) => setNewCompanyCnpj(e.target.value)} placeholder="CNPJ (opcional)" />
        <button type="submit">Criar Empresa</button>
      </form>

      <h3>Lista de Empresas</h3>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul>
          {companies.map((c) => (
            <li key={c.id}>
              {c.nome} (ID: {c.id}, CNPJ: {c.cnpj || 'N/A'}) - Ativa: {c.is_active ? 'Sim' : 'Não'}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default CompanyManagementPage;

