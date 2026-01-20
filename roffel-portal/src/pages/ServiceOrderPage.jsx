import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import { formatCurrency, formatQty } from "../utils/format";

export default function ServiceorderPage() {

  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [form, setForm] = useState({
    so: "",
    customer_ref: "",
    po: "",
    status: "",
    supplier: "",
    price_type: "",
    remarks: "",
  });

  // ========================
  // t.b.v. mail nieuwe stijl (met preview)
  // ========================
  const [mailPreview, setMailPreview] = useState(null);
  const [showMailModal, setShowMailModal] = useState(false);
  const [editMode, setEditMode] = useState(false)


  function updateField(name, value) {
    setForm(prev => ({ ...prev, [name]: value }));
  }

  const [soLocked, setSoLocked] = useState(false);

  // ============================
  // CUSTOMERS + CONTACTEN
  // ============================

  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);

  const [contacts, setContacts] = useState([]);
  const [selectedContactId, setSelectedContactId] = useState(null);

  useEffect(() => {
    async function loadCustomers() {
      try {
        const res = await axios.get(`${API}/customers`, {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`,
          },
        });

        setCustomers(res.data);
      } catch (err) {
        console.error(err);
        toast.error("Kon klanten niet laden");
      }
    }

    loadCustomers();
  }, [token]);

  // klant gekozen → prijs_type + contacten ophalen
  useEffect(() => {
    if (!selectedCustomerId) {
      setContacts([]);
      updateField("price_type", "");
      return;
    }

    const cust = customers.find(c => c.id === selectedCustomerId);

    if (cust) {
      // customer name in form.supplier
      updateField("supplier", cust.name);
      // PRIJSTYPE HIER INVULLEN
      updateField("price_type", cust.price_type || "");
    }

    async function loadContacts() {
      try {
        const res = await axios.get(
          `${API}/customers/${selectedCustomerId}/contacts`,
          {
            headers: {
              "x-api-key": "CHANGE_ME",
              Authorization: `Bearer ${token}`,
            }
          }
        );

        setContacts(res.data);

        const primary = res.data.find(c => c.is_primary);

        if (primary) {
          setSelectedContactId(primary.id);
        }

      } catch (err) {
        console.error(err);
      }
    }

    loadContacts();

  }, [selectedCustomerId, customers, token]);


  // ============================
  // OPSLAAN SERVICEORDER
  // ============================

  async function saveOrder() {

    if (!form.so.trim()) {
      alert("Serviceorder nummer is verplicht");
      return;
    }

    try {
      await axios.post(
        `${API}/serviceorders/upsert`,
        form,
        {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`,
          }
        }
      );

      toast.success("Serviceorder opgeslagen");
      setSoLocked(true);

    } catch (err) {
      console.error(err);
      toast.error("Opslaan mislukt");
    }
  }

  // ============================
  // ARTIKELEN
  // ============================

  const [items, setItems] = useState([]);
  const [newPartNo, setNewPartNo] = useState("");

  async function addArticle() {

    if (!newPartNo.trim()) return;

    try {
      const res = await axios.get(
        `${API}/articles/${newPartNo}`,
        {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`
          }
        }
      );

      const a = res.data;

      setItems(prev => [
        ...prev,
        {
          part_no: a.part_no,
          description: a.description,
          qty: 1,

          //prijzen
          list_price: a.list_price,
          price_bruto: a.price_bruto,
          price_wvk: a.price_wvk,
          price_edmac: a.price_edmac,
          price_purchase: a.price_purchase,

          bestellen: false
        }
      ]);

      setNewPartNo("");

    } catch (err) {
      toast.error("Artikel niet gevonden");
    }
  }

  async function saveItems() {

    await axios.post(
      `${API}/serviceorders/${form.so}/items/replace`,
      items,
      {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`
        }
      }
    );

    toast.success("Artikelen opgeslagen");
  }

  // ============================
  // MAIL SULLAIR
  // ============================

  async function openSullairMailPreview() {
  console.log("👉 Aanvraag bij Sullair geklikt");

  if (!form.so) {
    alert("Geen serviceorder nummer");
    return;
  }

  try {
    const res = await axios.post(
      `${API}/mail/sullair/preview`,
      { so: form.so },
      {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    console.log("📧 Mail preview ontvangen:", res.data);

    setMailPreview(res.data);
    setShowMailModal(true);

  } catch (err) {
    console.error("❌ Mail preview fout:", err);
    alert(
      err.response?.data?.detail ||
      "Fout bij ophalen mail preview"
    );
  }
}

async function sendMail() {
  if (!mailPreview) return;

  try {
    await axios.post(
      `${API}/mail/send`,
      {
        to: mailPreview.to,
        subject: mailPreview.subject,
        body_html: mailPreview.body_html,
      },
      {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setShowMailModal(false);
    alert("Mail verzonden ✔");
  } catch (err) {
    console.error(err);
    alert("Verzenden mislukt ❌");
  }
}


  // ============================
  // UI
  // ============================

  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-2xl font-bold mb-6">
        Serviceorder Sullair
      </h1>

      <div className="bg-white rounded-2xl shadow p-6 space-y-8">

        {/* SERVICEORDER BLOK */}
        <div>
          <h2 className="font-semibold mb-2">Serviceorder *</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div>
              <label>Serviceorder nr *</label>
              <input
                className="w-full border rounded px-3 py-2"
                disabled={soLocked}
                value={form.so}
                onChange={e => updateField("so", e.target.value)}
              />
            </div>

            <div>
              <label>Klantreferentie</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.customer_ref}
                onChange={e => updateField("customer_ref", e.target.value)}
              />
            </div>

            <div>
              <label>Inkoopnummer (PO)</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.po}
                onChange={e => updateField("po", e.target.value)}
              />
            </div>

            <div>
              <label>Status</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={form.status}
                onChange={e => updateField("status", e.target.value)}
              >
                <option value="">-- kies status --</option>
                <option>OPEN</option>
                <option>AANGEVRAAGD</option>
                <option>OFFERTE</option>
                <option>BESTELD</option>
                <option>ONTVANGEN</option>
                <option>AFGEHANDELD</option>
              </select>
            </div>

          </div>
        </div>

        {/* KLANT BLOK */}
        <div>
          <h2 className="font-semibold mb-2">Klant</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div>
              <label>Klant</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={selectedCustomerId || ""}
                onChange={e => setSelectedCustomerId(Number(e.target.value))}
              >
                <option value="">-- kies klant --</option>

                {customers.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Contactpersoon</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={selectedContactId || ""}
                onChange={e => setSelectedContactId(Number(e.target.value))}
              >
                <option value="">-- kies contactpersoon --</option>

                {contacts.map(ct => (
                  <option key={ct.id} value={ct.id}>
                    {ct.contact_name} — {ct.email} {ct.is_primary ? "(primair)" : ""}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Prijstype</label>
              <input
                className="w-full border rounded px-3 py-2 bg-gray-100"
                disabled
                value={form.price_type}
              />
            </div>

          </div>
        </div>

        <button
          className="bg-green-600 text-white px-6 py-2 rounded"
          onClick={saveOrder}
        >
          Serviceorder opslaan
        </button>

        {/* ARTIKELEN */}
        {soLocked && (
          <div>
            <h2 className="font-semibold mt-6">Artikelen</h2>

            <div className="flex gap-2 mt-2">
              <input
                className="border rounded px-3 py-2"
                placeholder="Part nr"
                value={newPartNo}
                onChange={e => setNewPartNo(e.target.value)}
              />

              <button
                className="bg-blue-600 text-white px-4 py-2 rounded"
                onClick={addArticle}
              >
                Toevoegen
              </button>
            </div>

            <table className="w-full mt-3 border text-sm">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2">Part nr</th>
                  <th className="border p-2">Omschrijving</th>
                  <th className="border p-2">Aantal</th>
                  <th className="border p-2">Bruto</th>
                  <th className="border p-2">WVK</th>
                  <th className="border p-2">Edmac</th>
                </tr>
              </thead>

              <tbody>
                {items.map((it, i) => (
                  <tr key={i}>
                    <td className="border p-1">{it.part_no}</td>
                    <td className="border p-1">{it.description}</td>

                    <td className="border p-1 text-center">
                      <input
                        type="number"
                        value={formatQty(it.qty)}
                        onChange={e => {
                          const qty = Number(e.target.value);
                          setItems(prev => {
                            const cp = [...prev];
                            cp[i].qty = qty;
                            return cp;
                          });
                        }}
                      />
                    </td>

                    <td className="border p-1 text-right">{formatCurrency(it.price_bruto)}</td>
                    <td className="border p-1 text-right">{formatCurrency(it.price_wvk)}</td>
                    <td className="border p-1 text-right">{formatCurrency(it.price_edmac)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button
              className="bg-green-700 text-white px-5 py-2 mt-2 rounded"
              onClick={saveItems}
            >
              Artikelen opslaan
            </button>

            <button
              className="mt-4 px-6 py-2 bg-blue-700 text-white rounded"
              onClick={openSullairMailPreview}
            >
              Aanvraag bij Sullair
            </button>


            
          </div>
        )}

         {/* ===== MAIL MODAL ===== */}
    {showMailModal && mailPreview && (
      <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
        <div className="bg-white w-3/4 max-w-4xl p-6 rounded shadow">

          <h2 className="text-xl font-bold mb-4">
            Mail aan Sullair (concept)
          </h2>

          <div className="mb-2">
            <b>Aan:</b> {mailPreview.to}
          </div>

          <div className="mb-2">
            <b>Onderwerp:</b>
            <input
              className="w-full border p-2"
              value={mailPreview.subject}
              onChange={(e) =>
                setMailPreview({
                  ...mailPreview,
                  subject: e.target.value,
                })
              }
            />
          </div>

          <div className="mt-2">

             {editMode ? (
              <textarea
                className="w-full h-64 border p-2 font-mono text-sm"
                  value={mailPreview.body_html}
                  onChange={(e) =>
                  setMailPreview({ ...mailPreview, body_html: e.target.value })
              }
              />
            ) : (
              <div className="border rounded p-3 bg-white max-h-64 overflow-auto">
                <div
                  dangerouslySetInnerHTML={{ __html: mailPreview.body_html }}
                />
              </div>
            )}

          </div>



          <div className="flex justify-end gap-3 mt-4">
            <button
              className="px-4 py-2 bg-gray-400 text-white rounded"
              onClick={() => setShowMailModal(false)}
            >
              Annuleren
            </button>

            <button
              className="px-4 py-2 bg-green-600 text-white rounded"
              onClick={sendMail}
            >
              Verzenden
            </button>

            <button
              className="text-sm text-blue-700 underline"
              onClick={() => setEditMode(!editMode)}
            >
              {editMode ? "Voorbeeld tonen" : "Tekst bewerken"}
            </button>

          </div>
        </div>
      </div>
    )}

      </div>
    </div>
  );
}
