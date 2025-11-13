# 4-Plex Unified Dashboard

React-based frontend for the 4-Plex Unified Investment Platform.

## Features

- **Dashboard**: Overview of system status, metrics, and quick actions
- **Properties**: Browse and filter discovered 4-plex properties
- **Opportunities**: View top-rated investment opportunities with detailed metrics
- **Analytics**: Comprehensive analytics with charts and performance metrics

## Tech Stack

- React 18
- Material-UI (MUI) 5
- Recharts for data visualization
- Vite for fast builds
- React Router for navigation
- Axios for API communication

## Development

```bash
# Install dependencies
npm install

# Start development server (with proxy to backend)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Build Output

The production build creates static files in the `dist/` directory that can be served by the backend FastAPI application or any static file server.

## API Integration

The frontend communicates with the backend API at `http://localhost:11070`. The Vite dev server includes a proxy configuration to forward API requests during development.

## Components

- **App.jsx**: Main application with routing and navigation
- **Dashboard.jsx**: Main dashboard with system metrics
- **Properties.jsx**: Property listing with filters
- **Opportunities.jsx**: Investment opportunities with scoring
- **Analytics.jsx**: Charts and analytics visualization
- **api.js**: API service layer for backend communication
