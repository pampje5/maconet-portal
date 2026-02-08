import Button from "./ui/Button";

export default function ConfirmSaveModal({ open, onConfirm, onCancel }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-3 text-red-600">
          Serviceorder bevestigen
        </h2>

        <p className="mb-4 text-gray-700">
          Let op: na het opslaan en bevestigen kunnen de gegevens van deze
          serviceorder <b>niet meer worden gewijzigd</b>.
        </p>

        <p className="mb-6 text-gray-700">
          Alleen het <b>PO-nummer</b> kan later nog worden toegevoegd of aangepast.
        </p>

        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel}>
            Annuleren
          </Button>

          <Button variant="danger" onClick={onConfirm}>
            Opslaan & bevestigen
          </Button>
        </div>
      </div>
    </div>
  );
}
