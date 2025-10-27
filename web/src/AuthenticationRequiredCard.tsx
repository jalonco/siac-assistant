import React, { useState, useEffect } from 'react';

/**
 * ChatGPT Skybridge API Types
 * These types define the interface for communicating with ChatGPT's iframe environment
 */
interface OpenAiGlobal {
  toolOutput?: {
    authentication_required: boolean;
    error_message?: string;
    auth_url?: string;
  };
  sendFollowUpMessage: (message: string) => Promise<void>;
}

/**
 * Custom hook to access ChatGPT Skybridge API
 * This hook provides access to the window.openai global object
 */
const useOpenAiGlobal = () => {
  const [openAiApi, setOpenAiApi] = useState<OpenAiGlobal | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Access the ChatGPT Skybridge API
    const checkForOpenAiApi = () => {
      if (typeof window !== 'undefined' && (window as any).openai) {
        const api = (window as any).openai as OpenAiGlobal;
        setOpenAiApi(api);
        setIsLoading(false);
      } else {
        // Retry after a short delay if API is not yet available
        setTimeout(checkForOpenAiApi, 100);
      }
    };

    checkForOpenAiApi();
  }, []);

  return { openAiApi, isLoading };
};

/**
 * AuthenticationRequiredCard Component Props
 */
interface AuthenticationRequiredCardProps {
  // Optional props for testing/development
  mockData?: {
    toolOutput?: OpenAiGlobal['toolOutput'];
  };
}

/**
 * AuthenticationRequiredCard Component
 * 
 * This component is designed to activate OAuth 2.1 with PKCE authentication flow.
 * It renders automatically when the MCP server fails token verification and responds
 * with 401 Unauthorized and WWW-Authenticate header.
 */
const AuthenticationRequiredCard: React.FC<AuthenticationRequiredCardProps> = ({ mockData }) => {
  const { openAiApi, isLoading } = useOpenAiGlobal();
  const [isProcessing, setIsProcessing] = useState(false);

  // Use mock data for development/testing, otherwise use ChatGPT API data
  const toolOutput = mockData?.toolOutput || openAiApi?.toolOutput;

  // Default data for demonstration when no API data is available
  const defaultData = {
    toolOutput: {
      authentication_required: true,
      error_message: 'Authentication required to access SIAC resources',
      auth_url: 'https://auth.siac-app.com/oauth/authorize'
    }
  };

  const data = {
    toolOutput: toolOutput || defaultData.toolOutput
  };

  /**
   * Handle SIAC account connection
   * This triggers the OAuth flow managed by ChatGPT client
   */
  const handleConnectAccount = async () => {
    if (!openAiApi?.sendFollowUpMessage) {
      console.log('Mock: Initiating SIAC account connection');
      return;
    }

    setIsProcessing(true);
    try {
      // Send a message that will trigger ChatGPT to handle OAuth flow
      await openAiApi.sendFollowUpMessage('I need to connect my SIAC account to access WhatsApp template management features. Please help me authenticate with SIAC.');
    } catch (error) {
      console.error('Error initiating authentication:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Loading state
  if (isLoading && !mockData) {
    return (
      <div style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        maxWidth: '400px',
        margin: '0 auto',
        padding: '20px',
        textAlign: 'center',
        color: '#6B7280'
      }}>
        Loading authentication...
      </div>
    );
  }

  return (
    <div style={{
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      maxWidth: '400px',
      margin: '0 auto',
      padding: '20px',
      backgroundColor: '#FFFFFF',
      borderRadius: '12px',
      border: '1px solid #E5E7EB',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid #E5E7EB'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            backgroundColor: '#FEF2F2',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #FECACA'
          }}>
            <span style={{ fontSize: '24px' }}>🔐</span>
          </div>
          <div>
            <h3 style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827'
            }}>
              Autenticación Requerida
            </h3>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: '#6B7280',
              marginTop: '2px'
            }}>
              SIAC Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Authentication Message */}
      <div style={{
        backgroundColor: '#FEF2F2',
        border: '1px solid #FECACA',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '20px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            backgroundColor: '#FEE2E2',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginTop: '2px'
          }}>
            <span style={{ fontSize: '12px', color: '#DC2626' }}>!</span>
          </div>
          <div>
            <h4 style={{
              margin: 0,
              fontSize: '16px',
              fontWeight: '600',
              color: '#DC2626',
              marginBottom: '8px'
            }}>
              Acceso Restringido
            </h4>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: '#B91C1C',
              lineHeight: '1.5'
            }}>
              Para acceder a las funciones de gestión de plantillas de WhatsApp y campañas, 
              necesitas conectar tu cuenta de SIAC.
            </p>
          </div>
        </div>
      </div>

      {/* Features List */}
      <div style={{
        marginBottom: '20px'
      }}>
        <h4 style={{
          margin: 0,
          fontSize: '14px',
          fontWeight: '600',
          color: '#374151',
          marginBottom: '12px'
        }}>
          Con la autenticación podrás:
        </h4>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#4B5563'
          }}>
            <span style={{ fontSize: '16px' }}>✅</span>
            <span>Validar plantillas de WhatsApp</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#4B5563'
          }}>
            <span style={{ fontSize: '16px' }}>✅</span>
            <span>Registrar plantillas en Meta</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#4B5563'
          }}>
            <span style={{ fontSize: '16px' }}>✅</span>
            <span>Programar campañas de difusión</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#4B5563'
          }}>
            <span style={{ fontSize: '16px' }}>✅</span>
            <span>Monitorear métricas de campañas</span>
          </div>
        </div>
      </div>

      {/* Security Information */}
      <div style={{
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '20px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '16px' }}>🛡️</span>
          <span style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#374151'
          }}>
            Seguridad Garantizada
          </span>
        </div>
        <p style={{
          margin: 0,
          fontSize: '12px',
          color: '#6B7280',
          lineHeight: '1.4'
        }}>
          Utilizamos OAuth 2.1 con PKCE para una autenticación segura. 
          Tus credenciales nunca se almacenan en ChatGPT.
        </p>
      </div>

      {/* Action Button */}
      <button
        onClick={handleConnectAccount}
        disabled={isProcessing}
        style={{
          width: '100%',
          backgroundColor: isProcessing ? '#9CA3AF' : '#10B981',
          color: '#FFFFFF',
          border: 'none',
          borderRadius: '8px',
          padding: '12px 16px',
          fontSize: '14px',
          fontWeight: '500',
          cursor: isProcessing ? 'not-allowed' : 'pointer',
          transition: 'background-color 0.2s'
        }}
        onMouseOver={(e) => {
          if (!isProcessing) {
            e.currentTarget.style.backgroundColor = '#059669';
          }
        }}
        onMouseOut={(e) => {
          if (!isProcessing) {
            e.currentTarget.style.backgroundColor = '#10B981';
          }
        }}
      >
        {isProcessing ? 'Conectando...' : 'Conectar Cuenta SIAC'}
      </button>

      {/* Footer */}
      <div style={{
        marginTop: '16px',
        paddingTop: '12px',
        borderTop: '1px solid #E5E7EB',
        fontSize: '12px',
        color: '#6B7280',
        textAlign: 'center'
      }}>
        SIAC Assistant • Authentication Required
      </div>
    </div>
  );
};

export default AuthenticationRequiredCard;



