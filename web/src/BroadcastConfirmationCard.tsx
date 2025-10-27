import React, { useState, useEffect } from 'react';

/**
 * ChatGPT Skybridge API Types
 * These types define the interface for communicating with ChatGPT's iframe environment
 */
interface OpenAiGlobal {
  toolOutput?: {
    campaign_id: string;
    template_id: string;
    segment_name: string;
    schedule_time_utc: string;
    status: 'SCHEDULED' | 'SCHEDULED_TEST' | 'SCHEDULING_FAILED';
    estimated_recipients: number;
    scheduled_at: string;
  };
  requestDisplayMode: (mode: 'fullscreen') => Promise<void>;
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
 * BroadcastConfirmationCard Component Props
 */
interface BroadcastConfirmationCardProps {
  // Optional props for testing/development
  mockData?: {
    toolOutput?: OpenAiGlobal['toolOutput'];
  };
}

/**
 * BroadcastConfirmationCard Component
 * 
 * This component displays confirmation of a scheduled broadcast campaign
 * and provides navigation to detailed metrics dashboard.
 */
const BroadcastConfirmationCard: React.FC<BroadcastConfirmationCardProps> = ({ mockData }) => {
  const { openAiApi, isLoading } = useOpenAiGlobal();
  const [isProcessing, setIsProcessing] = useState(false);

  // Use mock data for development/testing, otherwise use ChatGPT API data
  const toolOutput = mockData?.toolOutput || openAiApi?.toolOutput;

  // Default data for demonstration when no API data is available
  const defaultData = {
    toolOutput: {
      campaign_id: 'campaign_123_456789',
      template_id: 'template_welcome_offer',
      segment_name: 'clientes_recurrentes',
      schedule_time_utc: '2024-01-25T14:30:00Z',
      status: 'SCHEDULED' as const,
      estimated_recipients: 1250,
      scheduled_at: new Date().toISOString()
    }
  };

  const data = {
    toolOutput: toolOutput || defaultData.toolOutput
  };

  /**
   * Handle navigation to detailed metrics dashboard
   */
  const handleViewMetrics = async () => {
    if (!openAiApi?.requestDisplayMode) {
      console.log('Mock: Requesting fullscreen mode for metrics dashboard');
      return;
    }

    setIsProcessing(true);
    try {
      await openAiApi.requestDisplayMode('fullscreen');
    } catch (error) {
      console.error('Error requesting fullscreen mode:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * Format date/time for display
   */
  const formatDateTime = (utcString: string) => {
    try {
      const date = new Date(utcString);
      return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC'
      });
    } catch (error) {
      return utcString;
    }
  };

  /**
   * Get status display information
   */
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'SCHEDULED':
        return {
          icon: '📅',
          text: 'Programada',
          color: '#059669',
          bgColor: '#D1FAE5'
        };
      case 'SCHEDULED_TEST':
        return {
          icon: '🧪',
          text: 'Prueba Programada',
          color: '#D97706',
          bgColor: '#FEF3C7'
        };
      case 'SCHEDULING_FAILED':
        return {
          icon: '❌',
          text: 'Error de Programación',
          color: '#DC2626',
          bgColor: '#FEE2E2'
        };
      default:
        return {
          icon: '❓',
          text: 'Desconocido',
          color: '#6B7280',
          bgColor: '#F3F4F6'
        };
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
        Loading broadcast confirmation...
      </div>
    );
  }

  const statusInfo = getStatusInfo(data.toolOutput.status);

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
        justifyContent: 'space-between',
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid #E5E7EB'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827'
        }}>
          Campaña Programada
        </h3>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '16px' }}>
            {statusInfo.icon}
          </span>
          <span style={{
            fontSize: '12px',
            fontWeight: '500',
            color: statusInfo.color,
            backgroundColor: statusInfo.bgColor,
            padding: '4px 8px',
            borderRadius: '6px'
          }}>
            {statusInfo.text}
          </span>
        </div>
      </div>

      {/* Campaign Summary */}
      <div style={{
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#1E293B',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          📊 Resumen de la Campaña
        </div>
        
        {/* Campaign Details Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          fontSize: '13px'
        }}>
          <div>
            <div style={{
              color: '#6B7280',
              fontWeight: '500',
              marginBottom: '2px'
            }}>
              Plantilla
            </div>
            <div style={{
              color: '#111827',
              fontWeight: '500'
            }}>
              {data.toolOutput.template_id}
            </div>
          </div>
          
          <div>
            <div style={{
              color: '#6B7280',
              fontWeight: '500',
              marginBottom: '2px'
            }}>
              Segmento
            </div>
            <div style={{
              color: '#111827',
              fontWeight: '500'
            }}>
              {data.toolOutput.segment_name}
            </div>
          </div>
          
          <div>
            <div style={{
              color: '#6B7280',
              fontWeight: '500',
              marginBottom: '2px'
            }}>
              Fecha/Hora
            </div>
            <div style={{
              color: '#111827',
              fontWeight: '500'
            }}>
              {formatDateTime(data.toolOutput.schedule_time_utc)}
            </div>
          </div>
          
          <div>
            <div style={{
              color: '#6B7280',
              fontWeight: '500',
              marginBottom: '2px'
            }}>
              Destinatarios
            </div>
            <div style={{
              color: '#111827',
              fontWeight: '500'
            }}>
              {data.toolOutput.estimated_recipients.toLocaleString()}
            </div>
          </div>
        </div>
        
        {/* Campaign ID */}
        <div style={{
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #E2E8F0'
        }}>
          <div style={{
            color: '#6B7280',
            fontWeight: '500',
            fontSize: '12px',
            marginBottom: '4px'
          }}>
            ID de Campaña
          </div>
          <div style={{
            color: '#111827',
            fontWeight: '500',
            fontSize: '13px',
            fontFamily: 'Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
            backgroundColor: '#F1F5F9',
            padding: '6px 8px',
            borderRadius: '4px',
            border: '1px solid #E2E8F0'
          }}>
            {data.toolOutput.campaign_id}
          </div>
        </div>
      </div>

      {/* Status Message */}
      {data.toolOutput.status === 'SCHEDULED' && (
        <div style={{
          backgroundColor: '#F0FDF4',
          border: '1px solid #BBF7D0',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '16px' }}>✅</span>
            <span style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#059669'
            }}>
              Campaña Programada Exitosamente
            </span>
          </div>
          <p style={{
            margin: 0,
            fontSize: '13px',
            color: '#047857'
          }}>
            La campaña se ejecutará automáticamente en la fecha programada. 
            Puedes monitorear el progreso y métricas detalladas.
          </p>
        </div>
      )}

      {data.toolOutput.status === 'SCHEDULED_TEST' && (
        <div style={{
          backgroundColor: '#FEF3C7',
          border: '1px solid #FDE68A',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '16px' }}>🧪</span>
            <span style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#D97706'
            }}>
              Campaña de Prueba Programada
            </span>
          </div>
          <p style={{
            margin: 0,
            fontSize: '13px',
            color: '#B45309'
          }}>
            Esta es una campaña de prueba con un segmento limitado. 
            Ideal para validar el contenido antes del envío masivo.
          </p>
        </div>
      )}

      {data.toolOutput.status === 'SCHEDULING_FAILED' && (
        <div style={{
          backgroundColor: '#FEE2E2',
          border: '1px solid #FECACA',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '16px' }}>❌</span>
            <span style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#DC2626'
            }}>
              Error en la Programación
            </span>
          </div>
          <p style={{
            margin: 0,
            fontSize: '13px',
            color: '#B91C1C'
          }}>
            No se pudo programar la campaña. Por favor, revisa los parámetros 
            y vuelve a intentar.
          </p>
        </div>
      )}

      {/* Action Button */}
      {data.toolOutput.status !== 'SCHEDULING_FAILED' && (
        <button
          onClick={handleViewMetrics}
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
          {isProcessing ? 'Cargando...' : 'Ver Métricas Detalladas'}
        </button>
      )}

      {/* Footer */}
      <div style={{
        marginTop: '16px',
        paddingTop: '12px',
        borderTop: '1px solid #E5E7EB',
        fontSize: '12px',
        color: '#6B7280',
        textAlign: 'center'
      }}>
        SIAC Assistant • Broadcast Confirmation
      </div>
    </div>
  );
};

export default BroadcastConfirmationCard;



