import { useState, useEffect } from "react";
import api from "../api";
import toast from "react-hot-toast";

export default function SuppliersPage() {
  // ======================
  // STATE
  // ======================
  const [suppliers, setSuppliers] = useState([]);
  const [selectedSupplier, setSelectedSupplier] = useState(null);

  const [newSupplier, setNewSupplier] = useState({
    name: "",
    email_general: "",
    supplier_contact: "",
    supplier_contact_mail: "",
  });

  const [filter, setFilter] = useState("active");
  // "active" | "inactive" | "all"


  // ======================
  // LOAD SUPPLIERS
  // ======================
  async function loadSuppliers() {
    try {
      const res = await api.get("/suppliers");
      setSuppliers(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Kan leveranciers niet laden");
    }
  }

  useEffect(() => {
    loadSuppliers();
  }, []);

  // ======================
  // SELECT SUPPLIER
  // ======================
  function handleSelect(id) {
    if (!id) {
      setSelectedSupplier(null);
      return;
    }

    const sup = suppliers.find((s) => s.id === Number(id));
    setSelectedSupplier({ ...sup });
  }

  // ======================
  // CREATE SUPPLIER
  // ======================
  async function createSupplier() {
    try {
      await api.post("/suppliers", newSupplier);
      toast.success("Leverancier aangemaakt");

      setNewSupplier({
        name: "",
        email_general: "",
        supplier_contact: "",
        supplier_contact_mail: "",
      });

      loadSuppliers();
    } catch (err) {
      console.error(err);
      toast.error("Aanmaken mislukt");
    }
  }

  // ======================
  // SAVE SUPPLIER
  // ======================
  async function saveSupplier() {
    try {
      await api.put(
        `/suppliers/${selectedSupplier.id}`,
        selectedSupplier
      );

      toast.success("Leverancier opgeslagen");
      loadSuppliers();
    } catch (err) {
      console.error(err);
      toast.error("Opslaan mislukt");
    }
  }


  // ======================
  // UI
  // ======================

  const filteredSuppliers = suppliers.filter((s) => {
    if (filter === "active") return s.is_active;
    if (filter === "inactive") return !s.is_active;
    return true;
  });

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <h1 className="text-2xl font-bold mb-6">Leveranciersbeheer</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* ------------------- LINKS: NIEUWE LEVERANCIER ------------------- */}
        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="font-semibold mb-3">Nieuwe leverancier</h2>

          <input
            className="w-full border rounded px-3 py-2 mb-2"
            placeholder="Naam"
            value={newSupplier.name}
            onChange={(e) =>
              setNewSupplier({ ...newSupplier, name: e.target.value })
            }
          />

          <input
            className="w-full border rounded px-3 py-2 mb-2"
            placeholder="Algemeen e-mail"
            value={newSupplier.email_general}
            onChange={(e) =>
              setNewSupplier({
                ...newSupplier,
                email_general: e.target.value,
              })
            }
          />

          <input
            className="w-full border rounded px-3 py-2 mb-2"
            placeholder="Contactpersoon"
            value={newSupplier.supplier_contact}
            onChange={(e) =>
              setNewSupplier({
                ...newSupplier,
                supplier_contact: e.target.value,
              })
            }
          />

          <input
            className="w-full border rounded px-3 py-2 mb-3"
            placeholder="Contact e-mail"
            value={newSupplier.supplier_contact_mail}
            onChange={(e) =>
              setNewSupplier({
                ...newSupplier,
                supplier_contact_mail: e.target.value,
              })
            }
          />

          <button
            onClick={createSupplier}
            className="w-full bg-green-600 text-white rounded py-2"
          >
            Leverancier toevoegen
          </button>
        </div>

        {/* ------------------- MIDDEN: SELECTEER + BEWERK ------------------- */}
        <div className="bg-white p-6 rounded-2xl shadow space-y-4">
          <h2 className="font-semibold">Selecteer leverancier</h2>

          <div className="flex gap-2">
            <button
                className={`px-3 py-1 rounded ${
                filter === "active"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200"
                }`}
                onClick={() => setFilter("active")}
            >
                Actief
            </button>

            <button
                className={`px-3 py-1 rounded ${
                filter === "inactive"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200"
                }`}
                onClick={() => setFilter("inactive")}
            >
                Inactief
            </button>

            <button
                className={`px-3 py-1 rounded ${
                filter === "all"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200"
                }`}
                onClick={() => setFilter("all")}
            >
                Alles
            </button>
            </div>


          <select
            className="w-full border rounded px-3 py-2"
            value={selectedSupplier?.id || ""}
            onChange={(e) => handleSelect(e.target.value)}
          >
            <option value="">-- kies leverancier --</option>
            {filteredSuppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} {!s.is_active && "(inactief)"}
              </option>
            ))}
          </select>

          {selectedSupplier && (
            <>
              <button
                className={`text-white rounded px-4 py-2 ${
                    selectedSupplier.is_active
                    ? "bg-red-600"
                    : "bg-green-600"
                }`}
                onClick={async () => {
                    try {
                    await api.put(
                        `/suppliers/${selectedSupplier.id}`,
                        { ...selectedSupplier, is_active: !selectedSupplier.is_active }
                    );

                    toast.success(
                        selectedSupplier.is_active
                        ? "Leverancier gedeactiveerd"
                        : "Leverancier geactiveerd"
                    );

                    setSelectedSupplier(null);
                    loadSuppliers();
                    } catch (err) {
                    console.error(err);
                    toast.error("Actie mislukt");
                    }
                }}
                >
                {selectedSupplier.is_active
                    ? "Leverancier deactiveren"
                    : "Leverancier activeren"}
                </button>


              <hr />

              <h3 className="font-semibold">Leveranciergegevens</h3>

              <input
                className="w-full border rounded px-3 py-2"
                value={selectedSupplier.name}
                onChange={(e) =>
                  setSelectedSupplier({
                    ...selectedSupplier,
                    name: e.target.value,
                  })
                }
              />

              <input
                className="w-full border rounded px-3 py-2"
                value={selectedSupplier.email_general || ""}
                placeholder="Algemeen e-mail"
                onChange={(e) =>
                  setSelectedSupplier({
                    ...selectedSupplier,
                    email_general: e.target.value,
                  })
                }
              />

              <input
                className="w-full border rounded px-3 py-2"
                value={selectedSupplier.supplier_contact || ""}
                placeholder="Contactpersoon"
                onChange={(e) =>
                  setSelectedSupplier({
                    ...selectedSupplier,
                    supplier_contact: e.target.value,
                  })
                }
              />

              <input
                className="w-full border rounded px-3 py-2"
                value={selectedSupplier.supplier_contact_mail || ""}
                placeholder="Contact e-mail"
                onChange={(e) =>
                  setSelectedSupplier({
                    ...selectedSupplier,
                    supplier_contact_mail: e.target.value,
                  })
                }
              />

              <button
                onClick={saveSupplier}
                className="bg-blue-600 text-white rounded px-4 py-2 mt-2"
              >
                Opslaan
              </button>
            </>
          )}
        </div>

        {/* ------------------- RECHTS: PLACEHOLDER ------------------- */}
        <div />
      </div>
    </div>
  );
}
