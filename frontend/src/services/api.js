import axios from 'axios';
import { jwtDecode } from 'jwt-decode'; // Import jwt-decode

// Determine the backend URL based on environment
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
});

// Function to get user info from token
const getUserInfoFromToken = () => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        try {
            return jwtDecode(token);
        } catch (error) {
            console.error("Failed to decode token:", error);
            return null;
        }
    }
    return null;
};

// Interceptor to add the JWT token to requests if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Authentication --- 
export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  try {
    const response = await apiClient.post('/login/access-token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    if (response.data.access_token) {
      localStorage.setItem('accessToken', response.data.access_token);
      // Store decoded user info as well
      const decoded = jwtDecode(response.data.access_token);
      localStorage.setItem('userInfo', JSON.stringify(decoded)); 
    }
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response || error.message);
    localStorage.removeItem('accessToken'); // Clear token on failure
    localStorage.removeItem('userInfo');
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('userInfo');
};

export const getCurrentUser = async () => {
    try {
        const response = await apiClient.get('/usuarios/me');
        return response.data;
    } catch (error) {
        console.error('Failed to get current user:', error.response || error.message);
        logout(); // Log out the user if fetching fails
        throw error;
    }
};

// --- User Management --- 
export const getUsers = async (skip = 0, limit = 100) => {
    try {
        const response = await apiClient.get(`/usuarios/?skip=${skip}&limit=${limit}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get users:', error.response || error.message);
        throw error;
    }
};

export const createUser = async (userData) => {
    try {
        const response = await apiClient.post('/usuarios/', userData);
        return response.data;
    } catch (error) {
        console.error('Failed to create user:', error.response || error.message);
        throw error;
    }
};

// --- Company Management --- 
export const getCompanies = async (skip = 0, limit = 100) => {
    try {
        // Assuming superuser access is checked by the backend endpoint
        const response = await apiClient.get(`/empresas/?skip=${skip}&limit=${limit}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get companies:', error.response || error.message);
        throw error;
    }
};

export const createCompany = async (companyData) => {
    try {
        // Assuming superuser access is checked by the backend endpoint
        const response = await apiClient.post('/empresas/', companyData);
        return response.data;
    } catch (error) {
        console.error('Failed to create company:', error.response || error.message);
        throw error;
    }
};

// --- CRM Services --- 
export const getBoards = async () => {
    try {
        const response = await apiClient.get('/crm/boards/');
        return response.data;
    } catch (error) {
        console.error('Failed to get boards:', error.response || error.message);
        throw error;
    }
};

export const createBoard = async (boardData) => {
    try {
        const response = await apiClient.post('/crm/boards/', boardData);
        return response.data;
    } catch (error) {
        console.error('Failed to create board:', error.response || error.message);
        throw error;
    }
};

export const getColumnsByBoard = async (boardId) => {
    try {
        const response = await apiClient.get(`/crm/colunas/by_board/${boardId}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to get columns for board ${boardId}:`, error.response || error.message);
        throw error;
    }
};

export const createColumn = async (columnData) => {
    try {
        const response = await apiClient.post('/crm/colunas/', columnData);
        return response.data;
    } catch (error) {
        console.error('Failed to create column:', error.response || error.message);
        throw error;
    }
};

export const getCardsByColumn = async (columnId) => {
    try {
        const response = await apiClient.get(`/crm/cards/by_coluna/${columnId}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to get cards for column ${columnId}:`, error.response || error.message);
        throw error;
    }
};

export const createCard = async (cardData) => {
    try {
        const response = await apiClient.post('/crm/cards/', cardData);
        return response.data;
    } catch (error) {
        console.error('Failed to create card:', error.response || error.message);
        throw error;
    }
};

export const updateCard = async (cardId, cardData) => {
    try {
        const response = await apiClient.put(`/crm/cards/${cardId}`, cardData);
        return response.data;
    } catch (error) {
        console.error(`Failed to update card ${cardId}:`, error.response || error.message);
        throw error;
    }
};

// --- Evolution API Services --- 
export const getInstancias = async () => {
    try {
        const response = await apiClient.get('/evolution/');
        return response.data;
    } catch (error) {
        console.error('Failed to get instancias:', error.response || error.message);
        throw error;
    }
};

export const createInstancia = async (instanciaData) => {
    try {
        const response = await apiClient.post('/evolution/', instanciaData);
        return response.data;
    } catch (error) {
        console.error('Failed to create instancia:', error.response || error.message);
        throw error;
    }
};

export const connectInstancia = async (instanciaId) => {
    try {
        const response = await apiClient.post(`/evolution/${instanciaId}/connect`);
        return response.data; // Should contain { qr_code, status }
    } catch (error) {
        console.error(`Failed to connect instancia ${instanciaId}:`, error.response || error.message);
        throw error;
    }
};

export const sendEvolutionMessage = async (instanciaId, messagePayload) => {
    try {
        const response = await apiClient.post(`/evolution/${instanciaId}/send`, messagePayload);
        return response.data;
    } catch (error) {
        console.error(`Failed to send message via instancia ${instanciaId}:`, error.response || error.message);
        throw error;
    }
};


// Export the utility function if needed elsewhere
export { getUserInfoFromToken };

export default apiClient;

