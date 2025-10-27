# SIAC Assistant Frontend

This directory contains the React/TypeScript frontend components for the SIAC Assistant, designed to be embedded in ChatGPT Skybridge iframes.

## Project Structure

```
web/
├── src/
│   ├── TemplateValidationCard.tsx      # Template validation component
│   ├── BroadcastConfirmationCard.tsx   # Broadcast confirmation component
│   ├── AuthenticationRequiredCard.tsx  # Authentication required component
│   └── CampaignMetricsWidget.tsx      # Campaign metrics dashboard (fullscreen)
├── dist/
│   ├── template-validation-card.js     # Bundled template component (ESM)
│   ├── broadcast-confirmation-card.js  # Bundled broadcast component (ESM)
│   ├── authentication-required-card.js  # Bundled auth component (ESM)
│   ├── campaign-metrics-widget.js      # Bundled metrics widget (ESM)
│   └── *.js.map                       # Source maps (dev build)
├── package.json                       # Node.js dependencies and scripts
├── tsconfig.json                      # TypeScript configuration
├── test.html                          # Test page for TemplateValidationCard
├── test_all_components.html           # Test page for all components
├── test_metrics_widget.html          # Test page for CampaignMetricsWidget
└── README.md                          # This file
```

## Dependencies

### Production Dependencies
- **react@^18**: React library for component development
- **react-dom@^18**: React DOM rendering

### Development Dependencies
- **typescript@^5.9**: TypeScript compiler and type checking
- **esbuild@^0.25**: Fast JavaScript bundler
- **@types/react@^18**: TypeScript definitions for React
- **@types/react-dom@^18**: TypeScript definitions for React DOM

## Build Scripts

### Production Build
```bash
npm run build
```
- Bundles all four components into separate ES Modules
- Externalizes React and React DOM (assumes they're loaded separately)
- Output: 
  - `dist/template-validation-card.js` (13.2KB)
  - `dist/broadcast-confirmation-card.js` (11.7KB)
  - `dist/authentication-required-card.js` (9.1KB)
  - `dist/campaign-metrics-widget.js` (26.7KB)

### Individual Component Builds
```bash
npm run build:template    # TemplateValidationCard only
npm run build:broadcast   # BroadcastConfirmationCard only
npm run build:auth        # AuthenticationRequiredCard only
npm run build:metrics     # CampaignMetricsWidget only
```

### Development Build
```bash
npm run build:dev
```
- Same as production build but includes source maps for all components
- Output: All `.js` files + corresponding `.js.map` files

### Clean Build
```bash
npm run clean
```
- Removes the `dist/` directory

## Component Usage

The SIAC Assistant includes four React/TypeScript components designed to be embedded in ChatGPT Skybridge iframes:

### 1. TemplateValidationCard
Reads template validation results from the MCP server and orchestrates the conversational flow between error correction and final template registration.

### 2. BroadcastConfirmationCard
Displays confirmation of a scheduled broadcast campaign and provides navigation to detailed metrics dashboard.

### 3. AuthenticationRequiredCard
Activates OAuth 2.1 with PKCE authentication flow when the MCP server fails token verification.

### 4. CampaignMetricsWidget
Comprehensive fullscreen dashboard for campaign metrics visualization, including quality scores, delivery metrics, and Meta compliance information.

### ChatGPT Skybridge API Integration

The component integrates with ChatGPT's Skybridge API through the `window.openai` global object:

```typescript
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
```

### Props Interface
```typescript
interface TemplateValidationCardProps {
  // Optional props for testing/development
  mockData?: {
    toolOutput?: OpenAiGlobal['toolOutput'];
    toolResponseMetadata?: OpenAiGlobal['toolResponseMetadata'];
  };
}
```

### Usage Example
```javascript
import TemplateValidationCard from './dist/template-validation-card.js';

// Use with ChatGPT Skybridge API (automatic)
<TemplateValidationCard />

// Use with mock data for testing
<TemplateValidationCard 
  mockData={{
    toolOutput: {
      validation_status: 'SUCCESS',
      template_name: 'Welcome Message',
      passed_internal_checks: true,
      category: 'Marketing',
      language_code: 'es_ES'
    },
    toolResponseMetadata: {
      raw_payload_for_preview: {
        template_name: 'Welcome Message',
        body_text: 'Welcome to our service!',
        category: 'Marketing',
        language_code: 'es_ES',
        validation_rules_applied: ['Minimum length check'],
        validation_timestamp: '2024-01-20T10:00:00Z',
        estimated_review_time: '24-48 hours'
      },
      template_html_mockup: '<div>...</div>'
    }
  }}
/>
```

### Component Behaviors

#### TemplateValidationCard
**SUCCESS Scenario (validation_status: 'SUCCESS')**
- Displays WhatsApp template preview with header, body, and footer
- Shows validation success message
- Renders "Registrar Plantilla" button (Primary CTA)
- Button calls `siac.register_template` tool via `window.openai.callTool`

**FAILED Scenario (validation_status: 'FAILED')**
- Displays detailed validation errors from `raw_validation_errors`
- Shows error messages with suggestions
- Renders "Corregir Prompt" button (Secondary CTA)
- Button sends correction message via `window.openai.sendFollowUpMessage`

#### BroadcastConfirmationCard
**SCHEDULED Campaign**
- Shows campaign summary with template name, segment, schedule time, and campaign ID
- Displays estimated recipients count
- Renders "Ver Métricas Detalladas" button (Primary CTA)
- Button calls `window.openai.requestDisplayMode('fullscreen')` for metrics dashboard

**SCHEDULED_TEST Campaign**
- Same as scheduled but with test-specific messaging
- Indicates this is a limited test segment

#### AuthenticationRequiredCard
**Authentication Required**
- Shows clear message about restricted access
- Lists available features after authentication
- Displays security information about OAuth 2.1 with PKCE
- Renders "Conectar Cuenta SIAC" button (Primary CTA)
- Button sends follow-up message to trigger ChatGPT OAuth flow

#### CampaignMetricsWidget
**Fullscreen Dashboard**
- Displays comprehensive campaign metrics in fullscreen mode
- Shows quality scores (GREEN/YELLOW/RED) with appropriate warnings
- Includes delivery metrics, engagement rates, and cost analysis
- Handles Template Pacing status and Meta error 131049
- Implements time filters (7d, 30d, 90d, all) and metric selection
- Persists user preferences using `window.openai.setWidgetState`
- Compatible with ChatGPT composer overlay in fullscreen mode

## Testing

### Manual Testing
Open test pages in a web browser to see all components in action:

**Individual Component Testing:**
- `test.html` - TemplateValidationCard scenarios (SUCCESS/FAILED)

**All Components Testing:**
- `test_all_components.html` - All four components with different scenarios

**Campaign Metrics Testing:**
- `test_metrics_widget.html` - CampaignMetricsWidget with various quality scores and error scenarios

### Automated Testing
Run the comprehensive test suite:
```bash
python test_component.py
```

This will verify:
- Component structure and ChatGPT API integration
- Build process and output
- Package and TypeScript configuration
- UI design guidelines compliance
- SUCCESS and FAILED scenario logic
- Tool call and follow-up message functionality

## Integration with ChatGPT Skybridge

The bundled component is designed to be loaded as an ES Module in ChatGPT Skybridge iframes:

1. The component is bundled as a single ES Module (`dist/template-validation-card.js`)
2. React and React DOM are externalized and should be loaded separately
3. The component can be invoked from the backend MCP tools via the `openai/widgetAccessible` meta property

## Development Workflow

1. **Make changes** to `src/TemplateValidationCard.tsx`
2. **Build the component**: `npm run build`
3. **Test locally**: Open `test.html` in browser
4. **Deploy**: The `dist/template-validation-card.js` file can be served statically

## TypeScript Configuration

The project uses a modern TypeScript configuration:
- Target: ES2020
- Module: ESNext
- JSX: react-jsx
- Strict mode enabled
- Includes DOM types for browser APIs

## ESBuild Configuration

The build process uses ESBuild for fast bundling:
- Format: ESM (ES Module)
- External dependencies: React and React DOM
- Single output file for easy embedding
- Source maps available in development builds
