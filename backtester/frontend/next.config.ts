import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // P2: Frontend 3001, Backend 8002
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8002/api/:path*',
      },
    ];
  },
};

export default nextConfig;
