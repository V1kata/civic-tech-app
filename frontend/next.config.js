/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow importing from parent directories for backend data
  webpack: (config, { isServer }) => {
    return config;
  },
};

module.exports = nextConfig;
