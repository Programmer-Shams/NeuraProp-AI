import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@neuraprop/shared-types"],
};

export default nextConfig;
