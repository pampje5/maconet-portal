export default function ConfirmLeaveModal({
  open,
  onSave,
  onCancel,
  onClose,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-2">
          Serviceorder nog niet opgeslagen
        </h2>

        <p className="text-sm text-gray-600 mb-6">
          Deze serviceorder heeft al een nummer, maar is nog niet opgeslagen.
          Wat wil je doen?
        </p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-red-500 text-red-600 rounded hover:bg-red-50"
          >
            Annuleren
          </button>

          <button
            onClick={onSave}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Opslaan
          </button>
        </div>
      </div>
    </div>
  );
}
