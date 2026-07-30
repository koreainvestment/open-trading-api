# KOSIS Stats Frontend (React)

A React-based Single Page Application (SPA) for viewing financial reports from the KOSIS Stats backend.
Migrated from vanilla TypeScript to React + Vite.

## Features

- **Dashboard**: View reports for a specific company.
- **Reports List**: Browse all reports with client-side filtering and sorting.
- **Expandable Rows**: View report details inline in the list view.
- **Raw Report Viewer**: View HTML, XML, or Text content of raw reports.

## Development

### Prerequisites

- Node.js 18+ and npm

### Setup

1. Install dependencies:

```bash
npm install
```

2. Start Development Server (with HMR):

```bash
npm run dev
```

Then open `http://localhost:5173` in your browser.

## Production Build

1. Build the project:

```bash
npm run build
```

The output will be in the `dist/` directory.

2. Serve the build locally:

```bash
./serve.sh
# or
npm run preview
```

## API Configuration

The API URL is configured in `src/api.ts`. Default is `http://localhost:8080`.