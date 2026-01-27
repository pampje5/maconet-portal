export default function ActionBar({ children }) {
  return (
    <div
      className="
        fixed
        bottom-0
        right-0
        bg-white
        border-t
        border-gray-200
        px-6 py-4
        z-40
      "
      style={{ left: "16rem" }}   // ⬅️ sidebar breedte
    >
      <div className="max-w-7xl mx-auto flex flex-wrap gap-3 justify-between items-center">
        {children}
      </div>
    </div>
  );
}
