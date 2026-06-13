export { default } from "next-auth/middleware";

export const config = {
  matcher: ["/dashboard/:path*", "/internships/:path*", "/saved/:path*", "/profile/:path*"],
};
