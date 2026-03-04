import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // P1: Frontend 3000, Backend 8000
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
