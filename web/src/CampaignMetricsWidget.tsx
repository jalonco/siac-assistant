import React, { useState, useEffect } from 'react';

/**
 * ChatGPT Skybridge API Types for Fullscreen Mode
 * These types define the interface for communicating with ChatGPT's iframe environment
 */
interface OpenAiGlobal {
  toolOutput?: {
    campaign_id: string;
    delivery_rate: number;
    status: 'COMPLETED' | 'RUNNING' | 'FAILED' | 'PAUSED_META';
    quality_score: 'GREEN' | 'YELLOW' | 'RED' | 'UNKNOWN';
    total_sent: number;
    delivered: number;
    failed: number;
    performance_metrics?: {
      delivery_rate: number;
      open_rate: number;
      click_rate: number;
      response_rate: number;
    };
    quality_metrics?: {
      quality_score: string;
      spam_score: number;
      engagement_score: number;
    };
    timeline?: {
      started_at: string;
      completed_at?: string;
      duration_hours?: number;
    };
    cost_analysis?: {
      total_cost: number;
      cost_per_message: number;
      cost_per_delivery: number;
    };
    pacing_status?: {
      template_pacing_active: boolean;
      held_messages: number;
      pacing_reason?: string;
    };
    meta_errors?: Array<{
      error_code: number;
      error_message: string;
      count: number;
    }>;
  };
  widgetState?: {
    campaign_id: string;
    time_filter: '7d' | '30d' | '90d' | 'all';
    selected_metric: 'delivery' | 'engagement' | 'cost';
    last_updated: string;
  };
  setWidgetState: (state: any) => Promise<void>;
  requestDisplayMode: (mode: 'inline' | 'fullscreen') => Promise<void>;
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
 * CampaignMetricsWidget Component Props
 */
interface CampaignMetricsWidgetProps {
  // Optional props for testing/development
  mockData?: {
    toolOutput?: OpenAiGlobal['toolOutput'];
    widgetState?: OpenAiGlobal['widgetState'];
  };
}

/**
 * CampaignMetricsWidget Component
 * 
 * This component displays comprehensive campaign metrics in fullscreen mode,
 * including quality scores, delivery metrics, and Meta compliance information.
 */
const CampaignMetricsWidget: React.FC<CampaignMetricsWidgetProps> = ({ mockData }) => {
  const { openAiApi, isLoading } = useOpenAiGlobal();
  
  // Use mock data for development/testing, otherwise use ChatGPT API data
  const toolOutput = mockData?.toolOutput || openAiApi?.toolOutput;
  const initialWidgetState = mockData?.widgetState || openAiApi?.widgetState;

  // Component state
  const [timeFilter, setTimeFilter] = useState<'7d' | '30d' | '90d' | 'all'>('30d');
  const [selectedMetric, setSelectedMetric] = useState<'delivery' | 'engagement' | 'cost'>('delivery');
  const [isUpdating, setIsUpdating] = useState(false);

  // Default data for demonstration when no API data is available
  const defaultData = {
    toolOutput: {
      campaign_id: 'campaign_welcome_offer_123456',
      delivery_rate: 0.95,
      status: 'COMPLETED' as const,
      quality_score: 'GREEN' as const,
      total_sent: 1250,
      delivered: 1187,
      failed: 63,
      performance_metrics: {
        delivery_rate: 0.95,
        open_rate: 0.23,
        click_rate: 0.05,
        response_rate: 0.02
      },
      quality_metrics: {
        quality_score: 'GREEN',
        spam_score: 0.01,
        engagement_score: 0.15
      },
      timeline: {
        started_at: '2024-01-20T10:00:00Z',
        completed_at: '2024-01-20T18:30:00Z',
        duration_hours: 8.5
      },
      cost_analysis: {
        total_cost: 18.75,
        cost_per_message: 0.015,
        cost_per_delivery: 0.016
      },
      pacing_status: {
        template_pacing_active: false,
        held_messages: 0
      },
      meta_errors: []
    },
    widgetState: {
      campaign_id: 'campaign_welcome_offer_123456',
      time_filter: '30d' as const,
      selected_metric: 'delivery' as const,
      last_updated: new Date().toISOString()
    }
  };

  const data = {
    toolOutput: toolOutput || defaultData.toolOutput,
    widgetState: initialWidgetState || defaultData.widgetState
  };

  // Initialize state from widget state
  useEffect(() => {
    if (data.widgetState) {
      setTimeFilter(data.widgetState.time_filter);
      setSelectedMetric(data.widgetState.selected_metric);
    }
  }, [data.widgetState]);

  /**
   * Save widget state to persist user preferences
   */
  const saveWidgetState = async (newState: Partial<typeof data.widgetState>) => {
    if (!openAiApi?.setWidgetState) {
      console.log('Mock: Saving widget state:', newState);
      return;
    }

    const stateToSave = {
      campaign_id: data.toolOutput.campaign_id,
      time_filter: timeFilter,
      selected_metric: selectedMetric,
      last_updated: new Date().toISOString(),
      ...newState
    };

    try {
      await openAiApi.setWidgetState(stateToSave);
    } catch (error) {
      console.error('Error saving widget state:', error);
    }
  };

  /**
   * Handle time filter change
   */
  const handleTimeFilterChange = async (newFilter: typeof timeFilter) => {
    setTimeFilter(newFilter);
    setIsUpdating(true);
    
    await saveWidgetState({ time_filter: newFilter });
    
    // Simulate data refresh
    setTimeout(() => {
      setIsUpdating(false);
    }, 1000);
  };

  /**
   * Handle metric selection change
   */
  const handleMetricChange = async (newMetric: typeof selectedMetric) => {
    setSelectedMetric(newMetric);
    await saveWidgetState({ selected_metric: newMetric });
  };

  /**
   * Get quality score display information
   */
  const getQualityScoreInfo = (score: string) => {
    switch (score) {
      case 'GREEN':
        return {
          color: '#059669',
          bgColor: '#D1FAE5',
          borderColor: '#BBF7D0',
          icon: '✅',
          label: 'Excelente',
          description: 'La plantilla mantiene una calidad óptima'
        };
      case 'YELLOW':
        return {
          color: '#D97706',
          bgColor: '#FEF3C7',
          borderColor: '#FDE68A',
          icon: '⚠️',
          label: 'Advertencia',
          description: 'Riesgo de pausa por baja calidad'
        };
      case 'RED':
        return {
          color: '#DC2626',
          bgColor: '#FEE2E2',
          borderColor: '#FECACA',
          icon: '🚨',
          label: 'Crítico',
          description: 'Pausa inminente por baja calidad'
        };
      case 'UNKNOWN':
        return {
          color: '#6B7280',
          bgColor: '#F3F4F6',
          borderColor: '#D1D5DB',
          icon: '❓',
          label: 'Pendiente',
          description: 'Evaluación de calidad en progreso'
        };
      default:
        return {
          color: '#6B7280',
          bgColor: '#F3F4F6',
          borderColor: '#D1D5DB',
          icon: '❓',
          label: 'Desconocido',
          description: 'Estado de calidad no disponible'
        };
    }
  };

  /**
   * Get campaign status display information
   */
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return { color: '#059669', icon: '✅', label: 'Completada' };
      case 'RUNNING':
        return { color: '#3B82F6', icon: '🔄', label: 'En Progreso' };
      case 'FAILED':
        return { color: '#DC2626', icon: '❌', label: 'Fallida' };
      case 'PAUSED_META':
        return { color: '#D97706', icon: '⏸️', label: 'Pausada por Meta' };
      default:
        return { color: '#6B7280', icon: '❓', label: 'Desconocido' };
    }
  };

  /**
   * Format numbers for display
   */
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-ES').format(num);
  };

  /**
   * Format percentage for display
   */
  const formatPercentage = (num: number) => {
    return `${(num * 100).toFixed(1)}%`;
  };

  /**
   * Format currency for display
   */
  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(num);
  };

  // Loading state
  if (isLoading && !mockData) {
    return (
      <div style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#F8FAFC',
        color: '#6B7280'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>📊</div>
          <div>Cargando métricas de campaña...</div>
        </div>
      </div>
    );
  }

  const qualityInfo = getQualityScoreInfo(data.toolOutput.quality_score);
  const statusInfo = getStatusInfo(data.toolOutput.status);

  return (
    <div style={{
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      minHeight: '100vh',
      backgroundColor: '#F8FAFC',
      padding: '24px',
      color: '#111827'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        border: '1px solid #E5E7EB',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827'
            }}>
              Dashboard de Métricas
            </h1>
            <p style={{
              margin: '4px 0 0 0',
              fontSize: '16px',
              color: '#6B7280'
            }}>
              Campaña: {data.toolOutput.campaign_id}
            </p>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: statusInfo.color + '20',
              borderRadius: '8px',
              border: `1px solid ${statusInfo.color}40`
            }}>
              <span style={{ fontSize: '16px' }}>{statusInfo.icon}</span>
              <span style={{
                fontSize: '14px',
                fontWeight: '500',
                color: statusInfo.color
              }}>
                {statusInfo.label}
              </span>
            </div>
          </div>
        </div>

        {/* Quality Score Alert */}
        <div style={{
          backgroundColor: qualityInfo.bgColor,
          border: `1px solid ${qualityInfo.borderColor}`,
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '20px' }}>{qualityInfo.icon}</span>
            <span style={{
              fontSize: '16px',
              fontWeight: '600',
              color: qualityInfo.color
            }}>
              Calidad de Plantilla: {qualityInfo.label}
            </span>
          </div>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: qualityInfo.color === '#059669' ? '#047857' : 
                   qualityInfo.color === '#D97706' ? '#B45309' : 
                   qualityInfo.color === '#DC2626' ? '#B91C1C' : '#6B7280'
          }}>
            {qualityInfo.description}
          </p>
        </div>

        {/* Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          <div>
            <label style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px',
              display: 'block'
            }}>
              Período de Tiempo
            </label>
            <select
              value={timeFilter}
              onChange={(e) => handleTimeFilterChange(e.target.value as typeof timeFilter)}
              disabled={isUpdating}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #D1D5DB',
                backgroundColor: '#FFFFFF',
                fontSize: '14px',
                cursor: isUpdating ? 'not-allowed' : 'pointer'
              }}
            >
              <option value="7d">Últimos 7 días</option>
              <option value="30d">Últimos 30 días</option>
              <option value="90d">Últimos 90 días</option>
              <option value="all">Todo el período</option>
            </select>
          </div>
          
          <div>
            <label style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px',
              display: 'block'
            }}>
              Métrica Principal
            </label>
            <select
              value={selectedMetric}
              onChange={(e) => handleMetricChange(e.target.value as typeof selectedMetric)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #D1D5DB',
                backgroundColor: '#FFFFFF',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              <option value="delivery">Entrega</option>
              <option value="engagement">Engagement</option>
              <option value="cost">Costo</option>
            </select>
          </div>

          {isUpdating && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#6B7280',
              fontSize: '14px'
            }}>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #E5E7EB',
                borderTop: '2px solid #3B82F6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              Actualizando...
            </div>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        marginBottom: '24px'
      }}>
        {/* Delivery Metrics */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E5E7EB',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            margin: '0 0 16px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            📤 Métricas de Entrega
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Total Enviados
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#111827'
              }}>
                {formatNumber(data.toolOutput.total_sent)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Entregados
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#059669'
              }}>
                {formatNumber(data.toolOutput.delivered)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Fallidos
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#DC2626'
              }}>
                {formatNumber(data.toolOutput.failed)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Tasa de Entrega
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#3B82F6'
              }}>
                {formatPercentage(data.toolOutput.delivery_rate)}
              </div>
            </div>
          </div>
        </div>

        {/* Engagement Metrics */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E5E7EB',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            margin: '0 0 16px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            👥 Engagement
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Tasa de Apertura
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#8B5CF6'
              }}>
                {formatPercentage(data.toolOutput.performance_metrics?.open_rate || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Tasa de Clic
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#F59E0B'
              }}>
                {formatPercentage(data.toolOutput.performance_metrics?.click_rate || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Tasa de Respuesta
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#10B981'
              }}>
                {formatPercentage(data.toolOutput.performance_metrics?.response_rate || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Score de Engagement
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#EC4899'
              }}>
                {formatPercentage(data.toolOutput.quality_metrics?.engagement_score || 0)}
              </div>
            </div>
          </div>
        </div>

        {/* Cost Analysis */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E5E7EB',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            margin: '0 0 16px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            💰 Análisis de Costo
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px'
          }}>
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Costo Total
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#111827'
              }}>
                {formatCurrency(data.toolOutput.cost_analysis?.total_cost || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Costo por Mensaje
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#3B82F6'
              }}>
                {formatCurrency(data.toolOutput.cost_analysis?.cost_per_message || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Costo por Entrega
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#059669'
              }}>
                {formatCurrency(data.toolOutput.cost_analysis?.cost_per_delivery || 0)}
              </div>
            </div>
            
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                ROI Estimado
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#10B981'
              }}>
                +{((data.toolOutput.performance_metrics?.response_rate || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Control State and Errors */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid #E5E7EB',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        marginBottom: '24px'
      }}>
        <h3 style={{
          margin: '0 0 16px 0',
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          🛡️ Estado de Control y Errores
        </h3>

        {/* Template Pacing */}
        {data.toolOutput.pacing_status?.template_pacing_active && (
          <div style={{
            backgroundColor: '#FEF3C7',
            border: '1px solid #FDE68A',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '16px' }}>⏳</span>
              <span style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#D97706'
              }}>
                Template Pacing Activo
              </span>
            </div>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: '#B45309'
            }}>
              {data.toolOutput.pacing_status.held_messages} mensajes retenidos para evaluación de calidad.
              {data.toolOutput.pacing_status.pacing_reason && ` Razón: ${data.toolOutput.pacing_status.pacing_reason}`}
            </p>
          </div>
        )}

        {/* Meta Error 131049 */}
        {data.toolOutput.meta_errors?.some(error => error.error_code === 131049) && (
          <div style={{
            backgroundColor: '#FEE2E2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '16px' }}>🚨</span>
              <span style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#DC2626'
              }}>
                Error Meta 131049: Límite de Marketing
              </span>
            </div>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: '#B91C1C'
            }}>
              El envío masivo falló debido a límites de mensajes de marketing por usuario. 
              Meta ha aplicado restricciones para proteger la experiencia del usuario.
            </p>
          </div>
        )}

        {/* Other Meta Errors */}
        {data.toolOutput.meta_errors?.filter(error => error.error_code !== 131049).map((error, index) => (
          <div key={index} style={{
            backgroundColor: '#F3F4F6',
            border: '1px solid #D1D5DB',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '8px'
          }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>
              Error {error.error_code}: {error.error_message}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6B7280'
            }}>
              Ocurrencias: {error.count}
            </div>
          </div>
        ))}
      </div>

      {/* Timeline */}
      {data.toolOutput.timeline && (
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E5E7EB',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            margin: '0 0 16px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            ⏰ Cronología de Campaña
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '4px'
              }}>
                Iniciada
              </div>
              <div style={{
                fontSize: '14px',
                fontWeight: '500',
                color: '#111827'
              }}>
                {new Date(data.toolOutput.timeline.started_at).toLocaleString('es-ES')}
              </div>
            </div>
            
            {data.toolOutput.timeline.completed_at && (
              <div>
                <div style={{
                  fontSize: '12px',
                  color: '#6B7280',
                  marginBottom: '4px'
                }}>
                  Completada
                </div>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#111827'
                }}>
                  {new Date(data.toolOutput.timeline.completed_at).toLocaleString('es-ES')}
                </div>
              </div>
            )}
            
            {data.toolOutput.timeline.duration_hours && (
              <div>
                <div style={{
                  fontSize: '12px',
                  color: '#6B7280',
                  marginBottom: '4px'
                }}>
                  Duración
                </div>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#111827'
                }}>
                  {data.toolOutput.timeline.duration_hours}h
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* CSS Animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default CampaignMetricsWidget;



