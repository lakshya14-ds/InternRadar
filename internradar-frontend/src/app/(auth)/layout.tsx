import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#090514] flex flex-col items-center justify-center p-4">
      <Link href="/" className="flex items-center gap-2 mb-8 group">
        <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center shadow-lg shadow-orange-500/20 group-hover:scale-105 transition-transform duration-200">
          <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
        </div>
        <span className="font-bold text-lg text-white">InternRadar</span>
      </Link>
      {children}
    </div>
  );
}
