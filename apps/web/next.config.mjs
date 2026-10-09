/** Keep verification builds separate from the live development preview. */
const nextConfig = {
  distDir: process.env.VENDORGUARD_BUILD_CHECK === "1" ? ".next-check" : ".next",
};
export default nextConfig;
