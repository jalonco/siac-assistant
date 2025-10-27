import React, { useState, useEffect } from 'react';

/**
 * ChatGPT Skybridge API Types
 * These types define the interface for communicating with ChatGPT's iframe environment
 */
interface OpenAiGlobal {
  toolOutput?: {
    validation_status: 'SUCCESS' | 'FAILED';
    template_name: string;
    passed_internal_checks: boolean;
    category: string;
    language_code: string;
  };
  toolResponseMetadata?: {
    raw_payload_for_preview: {
      template_name: string;
      body_text: string;
      category: 'Marketing' | 'Utility' | 'Authentication';
      language_code: string;
      validation_rules_applied: string[];
      validation_timestamp: string;
      estimated_review_time: string;
    };
    template_html_mockup: string;
    raw_validation_errors?: {
      errors: Array<{
        field: string;
        message: string;
        severity: 'error' | 'warning';
        suggestion?: string;
      }>;
      overall_status: 'FAILED' | 'SUCCESS';
    };
  };
  callTool: (toolName: string, arguments: Record<string, any>) => Promise<any>;
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
 * TemplateValidationCard Component Props
 */
interface TemplateValidationCardProps {
  // Optional props for testing/development
  mockData?: {
    toolOutput?: OpenAiGlobal['toolOutput'];
    toolResponseMetadata?: OpenAiGlobal['toolResponseMetadata'];
  };
}

/**
 * TemplateValidationCard Component
 * 
 * This component reads template validation results from the MCP server
 * and orchestrates the conversational flow between error correction
 * and final template registration.
 */
const TemplateValidationCard: React.FC<TemplateValidationCardProps> = ({ mockData }) => {
  const { openAiApi, isLoading } = useOpenAiGlobal();
  const [isProcessing, setIsProcessing] = useState(false);

  // Use mock data for development/testing, otherwise use ChatGPT API data
  const toolOutput = mockData?.toolOutput || openAiApi?.toolOutput;
  const toolResponseMetadata = mockData?.toolResponseMetadata || openAiApi?.toolResponseMetadata;

  // Default data for demonstration when no API data is available
  const defaultData = {
    toolOutput: {
      validation_status: 'SUCCESS' as const,
      template_name: 'Welcome Message',
      passed_internal_checks: true,
      category: 'Marketing',
      language_code: 'es_ES'
    },
    toolResponseMetadata: {
      raw_payload_for_preview: {
        template_name: 'Welcome Message',
        body_text: 'Welcome to our service! This is a comprehensive welcome message with {{1}} and {{2}}.',
        category: 'Marketing' as const,
        language_code: 'es_ES',
        validation_rules_applied: ['Minimum length check', 'Spam content detection', 'Category-specific length limits'],
        validation_timestamp: new Date().toISOString(),
        estimated_review_time: '24-48 hours'
      },
      template_html_mockup: '<div class="template-preview">...</div>'
    }
  };

  const data = {
    toolOutput: toolOutput || defaultData.toolOutput,
    toolResponseMetadata: toolResponseMetadata || defaultData.toolResponseMetadata
  };

  /**
   * Handle template registration (SUCCESS scenario)
   */
  const handleRegisterTemplate = async () => {
    if (!openAiApi?.callTool) {
      console.log('Mock: Registering template');
      return;
    }

    setIsProcessing(true);
    try {
      await openAiApi.callTool('siac.register_template', {
        template_id: `template_${Date.now()}`,
        meta_template_id: `meta_template_${Date.now()}`,
        client_id: 'client_123'
      });
    } catch (error) {
      console.error('Error registering template:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * Handle error correction (FAILED scenario)
   */
  const handleCorrectPrompt = async () => {
    if (!openAiApi?.sendFollowUpMessage) {
      console.log('Mock: Sending correction message');
      return;
    }

    const errors = data.toolResponseMetadata?.raw_validation_errors?.errors || [];
    const errorMessages = errors.map(error => error.message).join(', ');
    const suggestions = errors.map(error => error.suggestion).filter(Boolean).join(' ');

    const correctionMessage = `I need to correct the template validation errors: ${errorMessages}. ${suggestions ? `Suggestions: ${suggestions}` : 'Please help me fix these issues.'}`;

    setIsProcessing(true);
    try {
      await openAiApi.sendFollowUpMessage(correctionMessage);
    } catch (error) {
      console.error('Error sending correction message:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * Render WhatsApp template preview
   */
  const renderTemplatePreview = () => {
    const preview = data.toolResponseMetadata?.raw_payload_for_preview;
    if (!preview) return null;

    return (
      <div style={{
        backgroundColor: '#F0F9FF',
        border: '1px solid #E0F2FE',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#0369A1',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          📱 WhatsApp Template Preview
        </div>
        
        {/* Template Header */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '8px'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '500',
            color: '#6B7280',
            marginBottom: '4px'
          }}>
            Header
          </div>
          <div style={{
            fontSize: '14px',
            color: '#111827'
          }}>
            {preview.template_name}
          </div>
        </div>

        {/* Template Body */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '8px'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '500',
            color: '#6B7280',
            marginBottom: '4px'
          }}>
            Body
          </div>
          <div style={{
            fontSize: '14px',
            color: '#111827',
            lineHeight: '1.5'
          }}>
            {preview.body_text}
          </div>
        </div>

        {/* Template Footer */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          padding: '12px'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '500',
            color: '#6B7280',
            marginBottom: '4px'
          }}>
            Footer
          </div>
          <div style={{
            fontSize: '14px',
            color: '#111827'
          }}>
            {preview.category} • {preview.language_code}
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render validation errors
   */
  const renderValidationErrors = () => {
    const errors = data.toolResponseMetadata?.raw_validation_errors?.errors || [];
    if (errors.length === 0) return null;

    return (
      <div style={{
        backgroundColor: '#FEF2F2',
        border: '1px solid #FECACA',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#DC2626',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          ❌ Validation Errors
        </div>
        
        {errors.map((error, index) => (
          <div key={index} style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '8px'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: '500',
              color: '#DC2626',
              marginBottom: '4px'
            }}>
              {error.field}: {error.message}
            </div>
            {error.suggestion && (
              <div style={{
                fontSize: '12px',
                color: '#7F1D1D',
                fontStyle: 'italic'
              }}>
                💡 {error.suggestion}
              </div>
            )}
          </div>
        ))}
      </div>
    );
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
        Loading template validation...
      </div>
    );
  }

  const isSuccess = data.toolOutput.validation_status === 'SUCCESS';
  const isFailed = data.toolOutput.validation_status === 'FAILED';

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
          {data.toolOutput.template_name}
        </h3>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '16px' }}>
            {isSuccess ? '✅' : '❌'}
          </span>
          <span style={{
            fontSize: '12px',
            fontWeight: '500',
            color: isSuccess ? '#059669' : '#DC2626',
            backgroundColor: isSuccess ? '#D1FAE5' : '#FEE2E2',
            padding: '4px 8px',
            borderRadius: '6px'
          }}>
            {isSuccess ? 'VALIDATED' : 'FAILED'}
          </span>
        </div>
      </div>

      {/* SUCCESS Scenario */}
      {isSuccess && (
        <>
          {renderTemplatePreview()}
          
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
                Template Validation Successful
              </span>
            </div>
            <p style={{
              margin: 0,
              fontSize: '13px',
              color: '#047857'
            }}>
              The template passed all validation checks and is ready for registration in Meta.
            </p>
          </div>

          <button
            onClick={handleRegisterTemplate}
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
            {isProcessing ? 'Registering...' : 'Registrar Plantilla'}
          </button>
        </>
      )}

      {/* FAILED Scenario */}
      {isFailed && (
        <>
          {renderValidationErrors()}
          
          <div style={{
            backgroundColor: '#FEF2F2',
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
                Template Validation Failed
              </span>
            </div>
            <p style={{
              margin: 0,
              fontSize: '13px',
              color: '#B91C1C'
            }}>
              The template failed validation checks. Please review the errors and make corrections.
            </p>
          </div>

          <button
            onClick={handleCorrectPrompt}
            disabled={isProcessing}
            style={{
              width: '100%',
              backgroundColor: isProcessing ? '#9CA3AF' : '#6B7280',
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
                e.currentTarget.style.backgroundColor = '#4B5563';
              }
            }}
            onMouseOut={(e) => {
              if (!isProcessing) {
                e.currentTarget.style.backgroundColor = '#6B7280';
              }
            }}
          >
            {isProcessing ? 'Sending...' : 'Corregir Prompt'}
          </button>
        </>
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
        SIAC Assistant • Template Validation
      </div>
    </div>
  );
};

export default TemplateValidationCard;