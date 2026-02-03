import Header from "./Header";
import BottomNav from "./BottomNav";

export default function AppShell({ title, children }) {
  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <Header title={title} />

      <main className="flex-1 overflow-y-auto p-4">
        {children}
      </main>

      <BottomNav />
    </div>
  );
}
