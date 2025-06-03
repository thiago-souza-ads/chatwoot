import React, { useState, useEffect, useCallback } from 'react';
import { getInstancias, createInstancia, connectInstancia } from '../services/api'; // Assuming API functions exist
import { useAuth } from '../contexts/AuthContext';
import useWebSocket from '../hooks/useWebSocket'; // Import WebSocket hook

// Determine WebSocket URL based on API_URL (replace http with ws/wss)
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const WS_URL_BASE = API_URL.replace(/^http/, 'ws');

function InstanciaCard({ instancia, onConnect, qrCodeData }) {
    const [isConnecting, setIsConnecting] = useState(false);
    const [connectError, setConnectError] = useState('');

    const handleConnectClick = async () => {
        setIsConnecting(true);
        setConnectError('');
        try {
            await onConnect(instancia.id);
            // QR code will be displayed by the parent component based on qrCodeData
        } catch (err) {
            setConnectError(`Falha ao conectar: ${err.response?.data?.detail || err.message}`);
        } finally {
            // Keep loading state until QR code is received or timeout?
            // For now, just stop loading after the call
            // setIsConnecting(false); // Let parent handle this based on qrCodeData
        }
    };

    return (
        <div style={{ border: '1px solid #eee', padding: '10px', marginBottom: '10px', borderRadius: '5px' }}>
            <h4>{instancia.nome_instancia}</h4>
            <p><strong>ID:</strong> {instancia.id}</p>
            <p><strong>URL API:</strong> {instancia.evolution_api_url}</p>
            <p><strong>Status:</strong> {instancia.status || 'Desconhecido'}</p>
            <p><strong>Última Atualização Status:</strong> {instancia.status_timestamp ? new Date(instancia.status_timestamp).toLocaleString() : 'N/A'}</p>
            
            {/* Display QR Code if it belongs to this instance */} 
            {qrCodeData && qrCodeData.instance_id === instancia.id && qrCodeData.qr_code && (
                <div style={{ marginTop: '10px' }}>
                    <p><strong>Escaneie o QR Code:</strong></p>
                    <img src={qrCodeData.qr_code} alt="QR Code" style={{ maxWidth: '200px' }} />
                </div>
            )}

            {/* Connect Button */} 
            {instancia.status !== 'connected' && (
                 <button onClick={handleConnectClick} disabled={isConnecting || (qrCodeData && qrCodeData.instance_id === instancia.id)}>
                    {isConnecting ? 'Conectando...' : 'Conectar / Obter QR Code'}
                </button>
            )}
           
            {connectError && <p style={{ color: 'red', marginTop: '5px' }}>{connectError}</p>}
        </div>
    );
}

function InstanciasPage() {
    const [instancias, setInstancias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user } = useAuth();

    // State for creating a new instancia
    const [newInstanceName, setNewInstanceName] = useState('');
    const [newInstanceUrl, setNewInstanceUrl] = useState('');
    const [newInstanceApiKey, setNewInstanceApiKey] = useState('');

    // State for QR Code display
    const [qrCodeData, setQrCodeData] = useState(null); // { instance_id: number, qr_code: string }

    // WebSocket connection for status updates
    const wsUrl = user ? `${WS_URL_BASE}/ws/${user.empresa_id || 0}/${user.id}` : null;
    const { lastMessage } = useWebSocket(wsUrl);

    // Fetch initial instances
    const fetchInstancias = useCallback(async () => {
        if (!user?.empresa_id && !user?.is_superuser) { // Allow superuser to see all?
             setError('Usuário não associado a uma empresa.');
             setLoading(false);
             return;
        }
        try {
            setLoading(true);
            const data = await getInstancias(); // API fetches instances for the current user's company
            setInstancias(data);
            setError('');
        } catch (err) {
            setError('Falha ao carregar instâncias.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        fetchInstancias();
    }, [fetchInstancias]);

    // Handle WebSocket messages for status updates and QR codes
    useEffect(() => {
        if (lastMessage) {
            if (lastMessage.type === 'instance_status_update') {
                console.log("Instance status update received:", lastMessage);
                setInstancias(prevInstancias =>
                    prevInstancias.map(inst =>
                        inst.id === lastMessage.instance_id
                            ? { ...inst, status: lastMessage.status, status_timestamp: new Date().toISOString() }
                            : inst
                    )
                );
                // Clear QR code if status changes (e.g., to connected)
                if (qrCodeData && qrCodeData.instance_id === lastMessage.instance_id && lastMessage.status !== 'qrcode') {
                    setQrCodeData(null);
                }
            } else if (lastMessage.type === 'instance_qr_code') {
                 console.log("QR Code received:", lastMessage);
                 setQrCodeData({ instance_id: lastMessage.instance_id, qr_code: lastMessage.qr_code });
            }
        }
    }, [lastMessage, qrCodeData]);

    const handleCreateInstancia = async (e) => {
        e.preventDefault();
        setError('');
        setQrCodeData(null); // Clear any previous QR code
        try {
            const instanciaData = {
                nome_instancia: newInstanceName,
                evolution_api_url: newInstanceUrl,
                evolution_api_key: newInstanceApiKey,
                // empresa_id is automatically set by the backend based on the user's token
            };
            const createdInstancia = await createInstancia(instanciaData);
            setInstancias([...instancias, createdInstancia]);
            // Clear form
            setNewInstanceName('');
            setNewInstanceUrl('');
            setNewInstanceApiKey('');
        } catch (err) {
            setError(`Falha ao criar instância: ${err.response?.data?.detail || err.message}`);
            console.error(err);
        }
    };

    const handleConnect = async (instanciaId) => {
        setQrCodeData(null); // Clear previous QR code before requesting new one
        try {
            const result = await connectInstancia(instanciaId);
            // QR code might be in result or come via WebSocket
            if (result && result.qr_code) {
                 setQrCodeData({ instance_id: instanciaId, qr_code: result.qr_code });
            } else {
                // Assume QR code will arrive via WebSocket
                console.log("Connect request sent, waiting for QR code via WebSocket...");
            }
        } catch (err) {
            setError(`Falha ao iniciar conexão para instância ${instanciaId}.`);
            console.error(err);
            throw err; // Re-throw to be caught by InstanciaCard
        }
    };

    return (
        <div>
            <h2>Gerenciamento de Instâncias Evolution API</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {/* Form to Create New Instance */} 
            <h3>Criar Nova Instância</h3>
            <form onSubmit={handleCreateInstancia} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
                <div style={{ marginBottom: '10px' }}>
                    <label>Nome da Instância: </label>
                    <input type="text" value={newInstanceName} onChange={(e) => setNewInstanceName(e.target.value)} required />
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <label>URL da API Evolution: </label>
                    <input type="url" value={newInstanceUrl} onChange={(e) => setNewInstanceUrl(e.target.value)} placeholder="http://..." required />
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <label>API Key da Evolution: </label>
                    <input type="text" value={newInstanceApiKey} onChange={(e) => setNewInstanceApiKey(e.target.value)} required />
                </div>
                <button type="submit">Criar Instância</button>
            </form>

            {/* List of Existing Instances */} 
            <h3>Instâncias Existentes</h3>
            {loading ? (
                <p>Carregando instâncias...</p>
            ) : instancias.length === 0 ? (
                <p>Nenhuma instância criada ainda.</p>
            ) : (
                instancias.map((inst) => (
                    <InstanciaCard 
                        key={inst.id} 
                        instancia={inst} 
                        onConnect={handleConnect} 
                        qrCodeData={qrCodeData} 
                    />
                ))
            )}
        </div>
    );
}

export default InstanciasPage;

